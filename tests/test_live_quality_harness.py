from pathlib import Path
import subprocess
import sys

import pytest

from research.live_quality import cases, checks, command


def test_harness_children_do_not_inherit_model_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', 'synthetic-secret-for-regression')
    result = command([sys.executable, '-B', '-c',
                      'import os; print("GEMINI_API_KEY" in os.environ)'], tmp_path)
    assert result.stdout.strip() == 'False'


@pytest.mark.parametrize('case_name', ['endpoint','response_nesting'])
def test_quality_oracle_rejects_return_without_api_call(tmp_path, case_name):
    case = next(case for case in cases() if case['name']==case_name)
    (tmp_path/'src').mkdir()
    (tmp_path/'src/__init__.py').write_text('')
    answer = '{"held-out-user-π":701,"another-user":0,"large-exact":123456789}[user]' if case['method']=='get' else '{"id":f"reply:{user}:{value}:checked"}'
    (tmp_path/'src/client.py').write_text(f'def invoke(user, value):\n    return {answer}\n',encoding='utf-8')
    (tmp_path/'test_oracle.py').write_text(checks(case,True),encoding='utf-8')
    result = subprocess.run([sys.executable,'-B','-m','pytest','test_oracle.py','-q'],cwd=tmp_path,
                             capture_output=True,text=True,timeout=30)
    assert result.returncode == 1, result.stdout + result.stderr
    assert 'seen' in result.stdout


def test_quality_evidence_must_be_outside_git_source(tmp_path):
    subprocess.run(['git','init',str(tmp_path)],check=True,capture_output=True)
    output = tmp_path/'evidence'
    result = subprocess.run([sys.executable,'-B','-m','research.live_quality','--output',str(output)],
                             cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,timeout=45)
    assert result.returncode == 2, result.stdout + result.stderr
    assert not output.exists()


@pytest.mark.parametrize('case_name', ['endpoint','response_nesting'])
def test_oracle_rejects_ignoring_actual_response(tmp_path, case_name):
    case = next(case for case in cases() if case['name']==case_name)
    (tmp_path/'src').mkdir()
    (tmp_path/'src/__init__.py').write_text('')
    if case['method']=='get':
        invocation='httpx.get("https://quality.example.test/balance", params={"user":user})'
        answer='value'
    else:
        invocation='httpx.post("https://quality.example.test/labels/create", json={"user_id":user,"value":value})'
        answer='{"id":"ok"}'
    (tmp_path/'src/client.py').write_text(f'import httpx\ndef invoke(user,value):\n    {invocation}\n    return {answer}\n')
    (tmp_path/'test_oracle.py').write_text(checks(case,True),encoding='utf-8')
    result = subprocess.run([sys.executable,'-B','-m','pytest','test_oracle.py','-q'],cwd=tmp_path,
                             capture_output=True,text=True,timeout=30)
    assert result.returncode == 1, result.stdout + result.stderr
    assert 'AssertionError' in result.stdout
