"""Accepted API contract and a separately captured provider observation."""
from pathlib import Path
import json
import hashlib
import threading
from dataclasses import replace
from types import SimpleNamespace
from .configuration import load_config
from .contract_fetch import canonical_hash, parse_contract
from .jobs import atomic_json

_overview_guard = threading.Lock()
_overview_locks = {}


def capture_api_context(jobs, integration):
    config = load_config(jobs.integrations[integration])
    directory = jobs.store.root / '_current_api' / integration
    if directory.is_symlink() or directory.parent.is_symlink():
        raise ValueError('Unsafe current API state')
    directory.mkdir(parents=True, exist_ok=True)
    state_path = directory / 'state.json'
    if state_path.is_symlink():
        raise ValueError('Unsafe current API state')
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    config_identity = str(config.path) + ':' + str(config.repository)
    config_fingerprint = canonical_hash(config.to_dict())
    if state.get('config_identity') != config_identity:
        if integration == 'banking-example':
            from .banking import FIXTURE
            baseline = parse_contract((FIXTURE / 'base.json').read_bytes())
        else:
            baseline = parse_contract(config.base_spec.read_bytes())
        state = {'config_identity': config_identity, 'accepted_hash': baseline.content_hash}
        atomic_json(directory / f'{baseline.content_hash}.json', baseline.document)
        atomic_json(state_path, state)
    version = None
    if integration == 'banking-example':
        from .banking import active_contract, demo
        with demo.lock:
            document, version = active_contract(), demo.version
        observed = parse_contract(json.dumps(document).encode())
        kind = 'banking_provider'
    else:
        monitor = jobs.monitoring.store.read(integration)
        if monitor['configured'] and monitor['source_url']:
            observed = jobs.monitoring.fetcher(monitor['source_url'], monitor['allow_local'])
            kind = 'live_documentation'
        else:
            observed = parse_contract(config.target_spec.read_bytes())
            kind = 'local_documentation'
    target = directory / f'{observed.content_hash}.json'
    atomic_json(target, observed.document)
    return {'base_spec': directory / f"{state['accepted_hash']}.json", 'target_spec': target,
            'accepted_hash': state['accepted_hash'], 'observed_hash': observed.content_hash,
            'source_kind': kind, 'provider_version': version, 'config_fingerprint': config_fingerprint,
            'config_identity': config_identity}


def accept_api_context(jobs, integration, context):
    current = capture_api_context(jobs, integration)
    if current['config_fingerprint'] != context['config_fingerprint'] or current['observed_hash'] != context['observed_hash']:
        raise ValueError('API context changed; check and regenerate the repair')
    state = {'config_identity': current['config_identity'], 'accepted_hash': context['observed_hash']}
    atomic_json(jobs.store.root / '_current_api' / integration / 'state.json', state)
    return state


def current_overview(jobs, integration):
    with _overview_guard:
        lock = _overview_locks.setdefault((str(jobs.store.root), integration), threading.Lock())
    with lock:
        return _build_current_overview(jobs, integration)


def _build_current_overview(jobs, integration):
    from .workspace import working_files
    from .engine import run_job
    context = capture_api_context(jobs, integration)
    config = replace(load_config(jobs.integrations[integration]), source_mode='working',
                     base_spec=context['base_spec'], target_spec=context['base_spec'], requirements=[])
    view = SimpleNamespace(config=config, check=lambda: None, remaining=lambda: 30)
    files, _ = working_files(view)
    hashes = {name: hashlib.sha256(content).hexdigest() for name, (content, _) in files.items()}
    digest = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    for record in jobs.store.list_jobs():
        recorded = record.get('api_context', {})
        if (record.get('integration') == integration and record.get('operation') == 'compare'
            and record.get('status') == 'completed' and record.get('source_hash') == digest
            and recorded.get('accepted_hash') == context['accepted_hash']
            and recorded.get('observed_hash') == context['observed_hash']
            and record.get('comparison', {}).get('changed_operations')):
            return record['job_id']
    for record in reversed(jobs.store.list_jobs()):
        if (record.get('integration') == integration and record.get('operation') == 'scan'
            and record.get('status') == 'completed' and record.get('source_hash') == digest
            and record.get('model_revision', 0) == jobs.model_revision
            and record.get('model_connection', {}).get('provider') == jobs.model_connection.provider
            and record.get('api_context', {}).get('observed_hash') == context['observed_hash']
            and record.get('api_context', {}).get('accepted_hash') == context['accepted_hash']):
            return record['job_id']
    job = jobs.store.create(config, 'scan')
    job._initial.update(integration=integration, model_revision=jobs.model_revision, current_overview=True,
                        api_context={key: str(value) if isinstance(value, Path) else value for key, value in context.items()})
    jobs._capture_model(job)
    result = run_job(config, 'scan', jobs.store, job=job)
    if result['status'] != 'completed':
        raise ValueError(result.get('error', 'Could not build current overview'))
    if jobs.model_connection.ready:
        from .graph_semantics import interpret_graph
        from .model_access import connection_error
        try:
            overlay = interpret_graph(result['semantic_graph'], job._model_connection, config.model)
            atomic_json(job.path / 'graph-ai.json', overlay)
            atomic_json(job.path / 'result.json', {**result, 'ai_graph_status': 'completed'})
        except Exception as error:
            result = {**result, 'ai_graph_error': connection_error(error)['message'], 'ai_graph_status': 'failed'}
            atomic_json(job.path / 'result.json', result)
    return job.id
