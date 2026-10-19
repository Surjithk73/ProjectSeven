"""Exact-revision GitHub merge and CI evidence, without merge permissions."""
import time
from .github_cli import GhClient, repository_name, sha


def classify_merge(pr, checks, expected_head):
    if pr.get('head', {}).get('sha') != sha(expected_head):
        raise ValueError('PR head changed after validation; regenerate the update')
    if not pr.get('merged'):
        return {'state': 'closed' if pr.get('state') == 'closed' else 'pr_open', 'merge_sha': None}
    merged = sha(pr.get('merge_commit_sha'))
    matching = [c for c in checks if c.get('head_sha') == merged and c.get('name') == 'cinema-client']
    matching.sort(key=lambda c: c.get('id', 0), reverse=True)
    if not matching or matching[0].get('status') != 'completed':
        return {'state': 'awaiting_ci', 'merge_sha': merged}
    return {'state': 'merged' if matching[0].get('conclusion') == 'success' else 'ci_failed', 'merge_sha': merged}


def reconcile_publication(record, github=None):
    client = github or GhClient()
    repo = repository_name(record['target']['repository'])
    number = record['publication']['number']
    deadline = time.monotonic() + 40
    pr = client.api('GET', f'repos/{repo}/pulls/{number}', None, deadline=deadline)
    if pr.get('base', {}).get('ref') != record['target']['base']:
        raise ValueError('PR target branch changed')
    checks = []
    if pr.get('merged'):
        merged = sha(pr['merge_commit_sha'])
        checks = client.api('GET', f'repos/{repo}/commits/{merged}/check-runs?per_page=100', None, deadline=deadline).get('check_runs', [])
    return {**classify_merge(pr, checks, record['commit']['sha']), 'pr_url': pr['html_url']}
