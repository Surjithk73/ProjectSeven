"""Archive a phone rehearsal and start the next one from a verified V1 revision."""
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import uuid

from apishield.engine import _execution_lock
from apishield.github_cli import GhClient
from apishield.jobs import atomic_json
from .setup import DEMO_ROOT, workspace_path

# Human-merged PR #5: V1 clients and a contract-complete public hold fixture.
BASELINE_SHA = '5c2ce0bc39136d5038c77a35faf1d16f9c0d1254'
SUPPORTED_BASELINES = {BASELINE_SHA, '0439f7c451dcc1032ed309071b0536ad2b12000b',
                      '77dfc946dd1a40f0fc8af8ef820bdd7009c7cdf0'}


def control_directory(root):
    path = workspace_path(root.parent / (root.name + '-control'))
    path.mkdir(parents=True, exist_ok=True)
    return path


def rehearsal_settings(root):
    path = root / 'rehearsal.json'
    if not path.exists():
        return None
    import re
    value = json.loads(path.read_text(encoding='utf-8'))
    if (value.get('version') != 1 or value.get('baseline_sha') not in SUPPORTED_BASELINES
            or not re.fullmatch(r'demo/rehearsal-[0-9TZ-]+-[0-9a-f]{8}', value.get('base', ''))):
        raise ValueError('Invalid rehearsal settings; preserve and inspect rehearsal.json')
    return value


def reset_phone_demo(root=None, github=None, stop_timeout=30):
    from .phone import REPOSITORY, PUBLISHER, prepare_source, git
    from .providers.state import Store
    raw = Path(root or DEMO_ROOT / 'phone')
    if raw.is_symlink() or (hasattr(raw, 'is_junction') and raw.is_junction()):
        raise ValueError('Reset requires a managed phone directory, not a link')
    root = workspace_path(raw)
    if not (root / '.phone-demo').is_file():
        raise ValueError('Reset requires an existing managed phone demo')
    github = github or GhClient()
    deadline = time.monotonic() + 45
    if github.api('GET', 'user', None, deadline=deadline)['login'].casefold() != PUBLISHER.casefold():
        raise ValueError('Keep GitHub CLI signed in as Surjithk73 for the demo reset')
    checks = github.api('GET', f'repos/{REPOSITORY}/commits/{BASELINE_SHA}/check-runs?per_page=100',
        None, deadline=deadline).get('check_runs', [])
    if not any(c.get('name') == 'cinema-client' and c.get('head_sha') == BASELINE_SHA
               and c.get('status') == 'completed' and c.get('conclusion') == 'success' for c in checks):
        raise ValueError('The pinned V1 baseline must have successful CI before resetting')

    # Request cooperative shutdown; never terminate unrelated processes by PID/port.
    (root / 'stop.request').touch()
    deadline = time.monotonic() + stop_timeout
    while True:
        with _execution_lock(control_directory(root)) as controlled:
            if controlled:
                with _execution_lock(root) as stopped:
                    pass  # Close the Windows lock handle before renaming its directory.
                if stopped:
                    return _replace_rehearsal(root, github, REPOSITORY, prepare_source, git, Store)
        if time.monotonic() >= deadline:
            raise ValueError('Demo did not stop; previous state was left intact. Use Stop Phone Demo.bat and retry.')
        time.sleep(.25)


def _replace_rehearsal(root, github, repository, prepare_source, git, Store):
    identity = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    base = 'demo/rehearsal-' + identity
    response = github.api('POST', f'repos/{repository}/git/refs',
        {'ref': 'refs/heads/' + base, 'sha': BASELINE_SHA}, deadline=time.monotonic() + 45)
    if response.get('ref') != 'refs/heads/' + base or response.get('object', {}).get('sha') != BASELINE_SHA:
        raise ValueError('GitHub did not confirm the exact rehearsal branch; previous local state was preserved')
    staging = workspace_path(root.parent / (root.name + '-reset-staging') / identity)
    archive = workspace_path(root.parent / (root.name + '-archives') / identity)
    staging.mkdir(parents=True)
    # Prepare everything before moving the previous state. A network failure leaves it intact.
    prepare_source(staging / 'client-source', base)
    if git(staging / 'client-source', 'rev-parse', 'HEAD') != BASELINE_SHA:
        raise ValueError('Prepared client does not match the pinned V1 revision; previous state was preserved')
    providers = staging / 'providers'
    providers.mkdir()
    (providers / '.apishield-demo-state').touch()
    for name in ('theatre', 'payment'):
        Store(providers / (name + '.db'))
    (staging / '.phone-demo').touch()
    settings = {'version': 1, 'baseline_sha': BASELINE_SHA, 'base': base, 'archive': str(archive)}
    atomic_json(staging / 'rehearsal.json', settings)
    archive.parent.mkdir(parents=True, exist_ok=True)
    # Both absolute paths were resolved and confined to ProjectSeven above. No recursive deletion.
    root.rename(archive)
    try:
        staging.rename(root)
    except OSError:
        archive.rename(root)
        raise
    return {**settings, 'status': 'reset', 'root': str(root), 'start_required': True}
