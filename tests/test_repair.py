import json
from pathlib import Path

import pytest

from agent import langgraph_loop as loop
from agent import monitor, planner
from mcp_server import file_editor as editor


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    root = tmp_path / 'client_app'
    root.mkdir()
    monkeypatch.setattr(editor, 'CLIENT_ROOT', root, raising=False)
    monkeypatch.setattr(loop, 'log_reasoning', lambda *args, **kwargs: None)
    return root


def plan(path, old='value = 1', new='value = 2'):
    return {'file': str(path), 'old_code_snippet': old, 'new_code_snippet': new}


@pytest.mark.parametrize('old,new', [('', 'x'), ('value = 1', 'value = 1'), ('value = 1', 'def broken('), ('value = 1', '')])
def test_editor_rejects_unsafe_patch_without_writing(workspace, old, new):
    path = workspace / 'service.py'
    path.write_text('value = 1\n')
    result = editor.apply_patch(str(path), old, new)
    assert result.startswith('Error')
    assert path.read_text() == 'value = 1\n'


def test_editor_rejects_ambiguous_match(workspace):
    path = workspace / 'service.py'
    path.write_text('value = 1\nvalue = 1\n')
    assert editor.apply_patch(str(path), 'value = 1', 'value = 2').startswith('Error')
    assert path.read_text() == 'value = 1\nvalue = 1\n'


def test_editor_rejects_traversal_even_if_name_contains_client_app(workspace):
    outside = workspace.parent / 'outside_client_app.py'
    outside.write_text('value = 1\n')
    result = editor.apply_patch(str(workspace / '..' / outside.name), 'value = 1', 'value = 2')
    assert result.startswith('Error')
    assert outside.read_text() == 'value = 1\n'


def test_failed_repair_restores_every_file_and_never_publishes(workspace, monkeypatch):
    a, b = workspace / 'a.py', workspace / 'b.py'
    a.write_bytes(b'value = 1\r\n')
    b.write_bytes(b'value = 1\n')
    monkeypatch.setattr(loop, 'run_tests_and_score_ips', lambda **kw: {'tests_passed': False, 'test_output': 'bad', 'ips_score': None, 'ips_error': None})
    monkeypatch.setattr(loop, 'revise_patch_plan', lambda **kw: plan(a))
    def forbidden(**kw):
        pytest.fail('Failed repair must never publish')
    monkeypatch.setattr(loop, 'apply_github_patch', forbidden, raising=False)
    result = loop.execute_node({'patch_plans': [plan(a), plan(b)], 'healing_mode': 'github'})
    assert result['final_status'] == 'failed'
    assert result['attempts'] == 3
    assert a.read_bytes() == b'value = 1\r\n'
    assert b.read_bytes() == b'value = 1\n'


def test_revision_observes_restored_base_and_reapplies_exactly(workspace, monkeypatch):
    path = workspace / 'service.py'
    path.write_text('value = 1\n')
    attempts = []
    def validate(**kw):
        attempts.append(path.read_text())
        return {'tests_passed': len(attempts) == 2, 'test_output': 'retry', 'ips_score': None, 'ips_error': 'unavailable'}
    def revise(**kw):
        assert path.read_text() == kw['target_code'] == 'value = 1\n'
        return plan(path, new='value = 3')
    monkeypatch.setattr(loop, 'run_tests_and_score_ips', validate)
    monkeypatch.setattr(loop, 'revise_patch_plan', revise)
    result = loop.execute_node({'patch_plans': [plan(path)]})
    assert result['final_status'] == 'validated'
    assert attempts == ['value = 2\n', 'value = 3\n']
    assert result['patch_plans'][0]['new_code_snippet'] == 'value = 3'


def test_validation_exception_rolls_back_candidate(workspace, monkeypatch):
    path = workspace / 'service.py'
    path.write_text('value = 1\n')
    monkeypatch.setattr(loop, 'run_tests_and_score_ips', lambda **kw: (_ for _ in ()).throw(RuntimeError('validator unavailable')))
    monkeypatch.setattr(loop, 'revise_patch_plan', lambda **kw: (_ for _ in ()).throw(RuntimeError('planner unavailable')))
    result = loop.execute_node({'patch_plans': [plan(path)]})
    assert result['final_status'] == 'failed'
    assert path.read_text() == 'value = 1\n'


def test_empty_plan_needs_input_without_validation(workspace, monkeypatch):
    monkeypatch.setattr(loop, 'run_tests_and_score_ips', lambda **kw: pytest.fail('Empty plans cannot validate'))
    assert loop.execute_node({'patch_plans': []})['final_status'] == 'needs_input'


def test_overlapping_plans_are_rejected_as_one_transaction(workspace, monkeypatch):
    path = workspace / 'service.py'
    path.write_text('value = 1\nother = 2\n')
    monkeypatch.setattr(loop, 'revise_patch_plan', lambda **kw: (_ for _ in ()).throw(ValueError('no valid revision')))
    monkeypatch.setattr(loop, 'run_tests_and_score_ips', lambda **kw: pytest.fail('Cannot validate overlapping patches'))
    result = loop.execute_node({'patch_plans': [plan(path), plan(path, 'value = 1\nother = 2', 'value = 3')]})
    assert result['final_status'] == 'failed'
    assert path.read_text() == 'value = 1\nother = 2\n'


def test_disjoint_same_file_edits_apply_against_same_original(workspace, monkeypatch):
    path = workspace / 'service.py'
    path.write_text('value = 1\nother = 2\n')
    monkeypatch.setattr(loop, 'run_tests_and_score_ips', lambda **kw: {'tests_passed': True, 'test_output': 'ok', 'ips_score': None, 'ips_error': None})
    result = loop.execute_node({'patch_plans': [plan(path), plan(path, 'other = 2', 'other = 3')]})
    assert result['final_status'] == 'validated'
    assert path.read_text() == 'value = 2\nother = 3\n'


def test_plans_group_current_disk_context_by_file(workspace, monkeypatch):
    path = workspace / 'service.py'
    path.write_text('value = 1\n')
    calls = []
    def generate(*args, **kwargs):
        calls.append((args, kwargs))
        assert args[1] == 'value = 1\n'
        return plan(path)
    monkeypatch.setattr(loop, 'generate_patch_plan', generate)
    result = loop.plan_node({'diff': '[]', 'impacted_sites': [{'file': str(path), 'code': 'stale', 'intent': 'A'}, {'file': str(path), 'code': 'stale', 'intent': 'B'}]})
    assert len(calls) == len(result['patch_plans']) == 1


def test_monitor_errors_are_failed_not_no_change(monkeypatch):
    monkeypatch.setattr(loop, 'get_api_diff', lambda **kw: (_ for _ in ()).throw(RuntimeError('oasdiff unavailable')))
    result = loop.monitor_node({})
    assert result['final_status'] == 'failed'
    assert 'oasdiff unavailable' in result['error']


def test_monitor_does_not_hide_bad_tool_output(monkeypatch):
    monkeypatch.setattr(monitor.subprocess, 'run', lambda *a, **kw: type('Result', (), {'returncode': 2, 'stdout': '', 'stderr': 'tool crashed'})())
    with pytest.raises(RuntimeError, match='tool crashed'):
        monitor.get_api_diff()


def test_blind_initial_and_revision_prompts_do_not_leak_intent(monkeypatch):
    monkeypatch.setenv('USE_SIG_CONTEXT', '0')
    prompts = []
    class Models:
        def generate_content(self, **kwargs):
            prompts.append(kwargs['contents'])
            return type('Response', (), {'text': json.dumps({'old_code_snippet': 'value = 1', 'new_code_snippet': 'value = 2'})})()
    import config
    monkeypatch.setattr(config, 'get_genai_client', lambda: type('Client', (), {'models': Models()})())
    code = 'def charge():\n    """Business Intent: SECRET_INTENT"""\n    value = 1\n'
    planner.generate_patch_plan('[]', code, 'SECRET_INTENT')
    planner.revise_patch_plan({'old_code_snippet': code, 'intent': 'SECRET_INTENT'}, 'SECRET_INTENT leaked in traceback', code, 'SECRET_INTENT')
    assert len(prompts) == 2
    assert all('SECRET_INTENT' not in prompt for prompt in prompts)
    assert all('numeric' in prompt and 'signatures' in prompt for prompt in prompts)


def test_failed_validation_restores_unplanned_file_changes(workspace, monkeypatch):
    path, untouched = workspace / 'service.py', workspace / 'original.txt'
    path.write_text('value = 1\n')
    untouched.write_bytes(b'original\r\n')
    created = workspace / 'created.txt'
    def validate(**kwargs):
        untouched.unlink()
        created.write_text('side effect')
        return {'tests_passed': False, 'test_output': 'failure', 'ips_score': None, 'ips_error': None}
    monkeypatch.setattr(loop, 'run_tests_and_score_ips', validate)
    monkeypatch.setattr(loop, 'revise_patch_plan', lambda **kw: (_ for _ in ()).throw(ValueError('cannot revise')))
    assert loop.execute_node({'patch_plans': [plan(path)]})['final_status'] == 'failed'
    assert untouched.read_bytes() == b'original\r\n'
    assert not created.exists()


def test_multifile_validated_candidate_requires_complete_publisher(workspace, monkeypatch):
    a, b = workspace / 'a.py', workspace / 'b.py'
    for path in (a, b):
        path.write_text('value = 1\n')
    monkeypatch.setattr(loop, 'run_tests_and_score_ips', lambda **kw: {'tests_passed': True, 'test_output': 'passed', 'ips_score': None, 'ips_error': 'disabled'})
    monkeypatch.setattr(loop, 'apply_github_patch', lambda **kw: pytest.fail('Multi-file changes cannot publish one file'))
    result = loop.execute_node({'patch_plans': [plan(a), plan(b)], 'healing_mode': 'github'})
    assert result['final_status'] == 'needs_input'
    assert result['validation']['tests_passed'] is True
    assert a.read_text() == b.read_text() == 'value = 2\n'


def test_publication_failure_retains_validated_local_candidate(workspace, monkeypatch):
    path = workspace / 'a.py'
    path.write_text('value = 1\n')
    monkeypatch.setattr(loop, 'run_tests_and_score_ips', lambda **kw: {'tests_passed': True, 'test_output': 'passed', 'ips_score': None, 'ips_error': 'disabled'})
    monkeypatch.setattr(loop, 'apply_github_patch', lambda **kw: {'status': 'error', 'message': 'authorization unavailable'})
    result = loop.execute_node({'patch_plans': [plan(path)], 'healing_mode': 'github'})
    assert result['final_status'] == 'validated'
    assert result['publication_error'] == 'authorization unavailable'
    assert path.read_text() == 'value = 2\n'


def test_monitor_uses_configured_portable_binary(monkeypatch):
    import config
    actual_setting = config.get_setting
    monkeypatch.setattr(config, 'get_setting', lambda name, default='': '/usr/local/bin/oasdiff' if name == 'OASDIFF_BIN' else actual_setting(name, default))
    calls = []
    def run(cmd, **kwargs):
        calls.append(cmd)
        return type('Result', (), {'returncode': 0, 'stdout': '[]', 'stderr': ''})()
    monkeypatch.setattr(monitor.subprocess, 'run', run)
    assert monitor.get_api_diff() == '[]'
    assert calls[0][0] == '/usr/local/bin/oasdiff'


def test_upgrade_monitor_uses_actual_contract_diff(monkeypatch):
    monkeypatch.setenv('TRIGGER_REASON', 'upgrade_available')
    monkeypatch.setenv('API_VERSION', 'v3')
    calls = []
    def diff(**kwargs):
        calls.append(kwargs)
        return json.dumps({'paths': {'modified': {'/refunds/create': {'new': 'actual feature'}}}})
    monkeypatch.setattr(loop, 'get_api_diff', diff)
    monkeypatch.setattr(loop, 'get_schema_context', lambda *args: 'actual schemas')
    result = loop.monitor_node({})
    assert calls[0]['mode'] == 'diff'
    assert calls[0]['base_spec'].endswith('v2_spec.json')
    assert calls[0]['revised_spec'].endswith('v3_spec.json')
    assert json.loads(result['diff'])[0]['path'] == '/refunds/create'
    assert result['schema_context'] == 'actual schemas'


@pytest.mark.parametrize('status,exit_code', [('failed', 1), ('needs_input', 1), ('no_change', 0), ('validated', 0)])
def test_cli_writes_structured_result_and_truthful_exit(tmp_path, monkeypatch, status, exit_code):
    (tmp_path / 'agent').mkdir()
    monkeypatch.setattr(loop, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(loop, 'app', type('App', (), {'invoke': lambda self, state: {**state, 'final_status': status, 'validation': {'tests_passed': status == 'validated', 'test_output': '', 'ips_score': None, 'ips_error': None}}})())
    assert loop.main() == exit_code
    result = json.loads((tmp_path / 'agent/result.json').read_text())
    assert result['final_status'] == status
    assert result['validation']['tests_passed'] is (status == 'validated')
    assert result['config']['model']
    assert not list((tmp_path / 'agent').glob('.result-*'))


def test_local_tools_remain_callable_when_mcp_decorator_returns_tool(monkeypatch):
    import runpy
    import sys
    import types
    class FakeMCP:
        def __init__(self, *args):
            pass
        def tool(self):
            return lambda fn: object()
    monkeypatch.setitem(sys.modules, 'fastmcp', types.SimpleNamespace(FastMCP=FakeMCP))
    assert callable(runpy.run_path(editor.__file__)['apply_patch'])
    from mcp_server import test_runner
    assert callable(runpy.run_path(test_runner.__file__)['run_tests_and_score_ips'])
