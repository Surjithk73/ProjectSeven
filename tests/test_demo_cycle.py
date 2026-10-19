"""Deterministic repair fixtures exercise the full loop, not model quality."""
import os
from pathlib import Path
import shutil

import pytest

import reset
from agent import langgraph_loop as loop, monitor
from mcp_server import file_editor, test_runner

SOURCE = Path(__file__).resolve().parents[1]


@pytest.fixture
def demo(tmp_path, monkeypatch):
    configured = os.getenv('OASDIFF_BIN') or shutil.which('oasdiff')
    binary = Path(configured) if configured else SOURCE / 'tools/oasdiff.exe'
    if not binary.is_file() or (not configured and os.name != 'nt'):
        pytest.skip('Full demo cycle requires a native oasdiff binary')
    for name in ('mock_provider', 'client_app/tests'):
        shutil.copytree(SOURCE / name, tmp_path / name, ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
    shutil.copy2(SOURCE / 'client_app/server.py', tmp_path / 'client_app/server.py')
    (tmp_path / 'agent').mkdir()
    (tmp_path / 'tools').mkdir()
    native_binary = tmp_path / 'tools' / binary.name
    shutil.copy2(binary, native_binary)
    reset.reset(tmp_path, switch_provider=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(loop, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(monitor, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(test_runner, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(file_editor, 'CLIENT_ROOT', tmp_path / 'client_app')
    monkeypatch.setenv('ENABLE_IPS_SCORING', '0')
    monkeypatch.setenv('GEMINI_API_KEY', '')
    monkeypatch.setenv('OASDIFF_BIN', str(native_binary))
    monkeypatch.setenv('API_VERSION', 'v2')
    monkeypatch.setenv('BASE_SPEC', 'mock_provider/specs/v1_spec.json')
    monkeypatch.setenv('REVISED_SPEC', 'mock_provider/specs/v2_spec.json')
    monkeypatch.setenv('PYTHONPATH', str(tmp_path))
    monkeypatch.setenv('TRIGGER_REASON', 'break_detected')
    return tmp_path


def candidate(source, incorrect_amount=False):
    repaired = source.replace('"amount": amount_cents', '"amount": {"value": amount_cents, "currency": "USD"}')
    repaired = repaired.replace('{API_BASE}/refund"', '{API_BASE}/refunds/create"')
    repaired = repaired.replace('"period": billing_period}', '"period": billing_period, "billing_address": billing_address}')
    if 'def log_transaction_event' in repaired:
        repaired = repaired.replace('    return response.json()', '    return response.json()["data"]')
    if incorrect_amount:
        repaired = repaired.replace('"value": amount_cents', '"value": amount_cents // 100')
    return {'old_code_snippet': source, 'new_code_snippet': repaired}


def test_v1_break_v2_validated_repair_without_model(demo, monkeypatch):
    assert test_runner.run_tests_and_score_ips(api_version='v1')['tests_passed'] is True
    before = test_runner.run_tests_and_score_ips(api_version='v2')
    assert before['tests_passed'] is False
    monkeypatch.setattr(loop, 'generate_patch_plan', lambda diff, source, intent, *a, **kw: candidate(source))
    monkeypatch.setattr(loop, 'revise_patch_plan', lambda **kw: candidate(kw['target_code']))
    result = loop.app.invoke({'healing_mode': 'webhook'})
    assert result['final_status'] == 'validated', result
    assert result['validation']['tests_passed'] is True
    assert result['ips_score'] is None
    assert len(result['patch_plans']) == 3
    loop.write_result(result)
    assert (demo / 'agent/result.json').exists()


def test_wrong_amount_repair_is_rejected_and_originals_restored(demo, monkeypatch):
    originals = {p: p.read_bytes() for p in (demo / 'client_app').glob('*.py')}
    monkeypatch.setattr(loop, 'generate_patch_plan', lambda diff, source, intent, *a, **kw: candidate(source, True))
    monkeypatch.setattr(loop, 'revise_patch_plan', lambda **kw: candidate(kw['target_code'], True))
    result = loop.app.invoke({'healing_mode': 'webhook'})
    assert result['final_status'] == 'failed'
    assert result['attempts'] == 3
    assert '5001' in result['validation']['test_output']
    assert all(path.read_bytes() == original for path, original in originals.items())
