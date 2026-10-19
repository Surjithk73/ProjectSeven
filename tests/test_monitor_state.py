import json

import pytest

from apishield.contract_fetch import parse_contract
from apishield.monitor_state import MonitorStore, MonitorConflict


def settings(**extra):
    return dict(source_url='http://127.0.0.1:9000/spec', allow_local=True,
                interval_minutes=60, baseline_mode='first_fetch', enabled=True, **extra)


def contract(version='1'):
    return parse_contract(json.dumps({'openapi':'3.0.0', 'info':{'title':'Fixture', 'version':version}, 'paths':{}}).encode())


def test_revision_conflict_and_restart(tmp_path):
    store = MonitorStore(tmp_path)
    assert store.read('parcel')['revision'] == 0
    saved = store.configure('parcel', settings(), 0, 'config1')
    assert saved['revision'] == 1 and saved['enabled']
    with pytest.raises(MonitorConflict):
        store.configure('parcel', settings(), 0, 'config1')
    assert MonitorStore(tmp_path).read('parcel') == saved
    with store.transaction('parcel') as state:
        state['last_observation_hash'] = 'retained'
    assert store.read('parcel')['last_observation_hash'] == 'retained'


@pytest.mark.parametrize('field,value', [('interval_minutes',4), ('interval_minutes',True),
    ('baseline_mode','automatic'), ('enabled','yes'), ('allow_local',1)])
def test_invalid_settings(tmp_path, field, value):
    body = settings()
    body[field] = value
    with pytest.raises(ValueError):
        MonitorStore(tmp_path).configure('parcel',body,0,'config1')


def test_snapshot_deduplication_acceptance_and_tampering(tmp_path):
    store = MonitorStore(tmp_path)
    store.configure('parcel',settings(),0,'config1')
    first, second = contract(), contract('2')
    assert store.retain('parcel', first) == store.retain('parcel', parse_contract(json.dumps(first.document, indent=2).encode()))
    store.retain('parcel', second)
    with store.transaction('parcel') as state:
        state['baseline_hash'] = first.content_hash
        state['changes'] = [{'id':'change1','observed_hash':second.content_hash,'baseline_hash':first.content_hash,'job_id':'testjob'}]
    assert store.read('parcel')['baseline_hash'] == first.content_hash
    accepted = store.accept('parcel','change1',1)
    assert accepted['baseline_hash'] == second.content_hash
    assert accepted['changes'][0]['job_id'] == 'testjob'
    assert 'validated' not in accepted
    with pytest.raises(MonitorConflict):
        store.accept('parcel','change1',1)
    snapshot = store.snapshot_path('parcel', second.content_hash)
    snapshot.write_bytes(b'{}')
    with pytest.raises(ValueError, match='snapshot'):
        store.snapshot_path('parcel', second.content_hash)


def test_corrupt_state_and_unsafe_names_are_not_reset(tmp_path):
    store = MonitorStore(tmp_path)
    store.configure('parcel',settings(),0,'config1')
    (tmp_path / '_monitoring/parcel/state.json').write_text('invalid')
    with pytest.raises(ValueError, match='state'):
        store.read('parcel')
    for name in ('../escape','a/b',''):
        with pytest.raises(ValueError):
            store.read(name)


def test_source_edit_resets_observation_but_keeps_changes(tmp_path):
    store = MonitorStore(tmp_path)
    store.configure('parcel',settings(),0,'config1')
    with store.transaction('parcel') as state:
        state['baseline_hash'] = 'old'
        state['changes'] = [{'id':'oldchange'}]
    body = settings()
    body['source_url'] += '?v=2'
    value = store.configure('parcel',body,1,'config1')
    assert value['baseline_hash'] is None
    assert value['changes'] == [{'id':'oldchange'}]
