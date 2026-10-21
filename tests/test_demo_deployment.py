import pytest


def test_windows_redirector_uses_serving_pid_and_checks_instance(monkeypatch):
    from demo.deployment.agent import DeploymentAgent
    import demo.deployment.agent as module
    agent = object.__new__(DeploymentAgent)
    agent.children = {}
    agent.url = 'http://127.0.0.1:8100'
    active = {'pid': 101, 'server_pid': 202, 'instance': 'owned', 'sha': 'a'*40}
    class Response:
        def json(self):
            return {'pid': 202, 'instance': 'owned', 'revision': 'a'*40}
    monkeypatch.setattr(module.httpx, 'get', lambda *a, **kw: Response())
    killed = []
    monkeypatch.setattr(module.os, 'kill', lambda pid, signal: killed.append(pid))
    monkeypatch.setattr(module.time, 'sleep', lambda seconds: None)
    agent.stop(active)
    assert killed == [202]
    with pytest.raises(ValueError, match='identity'):
        agent.stop({**active, 'instance': 'unrelated'})
    assert killed == [202]


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
            return [] if '/statuses?' in endpoint else {'statuses': []}
    assert read_receipt(Fake(), 'owner/repo', 1, 'b'*40, 'surjk73') is None


def test_receipt_uses_individual_statuses_to_verify_publisher_identity():
    import json
    from demo.deployment.receipt import read_receipt, digest, MARKER
    receipt = {'version':1,'status':'verified','deployed_sha':'b'*40}
    class GitHub:
        def api(self, method, endpoint, payload, **kwargs):
            if '/comments?' in endpoint:
                return [{'user':{'login':'owner'},'body':MARKER+json.dumps(receipt)}]
            status = {'id':1,'context':'apishield/deployment','description':'receipt-sha256:'+digest(receipt)}
            if '/statuses?' in endpoint:
                return [{**status,'creator':{'login':'owner'}}]
            # GitHub's combined status response does not include creator.
            return {'statuses':[status]}
    assert read_receipt(GitHub(), 'owner/repo', 6, 'b'*40, 'owner') == receipt
    assert read_receipt(GitHub(), 'owner/repo', 6, 'b'*40, 'stranger') is None


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


def test_polling_detects_merge_waits_for_ci_and_deploys_once(tmp_path, monkeypatch):
    import json
    from types import SimpleNamespace
    import demo.deployment.agent as module
    merged = 'b'*40
    workflow = {'repository':'owner/repo','project_id':'cinema','base':'demo/rehearsal',
                'providers':{},'workflow_id':'w1'}
    pr = {'user':{'login':'owner'},'base':{'ref':'demo/rehearsal'},'number':1,
          'state':'closed','merged':True,'merged_at':'2026-10-20T14:45:35Z',
          'head':{'sha':'a'*40},'merge_commit_sha':merged,
          'body':'<!-- APIShield workflow '+json.dumps(workflow)+' -->\n<!-- APIShield candidate '+'a'*40+' -->'}
    checks = []
    class GitHub:
        def api(self, method, endpoint, payload, **kwargs):
            if '/pulls?' in endpoint:
                return [pr]
            if '/pulls/1' in endpoint:
                return pr
            if '/git/ref/' in endpoint:
                return {'object':{'sha':merged}}
            if '/check-runs?' in endpoint:
                return {'check_runs':checks}
            raise AssertionError(endpoint)
    agent = object.__new__(module.DeploymentAgent)
    agent.config = {**workflow,'publisher':'owner','deployment_actor':'owner'}
    agent.github = GitHub()
    agent.receipts = tmp_path/'receipts.json'
    deployed, published = [], []
    def deploy(revision):
        deployed.append(revision)
        return {'status':'verified','deployed_sha':revision,'health_passed':True,'smoke_passed':True}
    agent.manager = SimpleNamespace(deploy=deploy)
    agent.provider_hashes = lambda workflow: {}
    monkeypatch.setattr(module,'publish_receipt',lambda *args:published.append(args))
    assert agent.tick() is None
    assert deployed == []
    checks.append({'name':'cinema-client','head_sha':merged,'status':'completed','conclusion':'success'})
    assert agent.tick()['status'] == 'verified'
    assert agent.tick() is None
    assert deployed == [merged] and len(published) == 1
