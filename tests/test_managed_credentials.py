import json
from test_model_access import credential, fake_credentials
from test_dashboard_jobs import api


def test_managed_service_account_survives_restart_and_ignores_api_keys(tmp_path, monkeypatch, fake_credentials):
    from apishield.model_access import persist_cloud_connection, environment_connection
    path = tmp_path / 'private/service-account.json'
    monkeypatch.setenv('APISHIELD_CREDENTIALS_FILE', str(path))
    monkeypatch.setenv('GEMINI_API_KEY', 'DO-NOT-USE')
    value = persist_cloud_connection(credential())
    assert value.provider == 'google_cloud'
    assert environment_connection().metadata() == value.metadata()
    assert json.loads(path.read_text())['type'] == 'service_account'
    path.unlink()
    assert not environment_connection().ready


def test_api_key_setup_is_unavailable_and_cloud_configuration_persists(api, fake_credentials):
    assert api.post('/api/settings/model', json={'key': 'DO-NOT-USE'}).status_code in {404, 405, 410}
    assert api.post('/api/settings/model/cloud', content=credential()).status_code == 200
    import dashboard_api
    service = dashboard_api.app.state.local_jobs
    service.close()
    del dashboard_api.app.state.local_jobs
    response = api.get('/api/settings/model').json()
    assert response['configured'] is True
    assert response['connection']['provider'] == 'google_cloud'


def test_remove_rejects_project_credential_path(monkeypatch):
    import pytest
    from pathlib import Path
    from apishield.model_access import clear_managed_connection
    path = Path(__file__).resolve().parents[1] / 'service-account.json'
    monkeypatch.setenv('APISHIELD_CREDENTIALS_FILE', str(path))
    with pytest.raises(ValueError, match='outside the project'):
        clear_managed_connection()


def test_private_save_replaces_existing_explicit_windows_grants(tmp_path, monkeypatch, fake_credentials):
    import os
    import subprocess
    import pytest
    from apishield.model_access import persist_cloud_connection
    if os.name != 'nt':
        pytest.skip('Windows ACL regression')
    directory = tmp_path / 'private'
    directory.mkdir()
    subprocess.run(['icacls', str(directory), '/grant', '*S-1-1-0:(OI)(CI)R'], check=True, capture_output=True)
    monkeypatch.setenv('APISHIELD_CREDENTIALS_FILE', str(directory / 'service-account.json'))
    persist_cloud_connection(credential())
    script = "([System.IO.Directory]::GetAccessControl('" + str(directory).replace("'", "''") + "')).Access | ForEach-Object { $_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value }"
    identities = subprocess.check_output(['powershell.exe', '-NoProfile', '-Command', script], text=True).splitlines()
    assert 'S-1-1-0' not in identities
    assert len(identities) == 2


def test_remove_rejects_junction_ancestor(tmp_path, monkeypatch):
    import os
    import subprocess
    import pytest
    from apishield.model_access import clear_managed_connection
    if os.name != 'nt':
        pytest.skip('Windows junction regression')
    target = tmp_path / 'target'
    target.mkdir()
    protected = target / 'service-account.json'
    protected.write_text('KEEP', encoding='utf-8')
    junction = tmp_path / 'junction'
    subprocess.run(['cmd', '/c', 'mklink', '/J', str(junction), str(target)], check=True, capture_output=True)
    monkeypatch.setenv('APISHIELD_CREDENTIALS_FILE', str(junction / protected.name))
    try:
        with pytest.raises(ValueError, match='Unsafe private credential path'):
            clear_managed_connection()
        assert protected.read_text(encoding='utf-8') == 'KEEP'
    finally:
        junction.rmdir()
