"""Bounded native oasdiff evidence and conservative operation localization."""
import json
import os
from pathlib import Path
import re
import shutil

from .commands import run_command

METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}


class _CommandView:
    def __init__(self, job, workspace):
        self._job, self.workspace = job, workspace

    def __getattr__(self, name):
        return getattr(self._job, name)


def _references(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == '$ref' and (not isinstance(item, str) or not item.startswith('#/')):
                raise ValueError('External contract references are unsupported in local comparison')
            _references(item)
    elif isinstance(value, list):
        for item in value:
            _references(item)


def _operations(spec):
    paths = spec.get('paths')
    if not isinstance(paths, dict) or not isinstance(spec.get('openapi'), str):
        raise ValueError('Comparison requires OpenAPI JSON with a paths object')
    operations = {}
    for endpoint, path in paths.items():
        if not isinstance(endpoint, str) or not endpoint.startswith('/') or not isinstance(path, dict):
            raise ValueError('Invalid OpenAPI path')
        shared = {key: value for key, value in path.items() if key not in METHODS}
        for method in METHODS:
            if method in path:
                if not isinstance(path[method], dict):
                    raise ValueError('Invalid OpenAPI operation')
                operations[(method.upper(), endpoint)] = {'operation': path[method], 'path_settings': shared}
    return operations


def compare_contracts(job) -> dict:
    base = json.loads((job.path / 'contracts/base.json').read_text(encoding='utf-8'))
    target = json.loads((job.path / 'contracts/target.json').read_text(encoding='utf-8'))
    _references(base); _references(target)
    old, new = _operations(base), _operations(target)
    executable = os.environ.get('OASDIFF_BIN') or shutil.which('oasdiff')
    if not executable and os.name == 'nt':
        development = Path(__file__).resolve().parents[1] / 'tools/oasdiff.exe'
        if development.is_file():
            executable = str(development)
    if not executable:
        raise ValueError('Native oasdiff unavailable; set OASDIFF_BIN or install oasdiff on PATH')
    cwd = job.path / 'comparison'
    cwd.mkdir(exist_ok=True)
    evidence = run_command([executable, 'diff', str(job.path / 'contracts/base.json'),
        str(job.path / 'contracts/target.json'), '--format', 'json', '--allow-external-refs=false'],
        _CommandView(job, cwd), 'oasdiff')
    job.check()
    if evidence['exit_code'] != 0 or evidence['timed_out'] or evidence['cancelled'] or evidence['output_limited']:
        raise ValueError(f'Native comparison failed or incomplete: {evidence}')
    try:
        diff = json.loads(evidence['stdout'])
        if not isinstance(diff, dict):
            raise ValueError('oasdiff JSON must be an object')
    except (ValueError, TypeError) as exc:
        raise ValueError('Native comparison returned invalid JSON evidence') from exc
    global_change = any(base.get(key) != target.get(key) for key in ('components', 'security', 'servers'))
    changed = [{'method': method, 'endpoint': endpoint}
        for method, endpoint in sorted(set(old) | set(new))
        if old.get((method, endpoint)) != new.get((method, endpoint)) or global_change]
    return {'diff': diff, 'changed_operations': changed, 'evidence': evidence,
        'limitations': ['Shared components/security/server changes conservatively impact all operations'] if global_change else []}


def impacted_sites(scan, comparison):
    def normalized(endpoint):
        return re.sub(r'\{[^}]+\}', '{}', endpoint)
    changed = {(item['method'], normalized(item['endpoint'])) for item in comparison['changed_operations']}
    return [site for site in scan['sites'] if site['endpoint'] is not None
        and (site['method'], normalized(site['endpoint'])) in changed]
