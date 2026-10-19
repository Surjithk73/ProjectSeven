import hashlib
import json

import pytest

from test_local_engine import shipment,run,git,load_config,SOURCE
from apishield.jobs import atomic_json


def test_validated_patch_has_creation_digest(shipment):
    result=run(shipment)
    patch=(shipment[3]._path(result['job_id'])/'candidate.patch').read_bytes()
    assert result['patch_sha256']==hashlib.sha256(patch).hexdigest()
    assert result['proposal_source']=='offline'


def test_two_file_offline_revalidation_preserves_source_and_original_result(shipment,monkeypatch):
    from apishield.publication_prepare import prepare_repair
    repo,path,candidate,store,_=shipment
    (repo/'src/second.py').write_text(SOURCE)
    git(repo,'add','.');git(repo,'-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-m','Second source')
    value=json.loads(candidate.read_text());value['patches'].append({**value['patches'][0],'file':'src/second.py'})
    candidate.write_text(json.dumps(value))
    result=run(shipment);original=(store._path(result['job_id'])/'result.json').read_bytes()
    source={name:(repo/name).read_bytes() for name in ['src/client.py','src/second.py']}
    monkeypatch.setattr('apishield.engine.generate_candidate',lambda *args,**kwargs:pytest.fail('Offline preparation must never infer'))
    prepared=prepare_repair(store,result['job_id'])
    assert [item['path'] for item in prepared['files']]==sorted(source)
    assert prepared['verification_job_id']!=result['job_id']
    assert store.get(prepared['verification_job_id'])['status']=='validated'
    assert prepared['source_commit']==result['source_commit']
    assert prepared['patch_sha256']==result['patch_sha256']
    assert all((repo/name).read_bytes()==content for name,content in source.items())
    assert (store._path(result['job_id'])/'result.json').read_bytes()==original
    assert not (store._path(prepared['verification_job_id'])/'workspace').exists()


@pytest.mark.parametrize('kind',['tampered','digestless','failed'])
def test_preparation_rejects_tampered_or_digestless_artifact(shipment,kind):
    from apishield.publication_prepare import prepare_repair
    result=run(shipment);store=shipment[3];root=store._path(result['job_id'])
    if kind=='tampered': (root/'candidate.patch').write_text('tampered')
    elif kind=='digestless': result.pop('patch_sha256');atomic_json(root/'result.json',result)
    else: result['status']='failed';atomic_json(root/'result.json',result)
    with pytest.raises(ValueError):prepare_repair(store,result['job_id'])


@pytest.mark.parametrize('patch',[
    '--- a/tests/test_shipping.py\n+++ b/tests/test_shipping.py\n@@ -1 +1 @@\n-import httpx\n+pass\n',
    '--- /dev/null\n+++ b/src/new.py\n@@ -0,0 +1 @@\n+VALUE = 1\n',
    '--- a/src/unrelated.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-VALUE = 1\n',
    '--- a/../escape.py\n+++ b/../escape.py\n@@ -1 +1 @@\n-a\n+b\n',
    'diff --git a/src/client.py b/src/client.py\nold mode 100644\nnew mode 120000\n',
    'diff --git a/src/client.py b/src/renamed.py\nsimilarity index 100%\nrename from src/client.py\nrename to src/renamed.py\n',
    'diff --git a/src/client.py b/src/client.py\nGIT binary patch\nliteral 1\nAc\n',
    '',
])
def test_only_allowed_existing_python_changes(shipment,patch):
    from apishield.publication_prepare import prepare_repair
    result=run(shipment);store=shipment[3];root=store._path(result['job_id'])
    (root/'candidate.patch').write_bytes(patch.encode())
    result['patch_sha256']=hashlib.sha256(patch.encode()).hexdigest();atomic_json(root/'result.json',result)
    with pytest.raises(ValueError):prepare_repair(store,result['job_id'])


def test_failed_requirement_check_blocks_preparation(shipment,monkeypatch):
    from apishield.publication_prepare import prepare_repair
    from apishield import engine
    result=run(shipment)
    def fail(config,operation,store,**kwargs):
        kwargs['job'].finish({'status':'failed','error':'Requirement check failed'})
        kwargs['job'].cleanup()
        return store.get(kwargs['job'].id)
    monkeypatch.setattr(engine,'run_job',fail)
    with pytest.raises(ValueError,match='revalidation'):prepare_repair(shipment[3],result['job_id'])


def test_private_key_marker_never_ready(shipment):
    from apishield.publication_prepare import prepare_repair
    repo,path,candidate,store,_=shipment
    value=json.loads(candidate.read_text())
    value['patches'][0]['new_code_snippet']='(f"{BASE}/shipments/create"\n # PRIVATE KEY-----\n)'
    candidate.write_text(json.dumps(value))
    result=run(shipment)
    assert result['status']=='validated'
    with pytest.raises(ValueError,match='secret'):prepare_repair(store,result['job_id'])


def test_external_cancel_reaches_verification_command_loop(shipment,monkeypatch):
    from apishield.publication_prepare import prepare_repair
    from apishield.jobs import JobCancelled
    result=run(shipment);cancelled=[False]
    def check():
        if cancelled[0]:raise JobCancelled('Preparation cancelled')
    def run_job(config,operation,store,**kwargs):
        cancelled[0]=True
        kwargs['job'].cancelled()
        pytest.fail('Verification did not observe cancellation')
    monkeypatch.setattr('apishield.engine.run_job',run_job)
    with pytest.raises(JobCancelled):prepare_repair(shipment[3],result['job_id'],check)
    verification=[item for item in shipment[3].list_jobs() if item['job_id']!=result['job_id']]
    assert len(verification)==1 and verification[0]['status']=='cancelled'
