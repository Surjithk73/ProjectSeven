import pytest


def test_receipt_requires_exact_revision_provider_hashes_and_smoke():
    from demo.deployment.receipt import verify_receipt
    workflow = {'workflow_id': 'w1', 'project_id': 'cinema'}
    hashes = {'payment': 'a'*64}
    receipt = {'version': 1, 'workflow_id': 'w1', 'project_id': 'cinema', 'deployed_sha': 'b'*40,
               'status': 'verified', 'provider_hashes': hashes, 'health_passed': True, 'smoke_passed': True}
    assert verify_receipt(receipt, workflow, 'b'*40, hashes)
    assert not verify_receipt({**receipt, 'deployed_sha': 'c'*40}, workflow, 'b'*40, hashes)
    assert not verify_receipt({**receipt, 'smoke_passed': False}, workflow, 'b'*40, hashes)
    assert not verify_receipt(receipt, workflow, 'b'*40, {'payment': 'c'*64})


def test_failed_release_rolls_back_and_never_reports_verified(tmp_path):
    from demo.deployment.release import ReleaseManager
    history = []
    def prepare(revision, path):
        path.mkdir(parents=True, exist_ok=True)
    def start(revision, path):
        history.append(('start', revision))
        return {'pid': 123, 'instance': revision}
    manager = ReleaseManager(tmp_path / 'releases', prepare, start, lambda active: history.append(('stop', active['sha'])),
                             lambda active: active['sha'] != 'b'*40)
    assert manager.deploy('a'*40)['status'] == 'verified'
    failed = manager.deploy('b'*40)
    assert failed['status'] == 'failed' and failed['rollback_sha'] == 'a'*40
    assert manager.state()['active']['sha'] == 'a'*40
    assert history[-1] == ('start', 'a'*40)
    assert manager.deploy('a'*40)['status'] == 'already_deployed'
    with pytest.raises(ValueError):
        manager.deploy('../../outside')


def test_deployment_root_requires_empty_or_managed_directory(tmp_path):
    from demo.deployment.release import ReleaseManager
    (tmp_path / 'personal.txt').write_text('keep me')
    with pytest.raises(ValueError, match='managed'):
        ReleaseManager(tmp_path, None, None, None, None)
    assert (tmp_path / 'personal.txt').read_text() == 'keep me'


def test_unexpected_author_receipt_is_not_trusted():
    from demo.deployment.receipt import read_receipt
    class Fake:
        def api(self, method, endpoint, payload, **kwargs):
            if '/comments' in endpoint:
                return [{'user': {'login': 'stranger'}, 'body': '<!-- APIShield deployment -->\n{}'}]
            return {'statuses': []}
    assert read_receipt(Fake(), 'owner/repo', 1, 'b'*40, 'surjk73') is None


def test_candidate_requires_original_validated_head_and_merged_ci():
    import json
    from demo.deployment.agent import candidate_from_pr
    config = {'repository':'owner/repo','publisher':'owner','project_id':'cinema','base':'main'}
    workflow = {'repository':'owner/repo','project_id':'cinema','base':'main','providers':{},'workflow_id':'w1'}
    body = '<!-- APIShield workflow ' + json.dumps(workflow) + ' -->\n<!-- APIShield candidate ' + 'a'*40 + ' -->'
    pr = {'user':{'login':'owner'},'base':{'ref':'main'},'body':body,'number':1,'state':'closed','merged':True,
          'head':{'sha':'a'*40},'merge_commit_sha':'b'*40}
    checks = [{'name':'cinema-client','head_sha':'b'*40,'status':'completed','conclusion':'success'}]
    assert candidate_from_pr(pr,checks,config)['merge_sha'] == 'b'*40
    assert candidate_from_pr({**pr,'merged':False},checks,config) is None
    with pytest.raises(ValueError,match='head'):
        candidate_from_pr({**pr,'head':{'sha':'c'*40}},checks,config)
