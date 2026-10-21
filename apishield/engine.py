"""Shared isolated local scan/compare/repair transaction for every adapter."""
from contextlib import contextmanager
import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time

from .analysis import scan_sources
from .commands import redact_data, run_command
from .comparison import compare_contracts, impacted_sites
from .configuration import IntegrationConfig
from .editing import apply_candidate
from .generation import generate_candidate, GenerationServiceError
from .jobs import Job, JobCancelled, JobStore, JobTimedOut, atomic_json
from .workspace import prepare_workspace
from .requirements import build_requirement_graph, requirement_outcomes, requirements_hash, read_check_result


@contextmanager
def _execution_lock(path):
    """Nonblocking OS ownership across worker threads and processes."""
    with (path / 'execution.lock').open('a+b') as stream:
        if stream.seek(0, os.SEEK_END) == 0:
            stream.write(b'\0'); stream.flush()
        owned = False
        try:
            stream.seek(0)
            try:
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                owned = True
            except OSError as exc:
                if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                    raise
            yield owned
        finally:
            if owned:
                stream.seek(0)
                if os.name == 'nt':
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def recover_interrupted(store: JobStore, job_id: str) -> dict:
    """Read persisted evidence, detecting workers that lost their OS ownership.

    The engine never resumes a partial repair. Adapters may use this for report
    reads after process loss; untouched queued jobs remain eligible to run.
    """
    path = store._path(job_id)
    result = store.get(job_id)
    if result.get('status') not in {'queued', 'running'} or not (path / 'worker-owner.json').exists():
        return result
    with _execution_lock(path) as owned:
        result = store.get(job_id)
        if owned and result.get('status') in {'queued', 'running'} and (path / 'worker-owner.json').is_file():
            result = {**result, 'status': 'failed', 'error': 'Job interrupted by worker process loss; start a new job to retry'}
            result.pop('patch', None)
            atomic_json(path / 'result.json', result)
            (path / 'candidate.patch').unlink(missing_ok=True)
            workspace = path / 'workspace'
            if workspace.is_symlink():
                workspace.unlink()
            elif workspace.exists():
                if workspace.resolve().parent != path.resolve():
                    raise ValueError('Unsafe interrupted workspace cleanup path')
                shutil.rmtree(workspace)
        return result


def _hash_files(root, *, include_caches=False, protected_cache_files=()):
    """Independent byte/mode inventory; only known test/Python caches excluded."""
    hashes = {}
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f'Repository command created a symlink: {relative.as_posix()}')
        if not include_caches and relative.as_posix() not in protected_cache_files and any(part in {'__pycache__', '.pytest_cache'} for part in relative.parts):
            continue
        if path.is_file():
            hashes[relative.as_posix()] = (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode & 0o777)
    return hashes


def _unchanged(job, baseline):
    current = _hash_files(job.workspace, protected_cache_files=baseline)
    changed = [name for name, value in baseline.items() if current.get(name) != value]
    # New test hooks/config/source can weaken validation just as edits can.
    # Explicit setup is permitted to use external environments and known
    # caches, but must not add repository files to the committed baseline.
    changed.extend(name for name in current if name not in baseline)
    contracts_changed = job._restore_contracts()
    if changed or contracts_changed:
        detail = ', '.join(sorted(set(changed))) or 'contract snapshots'
        raise ValueError(f'Repository commands modified protected source/tests/config/contracts or the candidate: {detail}')


def _repository_command(argv, job, label):
    arguments = list(argv)
    if arguments[0].lower() in {'python', 'python3'}:
        arguments[0] = sys.executable
    result = run_command(arguments, job, label)
    return result


def _check_command(job, result, label):
    if result['cancelled']:
        raise JobCancelled('job cancellation requested during command')
    if result['timed_out']:
        raise JobTimedOut(f'{label} exceeded its execution deadline')
    job.check()


def _execute(job, operation, candidate_path, result):
    job.event('activity', stage='prepare', message='Capturing source and API contracts in a temporary workspace')
    result.update(prepare_workspace(job))
    if job._initial.get('browser_ai'):
        from dataclasses import replace
        from .intent import discover_test_commands
        try:
            commands = job.config.test_commands or discover_test_commands(job.workspace)
        except ValueError:
            commands = []
        job.config = replace(job.config, test_commands=commands, requirements=[])
    atomic_json(job.path / 'result.json', redact_data({**job._initial, **result}))
    job.check()
    job.event('activity', stage='analyze', message='Scanning API consumers and building the structural graph')
    base_paths = json.loads(job._contract_bytes['base.json']).get('paths', {})
    result['scan'] = scan_sources(job.workspace, job.config.code_paths, job.config.http_bindings,
        qualify_operations=any(path.startswith('/__provider__/') for path in base_paths))
    result['requirements'] = job.config.requirements
    result['requirements_hash'] = requirements_hash(job.config.requirements)
    result['requirement_graph'] = build_requirement_graph(result['scan'], job.config.requirements, result)
    from .repository_graph import build_repository_graph
    result['semantic_graph'] = build_repository_graph(job.workspace, result['scan'], job.config.requirements, [], job.check)
    atomic_json(job.path / 'result.json', redact_data({**job._initial, **result}))
    job.check()
    job.event('scan_finished', sites=len(result['scan']['sites']), limitations=result['scan']['limitations'])
    if operation == 'scan':
        return {**result, 'status': 'completed'}
    job.event('activity', stage='analyze', message='Comparing API contracts and locating affected functions')
    result['comparison'] = compare_contracts(job)
    result['impacted_sites'] = impacted_sites(result['scan'], result['comparison'])
    result['semantic_graph'] = build_repository_graph(job.workspace, result['scan'], job.config.requirements, result['comparison']['changed_operations'], job.check)
    result['requirement_outcomes'] = requirement_outcomes(job.config.requirements, result['scan'], result['impacted_sites'], job.workspace)
    atomic_json(job.path / 'result.json', redact_data({**job._initial, **result}))
    job.check()
    job.event('comparison_finished', changed_operations=result['comparison']['changed_operations'])
    if operation == 'compare':
        return {**result, 'status': 'completed'}
    result['proposal_source']='offline' if candidate_path is not None else 'model'
    if not result['comparison']['changed_operations']:
        return {**result, 'status': 'no_change'}
    if not result['impacted_sites']:
        return {**result, 'status': 'needs_input', 'error': 'No changed operation could be localized to supported source calls; review coverage limitations'}
    if not job.config.test_commands and not job._initial.get('browser_ai'):
        return {**result, 'status': 'needs_input', 'error': 'Configure independent test commands before a repair can be validated'}
    blocked = [o for o in result['requirement_outcomes'] if o['status'] == 'needs_input']
    if blocked:
        return {**result, 'status':'needs_input', 'error':'; '.join(o['id'] + ': ' + o['reason'] for o in blocked)}
    offline = None
    if candidate_path is not None:
        offline = json.loads(Path(candidate_path).read_text(encoding='utf-8'))
        if not isinstance(offline, dict):
            raise ValueError('Offline candidate JSON must be an object')
    allowed = {site['file'] for site in result['impacted_sites']}
    generated = []
    if job._initial.get('browser_ai'):
        from .intent import infer_intent
        job.event('activity', stage='intent', message='Gemini is inferring behavior and generating regression checks')
        context = {'snapshot_root': str(job.workspace), 'model': job.config.model,
                   'http_bindings': job.config.http_bindings,
                   'request_timeout_seconds': min(job.config.budgets.command_timeout_seconds, job.remaining()),
                   'intent_timeout_seconds': min(2 * job.config.budgets.command_timeout_seconds, job.remaining()),
                   'sources': {name: (job.workspace / name).read_text(encoding='utf-8') for name in sorted(allowed)},
                   'base_spec': json.loads((job.path / 'contracts/base.json').read_text()),
                   'target_spec': json.loads((job.path / 'contracts/target.json').read_text()),
                   'semantic_graph': result['semantic_graph'],
                   'existing_tests': {p.relative_to(job.workspace).as_posix(): p.read_text(encoding='utf-8')[:8000]
                                      for p in list(job.workspace.glob('tests/**/test_*.py'))[:8]}}
        result['ai_intent'] = infer_intent(context, job._model_connection, check=job.check,
                                         on_activity=lambda message: job.event('activity', stage='intent', message=message))
        generated = result['ai_intent']['checks']
    result['attempts'] = []
    feedback = None
    # An explicit deterministic fixture is evaluated once and never falls back
    # to inference; live generation can repair feedback within the budget.
    attempts = 1 if candidate_path is not None else job.config.budgets.max_attempts
    for number in range(1, attempts + 1):
        job.check()
        prepare_workspace(job)
        for item in generated:
            destination = job.workspace / item['file']
            if destination.exists():
                raise ValueError('Generated checks cannot replace current tests')
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(item['code'], encoding='utf-8')
        protected = _hash_files(job.workspace, include_caches=True)
        attempt = {'number': number, 'setup': [], 'validation': [], 'requirements':[]}
        result['requirement_outcomes'] = requirement_outcomes(job.config.requirements, result['scan'], result['impacted_sites'], job.workspace)
        result['attempts'].append(attempt)
        try:
            for index, command in enumerate(job.config.setup_commands, 1):
                evidence = _repository_command(command, job, f'setup_{index}')
                attempt['setup'].append(evidence)
                _unchanged(job, protected)
                _check_command(job, evidence, f'setup_{index}')
                if evidence['exit_code'] != 0:
                    raise ValueError('Configured setup command failed')
            if generated and 'generated_baseline' not in result:
                job.event('activity', stage='intent', message='Checking that generated tests expose the original incompatibility', attempt=number)
                import xml.etree.ElementTree as ET
                baseline_xml = job.path / 'generated_baseline.xml'
                baseline = _repository_command(['python', '-m', 'pytest', '-q', '--junitxml', str(baseline_xml),
                                                '--', 'tests/apishield_generated'], job, 'generated_baseline')
                _unchanged(job, protected)
                _check_command(job, baseline, 'generated_baseline')
                checked = read_check_result(baseline_xml, baseline['exit_code'])
                if checked['tests'] == 0 or baseline['exit_code'] != 1:
                    raise ValueError('Generated checks must fail on the incompatible original code; no sensitive checks established')
                root = ET.fromstring(baseline_xml.read_bytes())
                if list(root.iter('error')) or not list(root.iter('failure')):
                    raise ValueError('Generated baseline must contain assertion failures, not collection/runtime errors')
                result['generated_baseline'] = baseline
            # Resolve the entire selector, not only its file, before inference.
            # Collection imports trusted repository tests under the same limits.
            for index, outcome in enumerate(result['requirement_outcomes'], 1):
                if outcome['status'] != 'pending':
                    continue
                outcome['collection'] = []
                for check_index, reference in enumerate(outcome['checks'], 1):
                    label = f'collect_requirement_{number}_{index}_{check_index}'
                    evidence = _repository_command(['python', '-m', 'pytest', '--collect-only', '-q',
                                                    '--rootdir', str(job.workspace), '--', reference], job, label)
                    outcome['collection'].append({'reference':reference, 'command':evidence})
                    _unchanged(job, protected)
                    _check_command(job, evidence, label)
                    collected = any(line == reference or line.startswith(reference + '[')
                                    for line in evidence['stdout'].splitlines())
                    if evidence['exit_code'] != 0 or evidence['output_limited'] or not collected:
                        outcome.update(status='needs_input', reason=f'Cannot collect selected test {reference} from the pinned revision. Review its function/class name and test environment.')
                        attempt['status'] = 'needs_input'
                        return {**result, 'status':'needs_input', 'error':outcome['id'] + ': ' + outcome['reason']}
            context = {'model': job.config.model,
                'http_bindings': job.config.http_bindings,
                'request_timeout_seconds': min(job.config.budgets.command_timeout_seconds, job.remaining(), 60),
                'allowed_files': sorted(allowed),
                'sources': {name: (job.workspace / name).read_bytes().decode('utf-8') for name in sorted(allowed)},
                'base_spec': json.loads((job.path / 'contracts/base.json').read_text(encoding='utf-8')),
                'target_spec': json.loads((job.path / 'contracts/target.json').read_text(encoding='utf-8')),
                'comparison': result['comparison']['diff'],
                'impacted_sites': [{k: v for k, v in site.items() if job.config.use_intent or k != 'intent'} for site in result['impacted_sites']]}
            if job.config.use_intent:
                context['confirmed_requirements'] = [o for o in result['requirement_outcomes'] if o['status'] == 'pending']
            if generated:
                context['ai_inferred_intent'] = result['ai_intent']['rules']
                context['semantic_graph'] = result['semantic_graph']
            job.check()
            model_arguments = {} if job._model_connection is None else dict(connection=job._model_connection,
                check=job.check, on_usage=lambda **data:job.event('model_usage',**data))
            if candidate_path is None and job._initial.get('browser_ai') and job._initial.get('project_workflow'):
                from demo.repair_guidance import reference_patches
                reference = reference_patches(context, job._initial['project_workflow'])
                if reference:
                    model_arguments['demo_reference_patches'] = reference
                    result['generation_guidance'] = {'kind':'prewritten_demo_reference',
                        'files':sorted({p['file'] for p in reference}), 'unseeded_evaluation':False}
                    job.event('demo_reference_guidance', files=result['generation_guidance']['files'])
            job.event('activity', stage='repair', attempt=number,
                      message='Generating a targeted patch' if number == 1 else 'Retrying the patch with validation feedback')
            candidate = offline if candidate_path is not None else generate_candidate(context, feedback, **model_arguments)
            job.check()
            if not isinstance(candidate, dict):
                raise ValueError('Generator must return a candidate object')
            if candidate.get('needs_input'):
                if not isinstance(candidate['needs_input'], str):
                    raise ValueError('needs_input must be a diagnostic string')
                attempt['status'] = 'needs_input'
                return {**result, 'status': 'needs_input', 'error': candidate['needs_input']}
            job.event('activity', stage='repair', attempt=number, message='Checking and applying the candidate only in the temporary workspace')
            applied = apply_candidate(job.workspace, candidate, allowed)
            attempt['files'] = applied['files']
            candidate_hashes = _hash_files(job.workspace, protected_cache_files=protected)
            job.event('activity', stage='validate', attempt=number, message='Running repository tests and behavioral checks against the candidate')
            for index, command in enumerate(job.config.test_commands, 1):
                evidence = _repository_command(command, job, f'test_{index}')
                attempt['validation'].append(evidence)
                _unchanged(job, candidate_hashes)
                _check_command(job, evidence, f'test_{index}')
            if generated:
                xml = job.path / 'generated_validation.xml'
                evidence = _repository_command(['python', '-m', 'pytest', '-q', '-o', 'xfail_strict=true',
                                                '--junitxml', str(xml), '--', 'tests/apishield_generated'], job, 'generated_validation')
                attempt['validation'].append(evidence)
                _unchanged(job, candidate_hashes)
                _check_command(job, evidence, 'generated_validation')
                result['generated_validation'] = read_check_result(xml, evidence['exit_code'])
                if not result['generated_validation']['passed']:
                    failures = result['generated_validation'].get('failures', [])
                    diagnostic = (failures[0]['test'] + ': ' + failures[0]['message']) if failures else result['generated_validation']['reason']
                    raise ValueError('Generated validation failed: ' + diagnostic)
            for index, outcome in enumerate(result['requirement_outcomes'], 1):
                if outcome['status'] != 'pending':
                    continue
                attempt['requirements'].append(outcome)
                for check_index, reference in enumerate(outcome['checks'], 1):
                    label = f'requirement_{number}_{index}_{check_index}'
                    xml = job.path / (label + '.xml')
                    xml.unlink(missing_ok=True)
                    evidence = _repository_command(['python', '-m', 'pytest', '-q', '-o', 'xfail_strict=true',
                                                    '--junitxml', str(xml), '--', reference], job, label)
                    outcome['evidence'].append({'reference':reference, 'command':evidence})
                    _unchanged(job, candidate_hashes)
                    _check_command(job, evidence, label)
                    checked = read_check_result(xml, evidence['exit_code'])
                    outcome['evidence'][-1]['result'] = checked
                    if not checked['passed']:
                        outcome.update(status='failed', reason=checked['reason'])
                if outcome['status'] == 'pending':
                    outcome['status'] = 'passed'
            job.check()
            if all(item['exit_code'] == 0 for item in attempt['validation']) and all(o['status'] == 'passed' for o in attempt['requirements']):
                attempt['status'] = 'validated'
                job.check()
                # Write only independently checked in-memory bytes, never a
                # patch prepared by a repository subprocess.
                from .jobs import _atomic_bytes
                _atomic_bytes(job.path / 'candidate.patch', applied['patch'].encode('utf-8'))
                retained = {}
                for name in [*applied['files'], *(item['file'] for item in generated)]:
                    content = (job.workspace / name).read_bytes()
                    target = job.path / 'applied-files' / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    _atomic_bytes(target, content)
                    retained[name] = hashlib.sha256(content).hexdigest()
                job.event('activity', stage='review', status='waiting', attempt=number,
                          message='Validation passed. Review the patch, then Apply repair to update working files')
                return {**result, 'status': 'validated', 'patch': 'candidate.patch',
                        'applied_files': retained,
                        'patch_sha256':hashlib.sha256(applied['patch'].encode('utf-8')).hexdigest()}
            attempt['status'] = 'failed'
            failed_rules = [o['id'] for o in attempt['requirements'] if o['status'] != 'passed']
            attempt['error'] = ('Requirement checks failed: ' + ', '.join(failed_rules)) if failed_rules else 'Configured tests failed; candidate was not validated'
        except (JobCancelled, JobTimedOut) as exc:
            for outcome in result['requirement_outcomes']:
                if outcome['status'] == 'pending':
                    outcome.update(status='failed', reason=str(exc))
            raise
        except (OSError, ValueError, SyntaxError) as exc:
            attempt['status'] = 'failed'; attempt['error'] = str(exc)
            for outcome in result['requirement_outcomes']:
                if outcome['status'] == 'pending':
                    outcome.update(status='failed', reason=str(exc))
            if isinstance(exc, GenerationServiceError) and number < attempts:
                time.sleep(min(1, job.remaining()))
        feedback = {'attempt': number, 'error': attempt.get('error'), 'validation': attempt['validation'], 'requirements':attempt['requirements']}
        job.event('attempt_finished', **attempt)
    return {**result, 'status': 'failed', 'error': result['attempts'][-1].get('error', 'Repair attempts exhausted')}


def run_job(config: IntegrationConfig, operation: str, store: JobStore,
            candidate_path: Path | None = None, job: Job | None = None, model_connection=None) -> dict:
    if operation not in {'scan', 'compare', 'repair'}:
        raise ValueError('Invalid job operation')
    if job is None:
        job = store.create(config, operation)
    if model_connection is not None:
        job._model_connection = model_connection
        job._initial['model_connection'] = {**model_connection.metadata(),'model':config.model}
    if job.config != config or job.operation != operation or job.path.resolve() != store._path(job.id).resolve():
        raise ValueError('Supplied job does not match configuration, operation or store')
    with _execution_lock(job.path) as owned:
        if not owned:
            return store.get(job.id)
        persisted = store.get(job.id)
        if persisted['status'] not in {'queued', 'running'}:
            return persisted
        if persisted['status'] in {'queued', 'running'} and (job.path / 'worker-owner.json').exists():
            final = job.finish({**persisted, 'status': 'failed', 'error': 'Job interrupted by worker process loss; start a new job to retry'})
            job.cleanup()
            (job.path / 'candidate.patch').unlink(missing_ok=True)
            return final
        result = {'status': 'running'}
        final = None
        try:
            atomic_json(job.path / 'worker-owner.json', {'pid': os.getpid(), 'job_id': job.id})
            atomic_json(job.path / 'result.json', {**job._initial, 'status': 'running'})
            job.event('job_started', operation=operation)
            result = _execute(job, operation, candidate_path, result)
            job.check()
        except JobCancelled as exc:
            result.update(status='cancelled', error=str(exc))
        except JobTimedOut as exc:
            result.update(status='failed', error=str(exc), timed_out=True)
        except KeyboardInterrupt:
            store.cancel(job.id)
            result.update(status='cancelled', error='Interrupted by controller')
        except Exception as exc:
            result.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        finally:
            try:
                if result.get('status') != 'validated':
                    result.pop('patch', None)
                final = job.finish(result)
                job.event('job_finished', status=final['status'])
            finally:
                job.cleanup()
                if final is None or final.get('status') != 'validated':
                    (job.path / 'candidate.patch').unlink(missing_ok=True)
        return final
