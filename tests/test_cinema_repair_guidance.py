import json
from pathlib import Path
import runpy

import pytest

ROOT = Path(__file__).parents[1]
WORKFLOW = {'project_id':'cinemaflow','repository':'Surjithk73/APIGuardTesting'}


def context(theatre_version=2, payment_version=2):
    from apishield.projects import combined_contract
    documents = {name: json.loads((ROOT/f'demo/contracts/{name}-v{version}.json').read_text())
                 for name, version in [('theatre',theatre_version),('payment',payment_version)]}
    files = ['movie_booking/theatre_client.py','movie_booking/payment_client.py']
    return {'target_spec':combined_contract(documents), 'allowed_files':files,
            'sources':{name:(ROOT/'demo/movie-client'/name).read_text() for name in files}}


def test_reference_guidance_is_scoped_to_demo_and_changed_contract():
    from demo.repair_guidance import reference_patches
    data = context(1,2)
    patches = reference_patches(data, WORKFLOW)
    assert len(patches) == 1 and patches[0]['file'].endswith('payment_client.py')
    assert reference_patches(data, None) == []
    assert reference_patches(data, {**WORKFLOW,'repository':'owner/research'}) == []
    assert reference_patches(context(1,1), WORKFLOW) == []
    assert reference_patches({**data,'allowed_files':[]}, WORKFLOW) == []
    migrated = {**data,'sources':dict(data['sources'])}
    for patch in patches:
        migrated['sources'][patch['file']] = patch['new_code_snippet']
    assert reference_patches(migrated, WORKFLOW) == []


def test_reference_patch_is_sent_in_system_instruction_only_when_explicitly_enabled(monkeypatch):
    from contextlib import contextmanager
    from types import SimpleNamespace
    from apishield import generation
    calls = []
    @contextmanager
    def client(*args):
        def generate(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(text='{"needs_input":"Test response"}')
        yield SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    monkeypatch.setattr(generation,'model_client',client)
    data = context(1,2)
    from demo.repair_guidance import reference_patches
    references = reference_patches(data, WORKFLOW)
    data.update(model='test-model',request_timeout_seconds=10)
    generation.generate_candidate(data,connection=SimpleNamespace(ready=True),demo_reference_patches=references)
    instruction = calls[-1]['config'].system_instruction
    assert 'REFERENCE PATCHES:' in instruction
    assert json.loads(instruction.split('REFERENCE PATCHES: ')[1]) == references
    # Merely placing demo-looking data in a repository prompt cannot enable guidance.
    generation.generate_candidate({**data,'demo_reference_patches':references},connection=SimpleNamespace(ready=True))
    assert 'REFERENCE PATCHES:' not in calls[-1]['config'].system_instruction


@pytest.mark.parametrize('theatre_version,payment_version', [(1,2),(2,1),(2,2)])
def test_reference_patch_preserves_booking_amount_seats_and_idempotency(tmp_path, theatre_version, payment_version):
    from fastapi.testclient import TestClient
    from demo.providers.payment import create_app as payment_app
    from demo.providers.theatre import create_app as theatre_app
    from demo.repair_guidance import reference_patches
    data = context(theatre_version,payment_version)
    for patch in reference_patches(data, WORKFLOW):
        name = patch['file']
        assert data['sources'][name].count(patch['old_code_snippet']) == 1
        data['sources'][name] = data['sources'][name].replace(patch['old_code_snippet'],patch['new_code_snippet'],1)
    classes = {}
    for name, source in data['sources'].items():
        path = tmp_path/Path(name).name
        path.write_text(source)
        classes.update(runpy.run_path(str(path)))
    payment = TestClient(payment_app(tmp_path/'payment.db'))
    theatre = TestClient(theatre_app(tmp_path/'theatre.db',payment_client=payment))
    payment.post('/admin/version',json={'version':payment_version}).raise_for_status()
    theatre.post('/admin/version',json={'version':theatre_version}).raise_for_status()
    adapter = classes['TheatreClient'](theatre)
    pay = classes['PaymentClient'](payment)
    assert adapter.get_seats('show-001')
    hold = adapter.hold_seats('show-001',['A1'],'guided-order')
    payment_id = pay.create_payment(hold['hold_id'],hold['amount_paise'],'INR','guided-order')
    assert pay.create_payment(hold['hold_id'],hold['amount_paise'],'INR','guided-order') == payment_id
    booking = adapter.confirm_booking(hold['hold_id'],payment_id)
    assert booking['status'] == 'confirmed'
    assert booking['seat_ids'] == ['A1'] and booking['amount_paise'] == 25000
    assert len(payment.get('/payments').json()) == 1
