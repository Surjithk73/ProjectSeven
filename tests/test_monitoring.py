from test_model_access import credential, fake_credentials
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
import threading
import time

import pytest
from fastapi.testclient import TestClient

import dashboard_api
from apishield.dashboard_jobs import LocalJobs
from apishield.monitoring import MonitorService
from apishield.monitor_state import MonitorConflict
from test_dashboard_jobs import configured_source
from test_monitor_state import contract, settings


@pytest.fixture
def monitor(tmp_path, monkeypatch):
    path = configured_source(tmp_path)
    for name in ('base.json','target.json'):
        (tmp_path / name).write_bytes(contract().raw)
    jobs = LocalJobs(tmp_path / 'jobs', {'parcel':str(path)})
    def complete(job, candidate=None):
        job.finish({'status':'completed','comparison':{'fixture':True}})
        job.cleanup()
        with jobs.lock:
            jobs.active.pop(job.id,None)
    monkeypatch.setattr(jobs,'_run',complete)
    value = jobs.monitoring
    value.fetcher = lambda url, allow_local: contract()
    value.configure('parcel',settings(),0)
    yield value
    jobs.close()


def wait(monitor):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = monitor.store.read('parcel')
        if state['active_check'] is None:
            return state
        time.sleep(.01)
    pytest.fail('Monitor did not finish')


def test_initialize_deduplicate_and_accept(monitor):
    monitor.check('parcel')
    state = wait(monitor)
    assert state['baseline_hash'] == contract().content_hash
    assert not state['changes'] and not monitor.jobs.store.list_jobs()
    monitor.fetcher = lambda *args: contract('2')
    monitor.check('parcel')
    changed = wait(monitor)
    assert len(changed['changes']) == 1
    change = changed['changes'][0]
    monitor.check('parcel')
    assert len(wait(monitor)['changes']) == 1
    assert len(monitor.jobs.store.list_jobs()) == 1
    assert monitor.jobs.store.get(change['job_id'])['operation'] == 'compare'
    monitor.store.accept('parcel',change['id'],changed['revision'])
    monitor.check('parcel')
    assert wait(monitor)['baseline_hash'] == contract('2').content_hash
    assert len(monitor.jobs.store.list_jobs()) == 1


def test_saved_baseline_and_formatting_only(monitor):
    body = settings()
    body['baseline_mode'] = 'saved'
    monitor.configure('parcel',body,1)
    monitor.fetcher = lambda *args: contract('2')
    monitor.check('parcel')
    assert len(wait(monitor)['changes']) == 1
    from apishield.contract_fetch import parse_contract
    monitor.fetcher = lambda *args: parse_contract(json.dumps(contract('2').document,indent=4).encode())
    monitor.check('parcel')
    assert len(wait(monitor)['changes']) == 1
    assert len(monitor.jobs.store.list_jobs()) == 1


def test_failure_preserves_success_and_recovers(monitor):
    monitor.check('parcel')
    before = wait(monitor)
    def fail(*args):
        raise ValueError('fixture unavailable')
    monitor.fetcher = fail
    monitor.check('parcel')
    failed = wait(monitor)
    assert failed['error'] == 'fixture unavailable'
    assert failed['baseline_hash'] == before['baseline_hash']
    assert failed['last_success'] == before['last_success']
    monitor.fetcher = lambda *args: contract()
    monitor.check('parcel')
    assert wait(monitor)['error'] is None


@pytest.mark.parametrize('mutation', ['pause','url','integration'])
def test_overlap_and_stale_fetch(monitor, mutation):
    body = settings(); body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    entered, release = threading.Event(), threading.Event()
    def blocked(*args):
        entered.set()
        release.wait(5)
        return contract('2')
    monitor.fetcher = blocked
    monitor.check('parcel')
    assert entered.wait(2)
    with pytest.raises(MonitorConflict):
        monitor.check('parcel')
    if mutation == 'integration':
        path = monitor.jobs.integrations['parcel']
        data = json.loads(open(path).read())
        data['use_intent'] = False
        with open(path,'w') as stream:
            json.dump(data,stream)
    else:
        body = settings(); body['baseline_mode']='saved'
        if mutation == 'pause':
            body['enabled'] = False
        else:
            body['source_url'] += '?v=2'
        monitor.configure('parcel',body,2)
    release.set()
    assert not wait(monitor)['changes']
    assert not monitor.jobs.store.list_jobs()


def test_schedule_coalesces_and_restart_keeps_state(monitor):
    now = datetime.now(timezone.utc)
    with monitor.store.transaction('parcel') as state:
        state['next_due'] = (now-timedelta(days=10)).isoformat()
    monitor.tick(now)
    wait(monitor)
    monitor.tick(now)
    assert not monitor.jobs.store.list_jobs()
    restored = MonitorService(monitor.jobs)
    assert restored.store.read('parcel')['baseline_hash'] == contract().content_hash
    restored.close()


def test_process_loss_claim_is_recovered(monitor):
    with monitor.store.transaction('parcel') as state:
        state['active_check'] = {'id':'dead','pid':99999999,'revision':state['revision']}
    restored = MonitorService(monitor.jobs)
    assert restored.store.read('parcel')['active_check'] is None
    assert 'interrupted' in restored.store.read('parcel')['error'].lower()
    restored.close()


def test_close_prevents_late_publication(monitor):
    entered, release = threading.Event(), threading.Event()
    def blocked(*args):
        entered.set(); release.wait(5)
        return contract('2')
    monitor.fetcher = blocked
    monitor.check('parcel')
    assert entered.wait(2)
    monitor.close()
    release.set()
    assert not wait(monitor)['changes']


def test_configuration_capture_and_source_commit(monitor):
    monitor.fetcher = lambda *args: contract('2')
    body=settings(); body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    monitor.check('parcel')
    change=wait(monitor)['changes'][0]
    config=json.loads((monitor.jobs.store._path(change['job_id'])/'config.json').read_text())
    assert len(config['ref'])==40
    assert config['base_spec'] != str(monitor.jobs.store.root.parent/'base.json')
    assert config['requirements']==[]


def test_local_endpoints_guard_and_readonly(monitor):
    previous=getattr(dashboard_api.app.state,'local_jobs',None)
    dashboard_api.app.state.local_jobs=monitor.jobs
    try:
        client=TestClient(dashboard_api.app)
        url='/api/integrations/parcel/monitoring'
        assert client.get(url).status_code==200
        assert client.put(url,json={**settings(), 'expected_revision':1}).status_code==403
        assert client.get(url,headers={'Origin':'https://evil.example'}).status_code==403
        assert client.get('/api/integrations/missing/monitoring').status_code==404
        from apishield.jobs import atomic_json
        atomic_json(monitor.jobs.store.root/'integrations.json', {'parcel':{'config':monitor.jobs.integrations['parcel'],'example':False}})
        assert client.put(url,json={**settings(), 'expected_revision':0}).status_code==409
        assert client.put(url,json={**settings(), 'expected_revision':1, 'command':'unsafe'}).status_code==422
        assert client.put(url,json={**settings(), 'expected_revision':1}).status_code==200
        assert client.post(url+'/check').status_code==202
        wait(monitor)
        assert client.post(url+'/accept',json={'change_id':'missing','expected_revision':2}).status_code==404
    finally:
        if previous is None:
            del dashboard_api.app.state.local_jobs
        else:
            dashboard_api.app.state.local_jobs=previous


def test_two_coordinators_cannot_claim_same_check(monitor):
    entered,release=threading.Event(),threading.Event()
    def blocked(*args):
        entered.set(); release.wait(5)
        return contract()
    monitor.fetcher=blocked
    other=MonitorService(monitor.jobs)
    monitor.check('parcel')
    assert entered.wait(2)
    try:
        with pytest.raises(MonitorConflict):
            other.check('parcel')
    finally:
        release.set()
        wait(monitor)
        other.close()


def test_missing_model_key_prevents_explicit_repair(monitor,monkeypatch):
    from apishield.model_access import disabled_connection
    monitor.jobs.select_model(disabled_connection())
    body=settings(); body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    monitor.fetcher=lambda *args:contract('2')
    monitor.check('parcel')
    change=wait(monitor)['changes'][0]
    with pytest.raises(ValueError,match='model connection'):
        monitor.repair('parcel',change['id'])
    assert len(monitor.jobs.store.list_jobs())==1


def test_dispatch_failure_is_visible_and_job_retained(monitor,monkeypatch):
    body=settings(); body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    monitor.fetcher=lambda *args:contract('2')
    def fail(job):
        raise RuntimeError('executor unavailable')
    monkeypatch.setattr(monitor.jobs,'dispatch',fail)
    monitor.check('parcel')
    change=wait(monitor)['changes'][0]
    deadline=time.monotonic()+2
    while monitor.jobs.store.get(change['job_id'])['status']=='queued' and time.monotonic()<deadline:
        time.sleep(.01)
    assert monitor.jobs.store.get(change['job_id'])['status']=='failed'


def test_real_shared_engine_comparison(monitor,monkeypatch):
    monkeypatch.setattr(monitor.jobs,'_run',LocalJobs._run.__get__(monitor.jobs))
    body=settings();body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    monitor.fetcher=lambda *args:contract('2')
    monitor.check('parcel')
    change=wait(monitor)['changes'][0]
    deadline=time.monotonic()+20
    while time.monotonic()<deadline:
        result=monitor.jobs.store.get(change['job_id'])
        if result['status'] not in {'queued','running'}:
            break
        time.sleep(.03)
    assert result['status'] in {'completed','no_change'}
    assert result['source_commit']


def test_explicit_rescan_preserves_change_and_job_history(monitor):
    body=settings();body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    monitor.fetcher=lambda *args:contract('2')
    monitor.check('parcel')
    change=wait(monitor)['changes'][0]
    result=monitor.rescan('parcel',change['id'])
    assert result['job_id'] != change['job_id']
    record=monitor.store.read('parcel')['changes'][0]
    assert record['job_id']==result['job_id']
    assert record['job_ids']==[change['job_id'],result['job_id']]
    assert len(monitor.store.read('parcel')['changes'])==1


def test_acceptance_during_fetch_cannot_be_overwritten(monitor):
    body=settings();body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    monitor.fetcher=lambda *args:contract('2')
    monitor.check('parcel')
    change=wait(monitor)['changes'][0]
    entered,release=threading.Event(),threading.Event()
    def blocked(*args):
        entered.set();release.wait(5)
        return contract('3')
    monitor.fetcher=blocked
    monitor.check('parcel')
    assert entered.wait(2)
    monitor.store.accept('parcel',change['id'],2)
    release.set()
    final=wait(monitor)
    assert final['baseline_hash']==contract('2').content_hash
    assert len(final['changes'])==1


def test_repair_uses_retained_contracts_and_requirements(monitor,monkeypatch,fake_credentials):
    body=settings();body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    monitor.fetcher=lambda *args:contract('2')
    monitor.check('parcel')
    change=wait(monitor)['changes'][0]
    from apishield.model_access import cloud_connection
    monitor.jobs.select_model(cloud_connection(credential()))
    captured=[]
    def submit(name,config,operation):
        captured.append((config,operation))
        return {'job_id':'fixture'}
    monkeypatch.setattr(monitor.jobs,'submit_config',submit)
    monitor.repair('parcel',change['id'])
    config,operation=captured[0]
    assert operation=='repair' and len(config.ref)==40
    assert config.base_spec.read_bytes()==contract().raw
    assert config.target_spec.read_bytes()==contract('2').raw
    config.target_spec.write_text('{}')
    with pytest.raises(ValueError,match='snapshot'):
        monitor.repair('parcel',change['id'])


def test_separate_process_cannot_duplicate_active_claim(monitor,tmp_path):
    import subprocess
    import sys
    from apishield.commands import sanitized_environment
    from apishield.configuration import load_config
    ready,release=tmp_path/'claimed',tmp_path/'release'
    script='''
import sys,time
from pathlib import Path
from apishield.dashboard_jobs import LocalJobs
from apishield.contract_fetch import parse_contract
jobs=LocalJobs(Path(sys.argv[1]),{'parcel':sys.argv[2]})
ready,release=Path(sys.argv[3]),Path(sys.argv[4])
def fetch(*args):
    ready.write_text('claimed')
    deadline=time.monotonic()+10
    while not release.exists() and time.monotonic()<deadline:
        time.sleep(.01)
    return parse_contract(b'{"openapi":"3.0.0","info":{"title":"Fixture","version":"1"},"paths":{}}')
jobs.monitoring.fetcher=fetch
jobs.monitoring.check('parcel')
deadline=time.monotonic()+10
while not release.exists() and time.monotonic()<deadline:
    time.sleep(.01)
jobs.close()
'''
    path=monitor.jobs.integrations['parcel']
    process=subprocess.Popen([sys.executable,'-B','-c',script,str(monitor.jobs.store.root),path,str(ready),str(release)],
                             env=sanitized_environment(load_config(path)),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        deadline=time.monotonic()+5
        while not ready.exists() and time.monotonic()<deadline and process.poll() is None:
            time.sleep(.01)
        assert ready.exists()
        with pytest.raises(MonitorConflict):
            monitor.check('parcel')
    finally:
        release.touch()
        try:
            output,error=process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            output,error=process.communicate()
    assert process.returncode==0,error.decode()


def test_scheduled_configuration_failure_is_visible_and_not_a_retry_burst(monitor,monkeypatch):
    import apishield.monitoring as module
    monitor.check('parcel')
    prior=wait(monitor)
    calls=[]
    def broken(path):
        calls.append(path)
        raise ValueError('repository disappeared')
    monkeypatch.setattr(module,'load_config',broken)
    now=datetime.now(timezone.utc)
    with monitor.store.transaction('parcel') as state:
        state['next_due']=(now-timedelta(days=1)).isoformat()
    monitor.tick(now)
    failed=monitor.store.read('parcel')
    assert failed['error']=='repository disappeared'
    assert failed['baseline_hash']==prior['baseline_hash']
    assert datetime.fromisoformat(failed['next_due'])>now
    monitor.tick(now)
    assert len(calls)==1


@pytest.mark.parametrize('boundary',['before_construction','construction','dispatch','configuration_edit'])
def test_process_loss_preserves_comparison_reservation_identity(monitor,tmp_path,boundary):
    import subprocess
    import sys
    from apishield.commands import sanitized_environment
    from apishield.configuration import load_config
    body=settings();body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    script='''
import os,sys,time
from pathlib import Path
from apishield.dashboard_jobs import LocalJobs
from apishield.contract_fetch import parse_contract
jobs=LocalJobs(Path(sys.argv[1]),{'parcel':sys.argv[2]})
jobs.monitoring.fetcher=lambda *args:parse_contract(b'{"openapi":"3.0.0","info":{"title":"Fixture","version":"2"},"paths":{}}')
if sys.argv[3] in {'construction','before_construction','configuration_edit'}:
    original=jobs.create_config_job
    def crash(*args,**kwargs):
        if sys.argv[3]=='before_construction':
            os._exit(17)
        job=original(*args,**kwargs)
        os._exit(17)
    jobs.create_config_job=crash
else:
    jobs.dispatch=lambda job:os._exit(17)
jobs.monitoring.check('parcel')
time.sleep(10)
os._exit(18)
'''
    path=monitor.jobs.integrations['parcel']
    result=subprocess.run([sys.executable,'-B','-c',script,str(monitor.jobs.store.root),path,boundary],
                          env=sanitized_environment(load_config(path)),capture_output=True,timeout=15)
    assert result.returncode==17,result.stderr.decode()
    prior_jobs=monitor.jobs.store.list_jobs()
    assert len(prior_jobs)==(0 if boundary=='before_construction' else 1)
    persisted=monitor.store.read('parcel')
    identity=(persisted['active_check']['reservation']['job_id'] if persisted['active_check'] else persisted['changes'][0]['job_id'])
    if boundary=='configuration_edit':
        data=json.loads(open(path).read());data['use_intent']=False
        with open(path,'w') as stream:
            json.dump(data,stream)
    restored=LocalJobs(monitor.jobs.store.root,{'parcel':path})
    try:
        restored.monitoring.fetcher=lambda *args:contract('2')
        state=restored.monitoring.store.read('parcel')
        if boundary=='configuration_edit':
            assert not state['changes']
            assert state['baseline_hash'] is None
            return
        assert len(state['changes'])==1
        assert state['changes'][0]['job_id']==identity
        restored.monitoring.check('parcel')
        wait(restored.monitoring)
        assert len(restored.store.list_jobs())==1
    finally:
        restored.close()


def test_shutdown_preserves_reserved_change_before_construction(monitor,monkeypatch):
    body=settings();body['baseline_mode']='saved'
    monitor.configure('parcel',body,1)
    monitor.fetcher=lambda *args:contract('2')
    entered,release=threading.Event(),threading.Event()
    original=monitor.jobs.create_config_job
    def blocked(*args,**kwargs):
        if threading.current_thread() is not threading.main_thread():
            entered.set();release.wait(5)
        return original(*args,**kwargs)
    monkeypatch.setattr(monitor.jobs,'create_config_job',blocked)
    monitor.check('parcel')
    assert entered.wait(2)
    reservation=monitor.store.read('parcel')['active_check']['reservation']
    try:
        monitor.close()
        state=monitor.store.read('parcel')
        assert len(state['changes'])==1
        assert state['changes'][0]['job_id']==reservation['job_id']
        assert monitor.jobs.store.get(reservation['job_id'])['status']=='failed'
    finally:
        release.set()
