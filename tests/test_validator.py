import subprocess

import pytest

from mcp_server import test_runner as runner


def test_default_validation_runs_all_workflows_with_version_and_stderr(monkeypatch):
    calls = []
    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 1, 'assertion details', 'import failure')
    monkeypatch.setattr(runner.subprocess, 'run', run)
    monkeypatch.setenv('API_VERSION', 'v2')
    result = runner.run_tests_and_score_ips()
    assert calls[0][0][-2:] == ['client_app/tests', '-v']
    assert calls[0][1]['env']['API_VERSION'] == 'v2'
    assert calls[0][1]['timeout'] > 0
    assert result['tests_passed'] is False
    assert 'assertion details' in result['test_output'] and 'import failure' in result['test_output']
    assert result['ips_score'] is None
    assert isinstance(result['ips_error'], str)


def test_validation_timeout_is_reported(monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 1, output=b'partial stdout', stderr=b'partial stderr')
    monkeypatch.setattr(runner.subprocess, 'run', timeout)
    result = runner.run_tests_and_score_ips()
    assert result['tests_passed'] is False
    assert 'partial stdout' in result['test_output'] and 'partial stderr' in result['test_output']
    assert 'timed out' in result['test_output']


@pytest.mark.parametrize('text', ['101', '-1', '95 confidence', 'score: 90', '12.5', '', '99\n100'])
def test_ips_rejects_malformed_or_out_of_range_scores(monkeypatch, text):
    import config
    monkeypatch.setenv('ENABLE_IPS_SCORING', '1')
    monkeypatch.setattr(runner.subprocess, 'run', lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, 'passed', ''))
    class Models:
        def generate_content(self, **kwargs):
            return type('Response', (), {'text': text})()
    monkeypatch.setattr(config, 'get_genai_client', lambda: type('Client', (), {'models': Models()})())
    result = runner.run_tests_and_score_ips()
    assert result['tests_passed'] is True
    assert result['ips_score'] is None
    assert result['ips_error']


def test_ips_retains_real_low_score_without_floor(monkeypatch):
    import config
    monkeypatch.setenv('ENABLE_IPS_SCORING', '1')
    monkeypatch.setattr(runner.subprocess, 'run', lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, 'passed', ''))
    class Models:
        def generate_content(self, **kwargs):
            return type('Response', (), {'text': '7'})()
    monkeypatch.setattr(config, 'get_genai_client', lambda: type('Client', (), {'models': Models()})())
    result = runner.run_tests_and_score_ips()
    assert result['ips_score'] == 7
    assert result['ips_error'] is None


def test_default_validator_does_not_call_paid_model(monkeypatch):
    import config
    monkeypatch.delenv('ENABLE_IPS_SCORING', raising=False)
    monkeypatch.setattr(config, 'get_genai_client', lambda: pytest.fail('Routine validation may not call paid model'))
    monkeypatch.setattr(runner.subprocess, 'run', lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, 'passed', ''))
    result = runner.run_tests_and_score_ips()
    assert result['tests_passed'] is True
    assert result['ips_score'] is None
