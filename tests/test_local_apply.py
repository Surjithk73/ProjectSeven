import json
from dataclasses import replace
import pytest
from apishield.configuration import load_config
from apishield.engine import run_job
from apishield.dashboard_jobs import LocalJobs
from apishield.current_api import capture_api_context
from apishield.local_apply import apply_local_repair
from test_local_engine import shipment, git


def repair(shipment, monkeypatch):
    repo, path, candidate, store, raw = shipment
    monkeypatch.setattr('apishield.engine.generate_candidate', lambda *a, **k: json.loads(candidate.read_text()))
    jobs = LocalJobs(store.root, {'client': str(path)})
    context = capture_api_context(jobs, 'client')
    config = replace(load_config(path), source_mode='working')
    job = store.create(config, 'repair')
    job._initial.update(integration='client', api_context={k: str(v) if hasattr(v, 'read_bytes') else v for k, v in context.items()})
    result = run_job(config, 'repair', store, job=job)
    assert result['status'] == 'validated'
    return repo, jobs, job, context


def test_apply_updates_working_files_without_commit_and_accepts_target(shipment, monkeypatch):
    repo, jobs, job, context = repair(shipment, monkeypatch)
    head = git(repo, 'rev-parse', 'HEAD')
    try:
        result = apply_local_repair(jobs, 'client', job.id)
        assert result['status'] == 'applied'
        assert '/shipments/create' in (repo / 'src/client.py').read_text()
        assert git(repo, 'rev-parse', 'HEAD') == head
        assert capture_api_context(jobs, 'client')['accepted_hash'] == context['observed_hash']
        assert apply_local_repair(jobs, 'client', job.id) == result
        assert (job.path / 'local-backup/src/client.py').exists()
    finally:
        jobs.close()


def test_apply_refuses_intervening_user_edits(shipment, monkeypatch):
    repo, jobs, job, context = repair(shipment, monkeypatch)
    source = repo / 'src/client.py'
    source.write_text('USER_CHANGE = 1\n')
    try:
        with pytest.raises(ValueError, match='changed'):
            apply_local_repair(jobs, 'client', job.id)
        assert source.read_text() == 'USER_CHANGE = 1\n'
        assert capture_api_context(jobs, 'client')['accepted_hash'] == context['accepted_hash']
    finally:
        jobs.close()


def test_apply_rolls_back_files_when_contract_acceptance_fails(shipment, monkeypatch):
    repo, jobs, job, context = repair(shipment, monkeypatch)
    source = repo / 'src/client.py'
    original = source.read_bytes()
    def fail(*args):
        raise OSError('simulated write failure')
    monkeypatch.setattr('apishield.local_apply.accept_api_context', fail)
    try:
        with pytest.raises(OSError):
            apply_local_repair(jobs, 'client', job.id)
        assert source.read_bytes() == original
        assert capture_api_context(jobs, 'client')['accepted_hash'] == context['accepted_hash']
        assert json.loads((job.path / 'local-apply.json').read_text())['status'] == 'rolled_back'
    finally:
        jobs.close()


def test_retry_restores_a_prepared_apply_interrupted_after_a_write(shipment, monkeypatch):
    from apishield.jobs import atomic_json
    repo, jobs, job, context = repair(shipment, monkeypatch)
    source = repo / 'src/client.py'
    backup = job.path / 'local-backup/src/client.py'
    backup.parent.mkdir(parents=True)
    backup.write_bytes(source.read_bytes())
    source.write_bytes((job.path / 'applied-files/src/client.py').read_bytes())
    atomic_json(job.path / 'local-apply.json', {'status': 'prepared', 'integration': 'client',
        'files': {'src/client.py': {'existed': True, 'mode': source.stat().st_mode & 0o777}}})
    try:
        assert apply_local_repair(jobs, 'client', job.id)['status'] == 'applied'
    finally:
        jobs.close()


def test_recovery_refuses_user_deleted_existing_source(shipment, monkeypatch):
    from apishield.jobs import atomic_json
    repo, jobs, job, context = repair(shipment, monkeypatch)
    source = repo / 'src/client.py'
    backup = job.path / 'local-backup/src/client.py'
    backup.parent.mkdir(parents=True)
    backup.write_bytes(source.read_bytes())
    atomic_json(job.path / 'local-apply.json', {'status': 'prepared', 'integration': 'client',
        'files': {'src/client.py': {'existed': True, 'mode': source.stat().st_mode & 0o777}}})
    source.unlink()
    try:
        with pytest.raises(ValueError, match='changed'):
            apply_local_repair(jobs, 'client', job.id)
        assert not source.exists()
    finally:
        jobs.close()
