from dataclasses import replace

import pytest

from apishield.configuration import load_config
from apishield.workspace import prepare_workspace
from test_local_engine import shipment, git


def working_job(shipment):
    repo, path, candidate, store, raw = shipment
    config = replace(load_config(path), source_mode='working')
    return repo, store.create(config, 'scan')


def test_working_files_are_captured_once_and_committed_mode_stays_pinned(shipment):
    repo, path, candidate, store, raw = shipment
    original = (repo / 'src/client.py').read_text()
    (repo / 'src/client.py').write_text(original + '\nCURRENT = 2\n')
    (repo / 'src/new.py').write_text('NEW = 3\n')
    _, job = working_job(shipment)
    first = prepare_workspace(job)
    assert first['source_mode'] == 'working'
    assert (job.workspace / 'src/client.py').read_text().endswith('CURRENT = 2\n')
    assert (job.workspace / 'src/new.py').read_text() == 'NEW = 3\n'
    (repo / 'src/client.py').write_text('LATER = 4\n')
    second = prepare_workspace(job)
    assert first['source_hash'] == second['source_hash']
    assert (job.workspace / 'src/client.py').read_text().endswith('CURRENT = 2\n')
    committed = store.create(load_config(path), 'scan')
    prepare_workspace(committed)
    assert (committed.workspace / 'src/client.py').read_text() == original
    assert not (committed.workspace / 'src/new.py').exists()


def test_working_snapshot_excludes_secrets_ignored_and_dependency_files(shipment):
    repo, path, candidate, store, raw = shipment
    (repo / '.env').write_text('SECRET=never-capture')
    (repo / '.gitignore').write_text('src/ignored.py\n')
    (repo / 'src/ignored.py').write_text('PRIVATE = 1')
    (repo / 'node_modules').mkdir()
    (repo / 'node_modules/tool.js').write_text('unneeded')
    _, job = working_job(shipment)
    prepare_workspace(job)
    assert not (job.workspace / '.env').exists()
    assert not (job.workspace / 'src/ignored.py').exists()
    assert not (job.workspace / 'node_modules').exists()


def test_working_snapshot_hash_changes_when_local_code_changes(shipment):
    repo, job = working_job(shipment)
    first = prepare_workspace(job)
    (repo / 'src/client.py').write_text('DIFFERENT = 1\n')
    _, other = working_job(shipment)
    assert prepare_workspace(other)['source_hash'] != first['source_hash']


def test_retained_snapshot_rejects_injected_files(shipment):
    repo, job = working_job(shipment)
    prepare_workspace(job)
    (job.path / 'source-tree/src/injected.py').write_text('INJECTED = True\n')
    with pytest.raises(ValueError, match='modified'):
        prepare_workspace(job)
