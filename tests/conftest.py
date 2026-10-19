"""Never let automated regressions load a user's real managed credentials."""
import pytest


@pytest.fixture(autouse=True)
def isolated_managed_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv('APISHIELD_CREDENTIALS_FILE', str(tmp_path / 'private/service-account.json'))
