import json
import subprocess
from pathlib import Path

import pytest


BASELINE = '77dfc946dd1a40f0fc8af8ef820bdd7009c7cdf0'


class GitHub:
    def __init__(self, approved=True):
        self.approved = approved
        self.branches = []

    def api(self, method, endpoint, payload, **kwargs):
        if endpoint == 'user':
            return {'login': 'Surjithk73'}
        if endpoint.endswith('/check-runs?per_page=100'):
            return {'check_runs': [{'name': 'cinema-client', 'head_sha': BASELINE,
                'status': 'completed', 'conclusion': 'success' if self.approved else 'failure'}]}
        assert method == 'POST' and endpoint.endswith('/git/refs')
        assert payload['sha'] == BASELINE
        self.branches.append(payload['ref'])
        return {'ref': payload['ref'], 'object': {'sha': BASELINE}}


@pytest.fixture
def phone(tmp_path):
    from demo.providers.state import Store
    root = tmp_path / 'phone'
    root.mkdir()
    (root / '.phone-demo').touch()
    (root / 'jobs').mkdir()
    (root / 'jobs/old-evidence.json').write_text('{"repair":"merged"}')
    (root / 'jobs/_integrations/cinema-payment').mkdir(parents=True)
    (root / 'jobs/_integrations/cinema-payment/base.json').write_text('{"info":{"version":"2.0.0"}}')
    (root / 'client-source/movie_booking').mkdir(parents=True)
    (root / 'client-source/movie_booking/payment_client.py').write_text('# Previous AI-migrated V2 client\n')
    (root / 'providers').mkdir()
    (root / 'providers/.apishield-demo-state').touch()
    for name in ('payment', 'theatre'):
        Store(root / f'providers/{name}.db').switch(2)
    return root


def fake_source(path, branch):
    from demo.setup import export_client
    path.mkdir(parents=True)
    export_client(path)
    for args in [('init',), ('config', 'user.name', 'Fixture'),
                 ('config', 'user.email', 'fixture@example.invalid'), ('add', '.'), ('commit', '-m', 'V1')]:
        subprocess.run(['git', '-C', str(path), *args], check=True, capture_output=True)


def test_complete_reset_archives_previous_run_and_restarts_on_isolated_v1_branch(phone, monkeypatch):
    import demo.phone as launcher
    from demo.phone_reset import reset_phone_demo
    from demo.providers.state import Store
    from apishield.project_store import ProjectStore
    from apishield.publication_state import PublicationStore
    monkeypatch.setattr(launcher, 'prepare_source', fake_source)
    monkeypatch.setattr(launcher, 'git', lambda *args: BASELINE)
    github = GitHub()
    result = reset_phone_demo(phone, github=github)
    archive = Path(result['archive'])
    assert json.loads((archive / 'jobs/old-evidence.json').read_text()) == {'repair': 'merged'}
    assert 'V2 client' in (archive / 'client-source/movie_booking/payment_client.py').read_text()
    assert 'V2 client' not in (phone / 'client-source/movie_booking/payment_client.py').read_text()
    assert 'function bookingKey()' in (phone / 'client-source/movie_booking/static/cinema.js').read_text()
    assert not (phone / 'jobs').exists()
    for name in ('payment', 'theatre'):
        assert Store(phone / f'providers/{name}.db').version == 1
        assert Store(archive / f'providers/{name}.db').version == 2
    assert github.branches == ['refs/heads/' + result['base']]

    class StartGitHub(GitHub):
        def api(self, method, endpoint, payload, **kwargs):
            assert 'ref=main' not in endpoint
            return {'login': 'Surjithk73'}
        def inspect_target(self, repository, base, **kwargs):
            assert base == result['base']
            return {'repository': repository, 'base': base, 'account': {'login': 'Surjithk73', 'id': 73}}
    # Reuse the already prepared client; real startup fetches the rehearsal branch.
    monkeypatch.setattr(launcher, 'prepare_source', lambda *args: None)
    prepared = launcher.prepare_phone_demo(phone, github=StartGitHub())
    project = ProjectStore(prepared['jobs']).load_project('cinemaflow')
    assert project.base_branch == result['base'] and project.automation_mode == 'manual'
    assert prepared['deployment']['base'] == result['base']
    assert PublicationStore(prepared['jobs']).read_target('cinemaflow')['base'] == result['base']
    assert ProjectStore(prepared['jobs']).workflows('cinemaflow') == []
    for name in ('payment', 'theatre'):
        doc = json.loads((phone / f'jobs/_integrations/cinema-{name}/base.json').read_text())
        assert doc['info']['version'] == '1.0.0'
    monkeypatch.setattr(launcher, 'prepare_source', fake_source)
    second = reset_phone_demo(phone, github=github)
    assert second['base'] != result['base']
    assert archive.exists() and Path(second['archive']).exists()


def test_reset_refuses_unmanaged_directories_and_failed_baseline_checks(phone, tmp_path, monkeypatch):
    from demo.phone_reset import reset_phone_demo
    import demo.phone as launcher
    monkeypatch.setattr(launcher, 'prepare_source', fake_source)
    with pytest.raises(ValueError, match='managed phone'):
        reset_phone_demo(tmp_path / 'other', github=GitHub())
    github = GitHub(approved=False)
    with pytest.raises(ValueError, match='CI'):
        reset_phone_demo(phone, github=github)
    assert (phone / 'jobs/old-evidence.json').exists()
    assert not github.branches


def test_reset_does_not_move_a_locked_phone_workspace(phone):
    from apishield.engine import _execution_lock
    from demo.phone_reset import reset_phone_demo
    with _execution_lock(phone) as owned:
        assert owned
        with pytest.raises(ValueError, match='stop'):
            reset_phone_demo(phone, github=GitHub(), stop_timeout=0)
    assert (phone / 'jobs/old-evidence.json').exists()


def test_failed_download_preserves_previous_client_and_evidence(phone, monkeypatch):
    import demo.phone as launcher
    from demo.phone_reset import reset_phone_demo
    def fail(*args):
        raise ValueError('Network unavailable')
    monkeypatch.setattr(launcher, 'prepare_source', fail)
    with pytest.raises(ValueError, match='Network'):
        reset_phone_demo(phone, github=GitHub())
    assert (phone / 'jobs/old-evidence.json').exists()
    assert not list(phone.parent.glob('phone-archives/*'))


def test_start_and_reset_share_ownership_lock(phone):
    from demo.phone_reset import control_directory, reset_phone_demo
    from apishield.engine import _execution_lock
    github = GitHub()
    with _execution_lock(control_directory(phone)) as owned:
        assert owned
        with pytest.raises(ValueError, match='stop'):
            reset_phone_demo(phone, github=github, stop_timeout=0)
    assert not github.branches
    assert (phone / 'jobs/old-evidence.json').exists()
