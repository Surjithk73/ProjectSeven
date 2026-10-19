"""Bounded, redacted activity snapshots for a retained execution."""
import json
import re
from .commands import redact_data


def failure_explanation(report):
    if report.get('status') not in {'failed', 'needs_input'}:
        return None
    commands = [command for attempt in report.get('attempts', []) for command in attempt.get('validation', [])
                if command.get('exit_code') != 0 or command.get('timed_out') or command.get('cancelled')]
    command = commands[-1] if commands else {}
    output = (command.get('stdout', '') + '\n' + command.get('stderr', '')).replace('\\', '/')
    tests = re.findall(r'^FAILED\s+(\S+)', output, re.M)
    exceptions = re.findall(r'^\s*E\s+([A-Za-z_]\w*(?:Error|Exception)(?::[^\r\n]*)?)', output, re.M)
    locations = re.findall(r'^([^\r\n]*?\.py:\d+):', output, re.M)
    detail = exceptions[-1] if exceptions else report.get('error', 'Execution did not complete successfully')
    test = tests[-1] if tests else ''
    location = locations[-1] if locations else ''
    generated_error = ((detail.startswith(('NameError', 'UnboundLocalError')) and
                        'tests/apishield_generated/' in (location or test)) or
                       'Generated check references undefined name' in report.get('error', ''))
    provider_error = report.get('error', '')
    provider_timeout = (('DEADLINE_EXCEEDED' in provider_error and '504' in provider_error) or
                        ('Google' in provider_error and ('timed out' in provider_error or 'deadline' in provider_error.lower())) or
                        ('IntentServiceError' in provider_error and 'timed out' in provider_error))
    if provider_timeout or 'IntentServiceError' in provider_error:
        category = 'provider_timeout' if provider_timeout else 'provider_unavailable'
        title = 'Google did not complete the AI request'
        summary = 'Google could not complete the AI request. This is a provider request failure, not a failed validation test.'
        detail = 'The AI service exceeded its deadline.' if provider_timeout else 'The AI service remained unavailable after bounded recovery.'
        next_action = 'Start a new AI update. Temporary provider errors now get one automatic retry within the job deadline; persistent failures still stop safely.'
    elif generated_error:
        category, title = 'generated_check_error', 'An AI-generated check could not run'
        summary = 'A generated test referenced an undefined name. This is a check-generation defect, not evidence that the migration behavior is wrong.'
        next_action = 'Request a new AI update. Generated checks are now checked for undefined names and regenerated before candidate validation.'
    elif commands:
        category, title = 'validation_failure', 'The candidate did not pass validation'
        summary = 'At least one test failed or could not finish. The proposal was not accepted.'
        next_action = 'Review the failing assertion and command output below. A new AI update can use this evidence to produce another proposal.'
    else:
        category, title = 'execution_failure', 'The run could not finish'
        summary = report.get('error', 'The worker stopped before validation completed.')
        next_action = 'Review the reported error and execution log before starting another run.'
    return redact_data(dict(category=category, title=title, summary=summary, detail=detail[:1200],
                            test=test, location=location, next_action=next_action,
                            consequence='Working files were not applied by this failed run.'))


def read_activity(store, job_id):
    path = store._path(job_id)
    report = store.get(job_id)
    source = path / 'events.jsonl'
    events, truncated = [], False
    if source.is_symlink():
        raise ValueError('Unsafe activity record')
    if source.is_file():
        with source.open('rb') as stream:
            size = stream.seek(0, 2)
            start = max(0, size - 512 * 1024)
            stream.seek(start)
            raw = stream.read(512 * 1024)
        truncated = start > 0
        if start:
            raw = raw.partition(b'\n')[2]
        # The last line may still be in flight while the worker appends it.
        for line in raw.splitlines(keepends=True):
            if not line.endswith(b'\n'):
                continue
            try:
                event = json.loads(line)
                if isinstance(event, dict):
                    events.append(event)
            except (ValueError, UnicodeError):
                continue
    truncated = truncated or len(events) > 200
    return redact_data({'job_id': job_id, 'status': report['status'],
                        'created_at': report.get('created_at'), 'finished_at': report.get('finished_at'),
                        'error': report.get('error'), 'application': report.get('application'),
                        'failure_explanation': failure_explanation(report),
                        'events': events[-200:], 'truncated': truncated})
