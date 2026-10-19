import pytest
import json
from contextlib import contextmanager
from types import SimpleNamespace
from apishield.intent import validate_intent, discover_test_commands


def answer():
    return {'rules': [{'id': 'balance', 'description': 'Preserve exact cents',
                       'file': 'src/client.py', 'function': 'balance'}],
            'checks': [{'file': 'tests/apishield_generated/test_balance.py',
                        'code': 'from src.client import balance\ndef test_balance():\n    assert balance() == 42\n'}]}


def test_intent_checks_are_separate_and_reference_real_source(tmp_path):
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src/client.py').write_text('def balance():\n    return 42\n')
    value = validate_intent(answer(), tmp_path)
    assert value['rules'][0]['origin'] == 'ai_inferred'
    assert value['checks'][0]['file'].startswith('tests/apishield_generated/')
    bad = answer()
    bad['checks'][0]['file'] = 'tests/test_existing.py'
    with pytest.raises(ValueError):
        validate_intent(bad, tmp_path)
    bad = answer()
    bad['rules'][0]['function'] = 'invented'
    with pytest.raises(ValueError):
        validate_intent(bad, tmp_path)


def test_trivial_and_dangerous_generated_checks_are_rejected(tmp_path):
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src/client.py').write_text('def balance():\n    return 42\n')
    for code in ['def test_fake():\n    assert True\n', 'import subprocess\ndef test_run():\n    subprocess.run(["x"])\n    assert 1 == 1\n']:
        bad = answer()
        bad['checks'][0]['code'] = code
        with pytest.raises(ValueError):
            validate_intent(bad, tmp_path)


def test_repository_tests_discovered_without_user_configuration(tmp_path):
    with pytest.raises(ValueError):
        discover_test_commands(tmp_path)
    (tmp_path / 'tests').mkdir()
    (tmp_path / 'tests/test_real.py').write_text('def test_real():\n    assert 1 == 1\n')
    assert discover_test_commands(tmp_path) == [['python', '-m', 'pytest', 'tests', '-q']]


@pytest.mark.parametrize('invalid_code,diagnostic', [
    ('def test_bad():\n    assert getattr(object(), "value") == 42\n', 'forbidden operation'),
    ('def test_bad():\n    args = {"json": 42}\n    assert args[json] == 42\n', 'undefined name: json'),
])
def test_invalid_generated_check_is_regenerated_with_feedback_before_execution(tmp_path, monkeypatch, invalid_code, diagnostic):
    from apishield import intent
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src/client.py').write_text('def balance():\n    return 42\n')
    invalid = answer()
    invalid['checks'][0]['code'] = invalid_code
    calls, deadlines = [], []
    responses = iter([invalid, answer()])
    def generate(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(text=json.dumps(next(responses)), usage_metadata=None)
    @contextmanager
    def client(connection, deadline, check):
        deadlines.append(deadline)
        yield SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    monkeypatch.setattr(intent, 'model_client', client)
    result = intent.infer_intent({'snapshot_root': str(tmp_path), 'model': 'gemini-3.8-flash', 'api_key': 'PRIVATE-FIXTURE'}, object())
    assert result['checks'][0]['code'] == answer()['checks'][0]['code']
    assert len(calls) == 2 and len(deadlines) == 1
    assert diagnostic in calls[1]['contents']
    assert 'unittest.mock.patch' in calls[0]['config'].system_instruction
    assert all('PRIVATE-FIXTURE' not in call['contents'] for call in calls)


def test_invalid_check_regeneration_is_bounded(tmp_path, monkeypatch):
    from apishield import intent
    calls = []
    @contextmanager
    def client(*args):
        def generate(**kwargs):
            calls.append(True)
            return SimpleNamespace(text='{}', usage_metadata=None)
        yield SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    monkeypatch.setattr(intent, 'model_client', client)
    with pytest.raises(ValueError, match='rules and checks'):
        intent.infer_intent({'snapshot_root': str(tmp_path), 'model': 'gemini-3.8-flash'}, object())
    assert len(calls) == 2


def test_undefined_name_in_generated_assertion_is_rejected_before_execution(tmp_path):
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src/client.py').write_text('def balance():\n    return 42\n')
    bad = answer()
    bad['checks'][0]['code'] = 'def test_refund():\n    call_args = ((), {"json": {"transaction_id": "t1"}})\n    assert call_args[1][json] == {"transaction_id": "t1"}\n'
    with pytest.raises(ValueError, match='undefined name.*json'):
        validate_intent(bad, tmp_path)
    bad['checks'][0]['code'] = bad['checks'][0]['code'].replace('[json]', '["json"]')
    assert validate_intent(bad, tmp_path)['checks']


def test_generated_name_validation_accepts_imports_closures_and_comprehensions(tmp_path):
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src/client.py').write_text('def balance():\n    return 42\n')
    value = answer()
    value['checks'][0]['code'] = '''from src.client import balance
def test_balance():
    expected = 42
    def check():
        return balance() == expected
    assert all([check() for item in range(2)])
'''
    assert validate_intent(value, tmp_path)['checks']


@pytest.mark.parametrize('code,failures,expected_calls', [(504, 1, 2), (503, 2, 2), (403, 1, 1)])
def test_intent_provider_recovery_is_bounded_and_does_not_retry_auth(tmp_path, monkeypatch, code, failures, expected_calls):
    from google.genai.errors import ServerError, ClientError
    from apishield import intent
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src/client.py').write_text('def balance():\n    return 42\n')
    deadlines, calls, events = [], [], []
    now = [100.0]
    monkeypatch.setattr(intent.time, 'monotonic', lambda: now[0])
    monkeypatch.setattr(intent.time, 'sleep', lambda seconds: now.__setitem__(0, now[0] + seconds))
    @contextmanager
    def client(connection, deadline, check):
        deadlines.append(deadline)
        def generate(**kwargs):
            calls.append(kwargs)
            now[0] += 60
            if len(calls) <= failures:
                error_type = ServerError if code >= 500 else ClientError
                raise error_type(code, {'error': {'message': 'private provider diagnostic'}})
            return SimpleNamespace(text=json.dumps(answer()), usage_metadata=None)
        yield SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    monkeypatch.setattr(intent, 'model_client', client)
    context = {'snapshot_root': str(tmp_path), 'model': 'gemini-3.8-flash',
               'request_timeout_seconds': 120, 'intent_timeout_seconds': 240}
    if code == 504:
        assert intent.infer_intent(context, object(), on_activity=events.append)['checks']
        assert events and 'retry' in events[0].lower()
        assert deadlines == [220, 281]
    else:
        with pytest.raises(Exception) as error:
            intent.infer_intent(context, object(), on_activity=events.append)
        if code == 503:
            assert 'private provider diagnostic' not in str(error.value)
            assert 'unavailable' in str(error.value).lower()
        else:
            assert isinstance(error.value, ClientError)
    assert len(calls) == expected_calls


def test_intent_timeout_recovery_checks_cancellation_before_retry(tmp_path, monkeypatch):
    from apishield import intent
    cancelled, calls = [False], []
    def check():
        if cancelled[0]:
            raise RuntimeError('job cancellation requested')
    @contextmanager
    def client(*args):
        def generate(**kwargs):
            calls.append(True)
            cancelled[0] = True
            raise TimeoutError('Google request timed out')
        yield SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    monkeypatch.setattr(intent, 'model_client', client)
    with pytest.raises(RuntimeError, match='cancellation requested'):
        intent.infer_intent({'snapshot_root': str(tmp_path), 'model': 'gemini-3.8-flash'}, object(), check=check)
    assert len(calls) == 1


def test_intent_does_not_retry_after_stage_deadline(tmp_path, monkeypatch):
    from apishield import intent
    now, calls = [100.0], []
    monkeypatch.setattr(intent.time, 'monotonic', lambda: now[0])
    @contextmanager
    def client(*args):
        def generate(**kwargs):
            calls.append(True)
            now[0] += 120
            raise TimeoutError('Google request timed out')
        yield SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    monkeypatch.setattr(intent, 'model_client', client)
    with pytest.raises(RuntimeError, match='Gemini'):
        intent.infer_intent({'snapshot_root': str(tmp_path), 'model': 'gemini-3.8-flash',
                            'intent_timeout_seconds': 120}, object())
    assert len(calls) == 1
