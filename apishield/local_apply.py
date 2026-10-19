"""Explicit reviewed working-file application with stale checks and recovery."""
import hashlib
import json
import threading
from types import SimpleNamespace
from .configuration import load_config, relative_path
from .current_api import capture_api_context, accept_api_context
from .jobs import atomic_json, _atomic_bytes
from .workspace import working_files

_apply_lock = threading.Lock()


def recover_apply(jobs, integration, path, result, config):
    """Reconcile a completed write or restore a preflighted interrupted one."""
    manifest = path / 'local-apply.json'
    if not manifest.exists():
        return None
    if manifest.is_symlink():
        raise ValueError('Unsafe Apply recovery record')
    state = json.loads(manifest.read_text())
    if state.get('integration', integration) != integration:
        raise ValueError('Apply recovery belongs to another integration')
    if state.get('status') == 'applied':
        if state.get('files') != sorted(result['applied_files']):
            raise ValueError('Apply recovery differs from reviewed files')
        application = {key: state[key] for key in ('status', 'backup_id', 'files', 'accepted_hash')}
        atomic_json(path / 'result.json', {**result, 'application': application})
        return application
    if state.get('status') != 'prepared':
        return None
    originals = result.get('files', {})
    if set(state['files']) != set(result['applied_files']):
        raise ValueError('Apply recovery is missing reviewed files')
    restores = []
    for raw, info in state['files'].items():
        name = relative_path(raw)
        if name not in result['applied_files']:
            raise ValueError('Apply recovery contains an unreviewed path')
        destination, saved = config.repository / name, path / 'local-backup' / name
        if destination.is_symlink() or saved.is_symlink() or any(p.is_symlink() for p in destination.parents):
            raise ValueError('Unsafe recovery path')
        actual = hashlib.sha256(destination.read_bytes()).hexdigest() if destination.exists() else None
        permitted = {originals.get(name), result['applied_files'][name]}
        if not info['existed']:
            permitted.add(None)
        else:
            permitted.discard(None)
        if actual not in permitted:
            raise ValueError('Files changed after interruption; review the recovery backup before applying')
        content = saved.read_bytes() if info['existed'] else None
        if content is not None and hashlib.sha256(content).hexdigest() != originals.get(name):
            raise ValueError('Original recovery backup changed')
        restores.append((destination, content, info['mode']))
    context = result['api_context']
    current = capture_api_context(jobs, integration)
    if (current['config_fingerprint'] != context['config_fingerprint'] or
        current['accepted_hash'] not in {context['accepted_hash'], context['observed_hash']}):
        raise ValueError('Integration changed during interruption; review the recovery backup')
    for destination, content, mode in restores:
        if content is None:
            destination.unlink(missing_ok=True)
        else:
            _atomic_bytes(destination, content)
            destination.chmod(mode)
    atomic_json(jobs.store.root / '_current_api' / integration / 'state.json',
                {'config_identity': context['config_identity'], 'accepted_hash': context['accepted_hash']})
    atomic_json(manifest, {**state, 'status': 'rolled_back'})
    return None


def apply_local_repair(jobs, integration, job_id):
    with _apply_lock:
        path = jobs.store._path(job_id)
        result = jobs.store.get(job_id)
        if result.get('integration') != integration:
            raise ValueError('Repair belongs to a different integration')
        if result.get('application', {}).get('status') == 'applied':
            return result['application']
        if result.get('status') != 'validated' or result.get('proposal_source') != 'model' or not result.get('applied_files'):
            raise ValueError('Only a validated AI repair can be applied')
        patch = path / 'candidate.patch'
        if patch.is_symlink() or hashlib.sha256(patch.read_bytes()).hexdigest() != result.get('patch_sha256'):
            raise ValueError('Reviewed patch changed; regenerate the repair')
        config = load_config(jobs.integrations[integration])
        original = load_config(path / 'config.json')
        if config.repository != original.repository or original.source_mode != 'working':
            raise ValueError('Integration changed or repair has no working-source snapshot')
        recovered = recover_apply(jobs, integration, path, result, config)
        if recovered:
            return recovered
        context = result.get('api_context', {})
        current = capture_api_context(jobs, integration)
        if any(context.get(k) != current[k] for k in ('config_fingerprint', 'accepted_hash', 'observed_hash')):
            raise ValueError('API context changed; check and regenerate the repair')
        files, _ = working_files(SimpleNamespace(config=config, check=lambda: None, remaining=lambda: 30))
        hashes = {name: hashlib.sha256(content).hexdigest() for name, (content, _) in files.items()}
        source_hash = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
        if source_hash != result.get('source_hash'):
            raise ValueError('Current working files changed; regenerate the repair')
        writes, backup = {}, {}
        for raw, digest in result['applied_files'].items():
            name = relative_path(raw)
            destination = config.repository / name
            retained = path / 'applied-files' / name
            generated = name.startswith('tests/apishield_generated/test_') and name.endswith('.py')
            if name not in files and not generated:
                raise ValueError('Repair contains an unreviewed new file')
            if retained.is_symlink() or destination.is_symlink() or any(p.is_symlink() for p in destination.parents):
                raise ValueError('Unsafe repair file path')
            content = retained.read_bytes()
            if hashlib.sha256(content).hexdigest() != digest:
                raise ValueError('Reviewed replacement changed')
            if generated and destination.exists():
                raise ValueError('Generated checks would overwrite current tests')
            writes[name] = content
            backup[name] = {'existed': destination.exists(), 'mode': destination.stat().st_mode & 0o777 if destination.exists() else None}
            if destination.exists():
                saved = path / 'local-backup' / name
                saved.parent.mkdir(parents=True, exist_ok=True)
                _atomic_bytes(saved, destination.read_bytes())
        manifest = path / 'local-apply.json'
        atomic_json(manifest, {'status': 'prepared', 'files': backup, 'integration': integration})
        written = []
        try:
            for name, content in writes.items():
                destination = config.repository / name
                if destination.is_symlink() or any(p.is_symlink() for p in destination.parents):
                    raise ValueError('Repair path changed during Apply')
                current_bytes = destination.read_bytes() if destination.exists() else None
                if current_bytes != (files[name][0] if name in files else None):
                    raise ValueError('Working file changed during Apply')
                destination.parent.mkdir(parents=True, exist_ok=True)
                _atomic_bytes(destination, content)
                written.append(name)
                if backup[name]['mode'] is not None:
                    destination.chmod(backup[name]['mode'])
            accept_api_context(jobs, integration, context)
        except BaseException:
            for name in reversed(written):
                destination = config.repository / name
                if backup[name]['existed']:
                    _atomic_bytes(destination, (path / 'local-backup' / name).read_bytes())
                    destination.chmod(backup[name]['mode'])
                else:
                    destination.unlink(missing_ok=True)
            atomic_json(manifest, {'status': 'rolled_back', 'files': backup, 'integration': integration})
            raise
        application = {'status': 'applied', 'backup_id': job_id, 'files': sorted(writes),
                       'accepted_hash': context['observed_hash']}
        atomic_json(manifest, {**application, 'integration': integration, 'recovery_files': backup})
        atomic_json(path / 'result.json', {**result, 'application': application})
        if integration == 'banking-example':
            from .banking import demo
            with demo.lock:
                demo.adapter_root, demo.repaired = config.repository, True
        return application
