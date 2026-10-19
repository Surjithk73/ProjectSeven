from types import SimpleNamespace


def test_authentic_failure_receipt_retains_cause_and_rollback(tmp_path,monkeypatch):
    from apishield.automation import AutomationService
    from apishield.projects import ClientProject,ProviderBinding
    import demo.deployment.receipt as receipts
    jobs=SimpleNamespace(store=SimpleNamespace(root=tmp_path),publication=SimpleNamespace(github=None))
    service=AutomationService(jobs)
    project=ClientProject('cinema',str(tmp_path),[ProviderBinding('payment','pay','http://localhost:8102')],target_repository='owner/repo',deployment_actor='reviewer')
    service.projects.save(project.to_dict(),0)
    record=service.observe('cinema',{'payment':{'observed_hash':'a'*64}},'b'*40)
    receipt={'version':1,'project_id':'cinema','workflow_id':record['workflow_id'],'deployed_sha':'c'*40,
        'provider_hashes':{'payment':'a'*64},'status':'failed','health_passed':False,'smoke_passed':False,
        'error':'Seat browsing failed','rollback_sha':'b'*40}
    monkeypatch.setattr(receipts,'read_receipt',lambda *args:receipt)
    service.reconcile_deployment(project,record,{'publication':{'number':1}},'c'*40)
    saved=service.projects.workflows('cinema')[0]
    assert saved['receipt']['rollback_sha']=='b'*40
    assert 'Seat browsing failed' in saved['error']
    assert saved['state']=='failed'
