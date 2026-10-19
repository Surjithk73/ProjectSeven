from types import SimpleNamespace
import pytest


def make_service(tmp_path):
    from apishield.automation import AutomationService
    from apishield.projects import ClientProject, ProviderBinding
    jobs = SimpleNamespace(store=SimpleNamespace(root=tmp_path), model_connection=SimpleNamespace(ready=False))
    service = AutomationService(jobs)
    service.projects.save(ClientProject('cinema', str(tmp_path), [ProviderBinding('payment', 'pay', 'http://localhost:8102')]).to_dict(), 0)
    return service


def test_manual_detection_is_durable_and_never_calls_model(tmp_path):
    service = make_service(tmp_path)
    change = {'payment': {'base_hash': 'a'*64, 'observed_hash': 'b'*64, 'change_id': 'c'*64}}
    first = service.observe('cinema', change, 'd'*40)
    assert first['state'] == 'awaiting_request'
    assert service.observe('cinema', change, 'd'*40)['workflow_id'] == first['workflow_id']
    assert len(service.projects.workflows('cinema')) == 1
    assert service.projects.load_project('cinema').automation_mode == 'manual'


def test_automatic_activation_requires_real_connections(tmp_path):
    service = make_service(tmp_path)
    with pytest.raises(ValueError, match='AI connection'):
        service.set_automation_mode('cinema', 'automatic_edit', 1)


def test_combined_changes_supersede_stale_proposal_and_failure_does_not_requeue(tmp_path):
    service = make_service(tmp_path)
    first = service.observe('cinema', {'payment': {'observed_hash': 'a'*64}}, 'd'*40)
    second = service.observe('cinema', {'payment': {'observed_hash': 'a'*64}, 'theatre': {'observed_hash': 'b'*64}}, 'd'*40)
    assert len(second['providers']) == 2
    assert service.projects.workflows('cinema')[0]['state'] == 'superseded'
    service.update('cinema', second['workflow_id'], state='failed', error='model timeout')
    assert service.observe('cinema', second['providers'], 'd'*40)['state'] == 'failed'


def test_disable_mode_persists_and_failed_job_requires_explicit_retry(tmp_path):
    service = make_service(tmp_path)
    record = service.observe('cinema', {'payment': {'observed_hash': 'a'*64}}, 'd'*40)
    service.update('cinema', record['workflow_id'], state='failed', error='timeout')
    assert service.set_automation_mode('cinema', 'manual', 1)['automation_mode'] == 'manual'
    assert service.projects.workflows('cinema')[0]['state'] == 'failed'


def test_superseding_a_running_candidate_cancels_it(tmp_path):
    service = make_service(tmp_path)
    canceled = []
    service.jobs.store.cancel = canceled.append
    first = service.observe('cinema', {'payment': {'observed_hash': 'a'*64}}, 'd'*40)
    service.update('cinema', first['workflow_id'], state='generating', job_id='job-1')
    service.observe('cinema', {'payment': {'observed_hash': 'b'*64}}, 'd'*40)
    assert canceled == ['job-1']
