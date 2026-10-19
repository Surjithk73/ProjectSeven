import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from types import SimpleNamespace

import pytest

from apishield.configuration import load_config
from apishield.jobs import JobStore,atomic_json
from test_dashboard_jobs import configured_source

SHA='a'*40
COMMIT='b'*40
TREE='c'*40
PATCH=b'--- a/src/client.py\n+++ b/src/client.py\n@@ -1 +1 @@\n-A = 1\n+A = 2\n'


class GitHub:
    def __init__(self):
        self.tip=SHA;self.branch=None;self.pr=None;self.calls=[]
        self.fail_branch=False;self.fail_pr=False;self.move_after_commit=False
    def inspect_target(self,repository,base,**kwargs):
        return {'repository':repository,'base':base,'source_commit':self.tip,'tree':TREE,
                'account':{'login':'fixture','id':7},'permission':'write','private':True,'url':'https://github.com/'+repository}
    def create_source_commit(self,target,files,message,**kwargs):
        self.calls.append('commit')
        if self.move_after_commit:self.tip='e'*40
        return {'sha':COMMIT,'tree':TREE,'parent':SHA}
    def ensure_branch(self,target,branch,commit,**kwargs):
        self.calls.append('branch')
        if self.branch and self.branch!=commit['sha']:raise ValueError('branch collision')
        self.branch=commit['sha']
        if self.fail_branch:raise ValueError('Remote response lost')
        return {'branch':branch,'sha':self.branch}
    def find_publication(self,target,branch,expected,**kwargs):
        return self.pr
    def create_draft(self,repository,base,head,title,body,**kwargs):
        self.calls.append('pr')
        self.pr={'number':1,'url':'https://github.com/owner/repo/pull/1','draft':True,'state':'open','head':head,'base':base,'commit':COMMIT}
        if self.fail_pr:raise ValueError('Remote response lost')
        return self.pr
    def api(self,method,endpoint,payload,**kwargs):
        assert method=='GET'
        if not self.branch:
            from apishield.github_cli import GitHubError
            raise GitHubError('not found',404)
        return {'object':{'sha':self.branch}}


@pytest.fixture
def publishing(tmp_path,monkeypatch):
    from apishield.publication import PublicationService
    from apishield.publication_prepare import evidence_hash
    config=load_config(configured_source(tmp_path))
    store=JobStore(tmp_path/'jobs');job=store.create(config,'repair')
    job._initial['integration']='parcel'
    (job.path/'candidate.patch').write_bytes(PATCH)
    job._source_metadata={'source_commit':SHA}
    job.finish({'status':'validated','patch':'candidate.patch','patch_sha256':hashlib.sha256(PATCH).hexdigest(),'impacted_sites':[{'file':'src/client.py'}]})
    jobs=SimpleNamespace(store=store,integrations={'parcel':str(config.path)},executor=ThreadPoolExecutor(max_workers=2),closed=False)
    github=GitHub();service=PublicationService(jobs,github)
    def prepare(store,job_id,check=None,*,verification_job_id=None):
        if check:check()
        verification=store.create(config,'repair',job_id=verification_job_id)
        (verification.path/'candidate.patch').write_bytes(PATCH)
        atomic_json(verification.path/'source.json',{'source_commit':SHA})
        verification.finish({'status':'validated','patch':'candidate.patch','patch_sha256':hashlib.sha256(PATCH).hexdigest(),'requirement_outcomes':[]})
        content='A = 2\n';data=content.encode()
        return {'source_job_id':job_id,'verification_job_id':verification.id,'source_commit':SHA,
            'patch_sha256':hashlib.sha256(PATCH).hexdigest(),'patch':PATCH.decode(),
            'files':[{'path':'src/client.py','content':content,'mode':'100644','blob_sha':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}],
            'evidence_sha256':evidence_hash(store,verification.id),'validation':{'status':'validated','test_commands':1,'requirements':[],'model_connection':None}}
    monkeypatch.setattr('apishield.publication.prepare_repair',prepare)
    service.configure('parcel','owner/repo','main',0)
    yield service,github,job,jobs
    service.close();jobs.executor.shutdown(wait=True,cancel_futures=True)


def wait(service,identity,statuses=('ready','published','failed','stale','reconciliation_needed','cancelled')):
    deadline=time.monotonic()+8
    while time.monotonic()<deadline:
        record=service.store.read(identity)
        if record['status'] in statuses:return record
        time.sleep(0.02)
    raise AssertionError('Publication did not reach a terminal/prepared state')


def ready(publishing):
    service,github,job,jobs=publishing
    initial=service.prepare('parcel',job.id,1)
    return wait(service,initial['id'])


def test_prepare_is_read_only_and_publish_is_complete_and_deduplicated(publishing):
    service,github,job,jobs=publishing;original=(job.path/'result.json').read_bytes()
    proposal=ready(publishing)
    assert proposal['status']=='ready' and github.calls==[]
    assert 'GitHub CI: not verified' in proposal['body']
    service.publish(proposal['id'],1)
    final=wait(service,proposal['id'],('published','failed','stale','reconciliation_needed'))
    assert final['status']=='published'
    assert github.calls==['commit','branch','pr']
    assert service.publish(proposal['id'],1)['publication']['number']==1
    assert github.calls.count('pr')==1 and (job.path/'result.json').read_bytes()==original


@pytest.mark.parametrize('changed',['patch','verification','target','base'])
def test_changed_preview_inputs_never_write(publishing,changed):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    if changed=='patch':(job.path/'candidate.patch').write_text('tampered')
    elif changed=='verification':(jobs.store._path(proposal['prepared']['verification_job_id'])/'result.json').write_text('{}')
    elif changed=='target':service.configure('parcel','owner/other','main',1)
    else:github.tip='d'*40
    try:service.publish(proposal['id'],1)
    except ValueError:pass
    if service.store.read(proposal['id'])['status']=='publishing':wait(service,proposal['id'])
    assert github.calls==[]


@pytest.mark.parametrize('phase',['branch','pr'])
def test_accepted_remote_effect_response_loss_reconciles_without_duplicate(publishing,phase):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    github.fail_branch=phase=='branch';github.fail_pr=phase=='pr'
    service.publish(proposal['id'],1)
    uncertain=wait(service,proposal['id'],('reconciliation_needed','failed'))
    assert uncertain['status']=='reconciliation_needed'
    github.fail_branch=github.fail_pr=False
    service.reconcile(proposal['id'])
    reconciled=wait(service,proposal['id'])
    if phase=='branch':
        assert reconciled['status']=='ready'
        service.publish(proposal['id'],1);reconciled=wait(service,proposal['id'],('published','failed'))
    assert reconciled['status']=='published' and github.calls.count('pr')==1


def test_base_advances_after_commit_preserves_partial_effects(publishing):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    github.move_after_commit=True
    service.publish(proposal['id'],1)
    final=wait(service,proposal['id'],('stale','failed','reconciliation_needed'))
    assert final['status']=='stale' and final['commit']['sha']==COMMIT
    assert github.calls==['commit']


def test_collision_never_overwrites_existing_branch(publishing):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    github.branch='f'*40
    service.publish(proposal['id'],1)
    final=wait(service,proposal['id'],('failed','reconciliation_needed'))
    assert 'collision' in final['error'] and github.branch=='f'*40 and github.calls==[]


def test_target_change_during_preparation_cannot_install_old_preview(publishing,monkeypatch):
    import apishield.publication as module
    service,github,job,jobs=publishing;original=module.prepare_repair
    started=threading.Event();release=threading.Event()
    def blocked(*args,**kwargs):
        started.set();assert release.wait(5);return original(*args,**kwargs)
    monkeypatch.setattr(module,'prepare_repair',blocked)
    proposal=service.prepare('parcel',job.id,1);assert started.wait(5)
    service.configure('parcel','owner/other','main',1);release.set()
    assert wait(service,proposal['id'])['status']=='stale'


def test_restart_keeps_interrupted_publication_uncertain(publishing):
    from apishield.publication import PublicationService
    service,github,job,jobs=publishing;proposal=ready(publishing)
    with service.store.transaction(proposal['id']) as state:state.update(status='publishing',phase='draft_pr',commit={'sha':COMMIT,'tree':TREE,'parent':SHA})
    restarted=PublicationService(jobs,github)
    assert restarted.store.read(proposal['id'])['status']=='reconciliation_needed'
    assert github.calls==[]
    restarted.close()


def test_same_target_reconfiguration_can_prepare_current_revision(publishing):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    service.configure('parcel','owner/repo','main',1)
    service.prepare('parcel',job.id,2)
    updated=wait(service,proposal['id'])
    assert updated['status']=='ready' and updated['target_revision']==2


def test_verification_identity_reserved_before_construction(publishing,monkeypatch):
    import apishield.publication as module
    service,github,job,jobs=publishing;original=module.prepare_repair
    def reserved(store,job_id,check=None,verification_job_id=None):
        assert verification_job_id is not None
        state=service.store.list()[0]
        assert state['verification_job_id']==verification_job_id
        return original(store,job_id,check,verification_job_id=verification_job_id)
    monkeypatch.setattr(module,'prepare_repair',reserved)
    assert ready(publishing)['status']=='ready'


def test_simultaneous_publish_requests_have_one_owner(publishing,monkeypatch):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    started=threading.Event();release=threading.Event();original=github.create_source_commit
    def blocked(*args,**kwargs):
        started.set();assert release.wait(5);return original(*args,**kwargs)
    monkeypatch.setattr(github,'create_source_commit',blocked)
    service.publish(proposal['id'],1);assert started.wait(5)
    assert service.publish(proposal['id'],1)['status']=='publishing'
    release.set()
    assert wait(service,proposal['id'],('published','failed','reconciliation_needed'))['status']=='published'
    assert github.calls==['commit','branch','pr']


def test_pr_summary_omits_unsafe_metadata():
    from apishield.publication import _summary
    prepared={'files':[{'path':'src/client.py'}],'source_commit':SHA,'patch_sha256':'d'*64,
        'source_job_id':'1'*32,'verification_job_id':'2'*32,
        'validation':{'test_commands':1,'requirements':[{'id':'rule','description':'Fixes https://github.com/owner/repo/issues/7. Keep C:/Users/private/config.json api_key=PRIVATE-KEY',
                      'status':'passed','checks':['tests/test_rule.py::test_rule']}],'model_connection':None}}
    title,body=_summary(prepared,'e'*64,{})
    assert 'Fixes https://' not in body and 'C:/Users' not in body and 'PRIVATE-KEY' not in body
    assert 'GitHub CI: not verified' in body


def test_restart_recovers_reserved_verification_and_cleans_copy(publishing):
    from apishield.publication import PublicationService
    service,github,job,jobs=publishing;proposal=ready(publishing)
    verification=jobs.store.create(job.config,'repair')
    (verification.workspace/'temporary.py').write_text('VALUE=1')
    with service.store.transaction(proposal['id']) as state:
        state.update(status='preparing',verification_job_id=verification.id)
    restarted=PublicationService(jobs,github)
    assert jobs.store.get(verification.id)['status']=='failed'
    assert not verification.workspace.exists()
    assert restarted.store.read(proposal['id'])['status']=='failed'
    restarted.close()


def test_previous_preview_revision_cannot_publish_reprepared_body(publishing):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    service.prepare('parcel',job.id,1)
    newer=wait(service,proposal['id'])
    assert newer['revision']>proposal['revision']
    with pytest.raises(ValueError,match='revision'):service.publish(proposal['id'],proposal['revision'])
    assert github.calls==[]


def test_old_approval_cannot_publish_replacement_during_reservation(publishing,monkeypatch):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    validated=threading.Event();release=threading.Event();original=service._queue
    def pause(identity,operation,*args,**kwargs):
        if operation=='publish':
            validated.set();assert release.wait(5)
        return original(identity,operation,*args,**kwargs)
    monkeypatch.setattr(service,'_queue',pause)
    with ThreadPoolExecutor(max_workers=1) as requests:
        old=requests.submit(service.publish,proposal['id'],proposal['revision'])
        assert validated.wait(5)
        service.prepare('parcel',job.id,1)
        replacement=wait(service,proposal['id'])
        assert replacement['revision']>proposal['revision']
        release.set()
        with pytest.raises(ValueError,match='revision'):old.result(timeout=5)
    assert github.calls==[]
    assert service.store.read(proposal['id'])['status']=='ready'


@pytest.mark.parametrize('snapshot',['base.json','target.json'])
def test_changed_verification_contract_blocks_publication(publishing,snapshot):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    root=jobs.store._path(proposal['prepared']['verification_job_id'])
    (root/'contracts'/snapshot).write_text('{"changed":true}')
    with pytest.raises(ValueError,match='evidence|contract'):service.publish(proposal['id'],proposal['revision'])
    assert github.calls==[]


@pytest.mark.parametrize('state',['closed','merged'])
def test_reconcile_recovers_accepted_pr_without_branch_and_with_advanced_base(publishing,state):
    service,github,job,jobs=publishing;proposal=ready(publishing)
    github.fail_pr=True;service.publish(proposal['id'],proposal['revision'])
    assert wait(service,proposal['id'],('reconciliation_needed',))['status']=='reconciliation_needed'
    github.branch=None;github.tip='e'*40;github.pr.update(state=state,draft=False)
    calls=list(github.calls)
    service.reconcile(proposal['id'])
    recovered=wait(service,proposal['id'])
    assert recovered['status']=='published'
    assert recovered['publication']['url']==github.pr['url']
    assert recovered['publication']['state']==state
    assert github.calls==calls
