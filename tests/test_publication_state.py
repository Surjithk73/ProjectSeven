import json
import subprocess
import sys

import pytest


def test_target_revision_conflict_and_safe_identity(tmp_path):
    from apishield.publication_state import PublicationStore,PublicationConflict
    store=PublicationStore(tmp_path)
    assert store.read_target('parcel')['revision']==0
    target={'repository':'owner/repo','base':'main','account':{'login':'fixture','id':7}}
    saved=store.save_target('parcel',target,0)
    assert saved['revision']==1 and saved['configured']
    with pytest.raises(PublicationConflict):store.save_target('parcel',target,0)
    assert PublicationStore(tmp_path).read_target('parcel')==saved
    for name in ['../escape','a/b','CON','']:
        with pytest.raises(ValueError):store.read_target(name)
    with pytest.raises(ValueError):store.read('../escape')


def test_proposal_identity_deduplicates_and_os_ownership_spans_processes(tmp_path):
    from apishield.publication_state import PublicationStore,proposal_identity
    identity=proposal_identity('owner/repo','main','a'*40,'b'*64)
    assert identity==proposal_identity('OWNER/REPO','main','a'*40,'b'*64)
    store=PublicationStore(tmp_path)
    store.reserve(identity,{'id':identity,'version':1,'status':'preparing'})
    assert store.reserve(identity,{'id':identity,'version':1,'status':'ready'})['status']=='preparing'
    with store.ownership(identity) as owned:
        assert owned
        child=subprocess.run([sys.executable,'-B','-c',
            'import sys;from apishield.publication_state import PublicationStore; s=PublicationStore(sys.argv[1]);\nwith s.ownership(sys.argv[2]) as owned: print(owned)',
            str(tmp_path),identity],capture_output=True,text=True,timeout=30)
        assert child.returncode==0,child.stderr
        assert child.stdout.strip()=='False'
    with store.ownership(identity) as owned:assert owned


def test_malformed_and_symlink_state_rejected(tmp_path):
    from apishield.publication_state import PublicationStore
    store=PublicationStore(tmp_path)
    identity='c'*64
    store.reserve(identity,{'id':identity,'version':1,'status':'ready'})
    (store.directory(identity)/'state.json').write_text('not JSON')
    with pytest.raises(ValueError,match='Malformed'):store.read(identity)
