import pytest


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
