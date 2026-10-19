"""Read-only live inference check using the failed run's retained inputs.

Does not execute generated tests, apply a patch, or change the banking demo.
Run from the project root with: venv/Scripts/python.exe -m reports.intent-timeout-verification-2026-10-15.verify_intent
"""
import json
import time
from pathlib import Path

from apishield.commands import redact_data
from apishield.intent import infer_intent
from apishield.model_access import environment_connection


def main():
    source = Path.home() / '.apishield/jobs/b08960f0bb3b4d10b08e0109543a4109'
    report = json.loads((source / 'result.json').read_text())
    config = json.loads((source / 'config.json').read_text())
    root = source / 'source-tree'
    allowed = {site['file'] for site in report['impacted_sites']}
    context = {
        'snapshot_root': str(root), 'model': config.get('model', 'gemini-3.8-flash'),
        'request_timeout_seconds': 120, 'intent_timeout_seconds': 240,
        'sources': {name: (root / name).read_text(encoding='utf-8') for name in sorted(allowed)},
        'base_spec': json.loads((source / 'contracts/base.json').read_text()),
        'target_spec': json.loads((source / 'contracts/target.json').read_text()),
        'semantic_graph': report['semantic_graph'],
        'existing_tests': {p.relative_to(root).as_posix(): p.read_text(encoding='utf-8')[:8000]
                           for p in list(root.glob('tests/**/test_*.py'))[:8]},
    }
    started = time.monotonic()
    events = []
    def activity(message):
        events.append({'elapsed_s': round(time.monotonic() - started, 2), 'message': message})
        print(message, flush=True)
    try:
        value = infer_intent(context, environment_connection(), on_activity=activity)
        result = {'status': 'inference_validated', 'intent': value}
    except Exception as error:
        result = {'status': 'failed', 'error': f'{type(error).__name__}: {error}'}
    result.update(elapsed_s=round(time.monotonic() - started, 2), events=events,
                  source_job=source.name, scope='Live intent inference only; no tests executed or patch applied')
    output = Path(__file__).with_name('result.json')
    output.write_text(json.dumps(redact_data(result), indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'intent'}), flush=True)


if __name__ == '__main__':
    main()
