"""Offline adapter checks; no GitHub requests or credentials are used."""
import runpy
import sys
from types import SimpleNamespace

import pytest

import config
from mcp_server import github_editor as editor


class CheckRuns(list):
    @property
    def totalCount(self):
        return len(self)


class Repository:
    default_branch = 'main'

    def __init__(self, checks=()):
        self.checks = CheckRuns(checks)
        self.publications = []
        self.updated = []

    def get_git_ref(self, ref):
        return SimpleNamespace(object=SimpleNamespace(sha='base-sha'))

    def create_git_ref(self, **kwargs):
        return None

    def get_contents(self, path, **kwargs):
        return SimpleNamespace(path=path, sha='file-sha')

    def update_file(self, path, message, content, sha, **kwargs):
        self.updated.append((path, content))

    def create_pull(self, **kwargs):
        self.publications.append(kwargs)
        return SimpleNamespace(html_url='https://github.com/example/demo/pull/1', number=1)

    def get_pull(self, number):
        return SimpleNamespace(head=SimpleNamespace(sha='candidate-sha'), mergeable=True, state='open')

    def get_commit(self, sha):
        return SimpleNamespace(get_check_runs=lambda: self.checks)


@pytest.fixture
def github(monkeypatch):
    repository = Repository()
    calls = []
    class Client:
        def __init__(self, token):
            calls.append(('token', token))
        def get_repo(self, name):
            calls.append(('repo', name))
            return repository
    monkeypatch.setattr(editor, 'Github', Client)
    monkeypatch.setenv('GITHUB_TOKEN', 'environment-token')
    monkeypatch.setenv('GITHUB_REPO', 'environment/repository')
    monkeypatch.setattr(config, 'dotenv_values', lambda *args: {'GITHUB_TOKEN': 'dotenv-token', 'GITHUB_REPO': 'dotenv/repository'})
    if hasattr(editor, 'dotenv_values'):
        monkeypatch.setattr(editor, 'dotenv_values', lambda *args: {'GITHUB_TOKEN': 'dotenv-token', 'GITHUB_REPO': 'dotenv/repository'})
    return repository, calls


def test_publication_uses_environment_over_dotenv_credentials(github):
    repository, calls = github
    result = editor.apply_github_patch('client_app/service.py', 'value = 2\n', 'Collect payment', 7)
    assert result['status'] == 'success'
    assert calls == [('token', 'environment-token'), ('repo', 'environment/repository')]
    assert repository.updated == [('service.py', 'value = 2\n')]


def test_publication_is_draft_and_reports_missing_ips(github):
    repository, _ = github
    result = editor.apply_github_patch('client_app/service.py', 'value = 2\n', 'Collect payment', None)
    assert result['status'] == 'success'
    proposal = repository.publications[0]
    assert proposal.get('draft') is True
    assert 'Intent Preservation Score: unavailable' in proposal['body']
    assert 'None/100' not in proposal['body']
    assert 'CI: Pending' in proposal['body']


def test_publication_keeps_real_low_ips(github):
    repository, _ = github
    editor.apply_github_patch('client_app/service.py', 'value = 2\n', 'Collect payment', 7)
    assert 'Intent Preservation Score: 7/100' in repository.publications[0]['body']


def test_missing_ci_is_not_passing_evidence(github):
    result = editor.get_pr_status(1)
    assert result['status'] == 'success'
    assert result['checks'] == []
    assert result['all_checks_passed'] is False
    assert result['any_pending'] is False
    assert result['ci_evidence'] == 'unavailable'


@pytest.mark.parametrize('checks,want_pass,want_pending', [
    ([SimpleNamespace(name='tests', status='completed', conclusion='success')], True, False),
    ([SimpleNamespace(name='tests', status='completed', conclusion='failure')], False, False),
    ([SimpleNamespace(name='tests', status='in_progress', conclusion=None)], False, True),
])
def test_ci_state_reflects_actual_checks(github, checks, want_pass, want_pending):
    repository, _ = github
    repository.checks.extend(checks)
    result = editor.get_pr_status(1)
    assert result['all_checks_passed'] is want_pass
    assert result['any_pending'] is want_pending
    assert result['ci_evidence'] == 'available'


def test_github_functions_stay_callable_with_tool_returning_decorator(monkeypatch):
    class MCP:
        def __init__(self, *args):
            pass
        def tool(self):
            return lambda fn: object()
    monkeypatch.setitem(sys.modules, 'fastmcp', SimpleNamespace(FastMCP=MCP))
    namespace = runpy.run_path(editor.__file__)
    assert callable(namespace['apply_github_patch'])
    assert callable(namespace['get_pr_status'])
    assert callable(namespace['merge_pr'])
