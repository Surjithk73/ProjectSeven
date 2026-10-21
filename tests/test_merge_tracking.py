import pytest


def test_github_response_contract_retains_merged_revision_for_tracking(monkeypatch):
    import json
    from apishield.github_cli import GhClient
    from apishield.merge_tracking import reconcile_publication
    pr = {'state':'closed','merged':True,'head':{'sha':'a'*40},
          'base':{'ref':'demo/rehearsal'},'html_url':'https://github.com/owner/repo/pull/6'}
    def run(self, argv, deadline, check=None, files=None):
        if any('/check-runs?' in arg for arg in argv):
            return json.dumps({'check_runs':[{'head_sha':'b'*40,'name':'cinema-client',
                               'status':'completed','conclusion':'success'}]})
        # GitHub's 2026-03-10 pull-request contract removed merge_commit_sha.
        return json.dumps({**pr, **({'merge_commit_sha':'b'*40}
            if 'X-GitHub-Api-Version: 2022-11-28' in argv else {})})
    monkeypatch.setattr(GhClient, '_run', run)
    record = {'target':{'repository':'owner/repo','base':'demo/rehearsal'},
              'publication':{'number':6},'commit':{'sha':'a'*40}}
    result = reconcile_publication(record)
    assert result['state'] == 'merged' and result['merge_sha'] == 'b'*40


def test_merge_requires_expected_head_and_exact_successful_ci():
    from apishield.merge_tracking import classify_merge
    pr = {'state': 'closed', 'merged': True, 'head': {'sha': 'a'*40}, 'merge_commit_sha': 'b'*40}
    checks = [{'head_sha': 'b'*40, 'name': 'cinema-client', 'status': 'completed', 'conclusion': 'success'}]
    assert classify_merge(pr, checks, 'a'*40)['state'] == 'merged'
    assert classify_merge(pr, [{**checks[0], 'head_sha': 'c'*40}], 'a'*40)['state'] == 'awaiting_ci'
    with pytest.raises(ValueError, match='head'):
        classify_merge(pr, checks, 'c'*40)
    assert classify_merge({**pr, 'merged': False}, checks, 'a'*40)['state'] == 'closed'
    assert classify_merge(pr, [{**checks[0], 'conclusion': 'failure'}], 'a'*40)['state'] == 'ci_failed'


def test_publication_side_effect_guard_rejects_superseded_workflow():
    import time
    from types import SimpleNamespace
    from apishield.publication import PublicationService
    from apishield.publication_state import PublicationConflict
    publisher=PublicationService.__new__(PublicationService)
    publisher.closed=False
    publisher.jobs=SimpleNamespace(closed=False,store=SimpleNamespace(get=lambda job:{'project_workflow':{'project_id':'cinema','workflow_id':'w1','providers':{}}}),
        automation=SimpleNamespace(projects=SimpleNamespace(workflows=lambda project:[{'workflow_id':'w1','state':'superseded'}])))
    publisher.store=SimpleNamespace(read=lambda identity:{'cancel_requested':False})
    publisher._target=lambda record: None
    with pytest.raises(PublicationConflict,match='superseded'):
        publisher._check({'id':'p1','source_job_id':'j1'},time.monotonic()+10)
