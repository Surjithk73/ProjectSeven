"""Deployment receipts are bound to a GitHub identity, commit and workflow."""
import hashlib
import json
import time

from apishield.github_cli import GhClient, repository_name, sha

MARKER = '<!-- APIShield deployment -->\n'


def digest(receipt):
    return hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def receipt_identity_matches(receipt, workflow, merge_sha, provider_hashes):
    return (isinstance(receipt, dict) and receipt.get('version') == 1 and receipt.get('workflow_id') == workflow['workflow_id']
        and receipt.get('project_id') == workflow['project_id'] and receipt.get('deployed_sha') == merge_sha
        and receipt.get('provider_hashes') == provider_hashes)


def verify_receipt(receipt, workflow, merge_sha, provider_hashes):
    return (receipt_identity_matches(receipt, workflow, merge_sha, provider_hashes) and receipt.get('status') == 'verified'
            and receipt.get('health_passed') is True and receipt.get('smoke_passed') is True)


def publish_receipt(github, repository, number, merge_sha, receipt, actor):
    client = github or GhClient()
    repo = repository_name(repository)
    deadline = time.monotonic() + 45
    user = client.api('GET', 'user', None, deadline=deadline)
    if user['login'].casefold() != actor.casefold():
        raise ValueError('Deployment GitHub login differs from the configured receipt author')
    body = MARKER + json.dumps(receipt, sort_keys=True, separators=(',', ':'))
    if len(body) > 16000:
        raise ValueError('Deployment receipt exceeds its evidence budget')
    client.api('POST', f'repos/{repo}/issues/{int(number)}/comments', {'body': body}, deadline=deadline)
    client.api('POST', f'repos/{repo}/statuses/{sha(merge_sha)}', {
        'context': 'apishield/deployment', 'state': 'success' if receipt['status'] == 'verified' else 'failure',
        'description': 'receipt-sha256:' + digest(receipt)}, deadline=deadline)


def read_receipt(github, repository, number, merge_sha, actor):
    if not actor:
        return None
    client = github or GhClient()
    repo = repository_name(repository)
    deadline = time.monotonic() + 40
    comments = client.api('GET', f'repos/{repo}/issues/{int(number)}/comments?per_page=100', None, deadline=deadline)
    status = client.api('GET', f'repos/{repo}/commits/{sha(merge_sha)}/status', None, deadline=deadline)
    contexts = [s for s in status.get('statuses', []) if s.get('context') == 'apishield/deployment'
                and s.get('creator', {}).get('login', '').casefold() == actor.casefold()]
    if not contexts:
        return None
    contexts.sort(key=lambda s: s.get('id', 0), reverse=True)
    for comment in reversed(comments):
        body = comment.get('body', '')
        if comment.get('user', {}).get('login', '').casefold() != actor.casefold() or not body.startswith(MARKER) or len(body) > 16000:
            continue
        try:
            receipt = json.loads(body[len(MARKER):])
        except ValueError:
            continue
        if contexts[0].get('description') == 'receipt-sha256:' + digest(receipt):
            return receipt
    return None
