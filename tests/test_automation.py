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


def test_returning_to_prior_provider_combination_creates_fresh_current_work(tmp_path):
    service=make_service(tmp_path)
    payment={'payment':{'observed_hash':'a'*64}}
    first=service.observe('cinema',payment,'d'*40)
    second=service.observe('cinema',{**payment,'theatre':{'observed_hash':'b'*64}},'d'*40)
    third=service.observe('cinema',payment,'d'*40)
    assert third['workflow_id']!=first['workflow_id'] and third['state']=='awaiting_request'
    assert next(w for w in service.projects.workflows('cinema') if w['workflow_id']==second['workflow_id'])['state']=='superseded'


def test_interrupted_publication_reconciles_instead_of_sticking(tmp_path):
    service=make_service(tmp_path)
    record=service.observe('cinema',{'payment':{'observed_hash':'a'*64}},'d'*40)
    service.update('cinema',record['workflow_id'],state='preparing',publication_id='pub1')
    reconciled=[]
    service.jobs.publication=SimpleNamespace(store=SimpleNamespace(read=lambda identity:{'id':identity,'status':'reconciliation_needed'}),reconcile=reconciled.append)
    service.advance(service.projects.load_project('cinema'))
    assert reconciled==['pub1']


def test_generation_refreshes_merged_publication_base(tmp_path):
    service=make_service(tmp_path)
    changes={'payment':{'observed_hash':'a'*64}}
    old=service.observe('cinema',changes,'b'*40)
    refreshed=[]
    service.jobs.model_connection.ready=True
    service.source=lambda project,refresh=False: refreshed.append(refresh) or 'c'*40
    service.snapshots=lambda project: ({},changes)
    service.config=lambda *args: None
    service.jobs.create_config_job=lambda integration,config,operation,job_id: SimpleNamespace(id=job_id,path=tmp_path,_initial={})
    service.jobs.dispatch=lambda job: None
    generated=service.dispatch_change('cinema',old['workflow_id'])
    assert refreshed==[True]
    assert generated['source_sha']=='c'*40 and generated['state']=='generating'


def test_restart_at_merged_source_keeps_deployment_workflow(tmp_path):
    service = make_service(tmp_path)
    changes = {'payment': {'observed_hash':'a'*64}}
    record = service.observe('cinema', changes, 'b'*40)
    service.update('cinema', record['workflow_id'], state='pr_open', publication_id='p1')
    service.snapshots = lambda project: ({}, changes)
    service.source = lambda project: 'c'*40
    def advance(project):
        service.update('cinema', record['workflow_id'], state='merged', merge_sha='c'*40)
    service.advance = advance
    service.tick()
    rows = service.projects.workflows('cinema')
    assert len(rows) == 1 and rows[0]['state'] == 'merged'
    # Unrelated source edits and fresh provider changes must still supersede.
    next_record = service.observe('cinema', changes, 'd'*40)
    assert next_record['workflow_id'] != record['workflow_id']
