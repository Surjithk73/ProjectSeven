from pathlib import Path
import pytest


def test_project_persistence_revision_and_single_provider_migration(tmp_path):
    from apishield.projects import ClientProject, ProviderBinding
    from apishield.project_store import ProjectStore
    store = ProjectStore(tmp_path)
    project = ClientProject('cinema', str(tmp_path), [ProviderBinding('payment', 'pay-child', 'http://127.0.0.1:8102', '')])
    saved = store.save(project.to_dict(), 0)
    assert saved['automation_mode'] == 'manual' and saved['revision'] == 1
    assert store.load_project('cinema').providers[0].integration_id == 'pay-child'
    with pytest.raises(ValueError, match='changed'):
        store.save(project.to_dict(), 0)
    migrated = store.ensure_legacy('old', str(tmp_path), 'http://localhost:8001')
    assert migrated.providers[0].integration_id == 'old'
    assert store.ensure_legacy('old', str(tmp_path), 'http://localhost:8001').project_id == 'old'


def test_provider_match_origin_prefix_and_dynamic_uncertainty():
    from apishield.projects import ProviderBinding, resolve_provider
    bindings = [ProviderBinding('a', 'a', 'http://a.local:8101', '/api'), ProviderBinding('b', 'b', 'http://b.local:8102', '')]
    assert resolve_provider('http://a.local:8101/api/payments', bindings) == 'a'
    assert resolve_provider('http://b.local:8102/payments', bindings) == 'b'
    assert resolve_provider('http://a.local:8101/apiculture', bindings) is None
    assert resolve_provider('http://{host}/api/payments', bindings) is None


def test_project_rejects_duplicate_providers_and_bad_mode(tmp_path):
    from apishield.projects import ClientProject, ProviderBinding
    binding = ProviderBinding('a', 'a', 'http://localhost:8101', '')
    with pytest.raises(ValueError):
        ClientProject('cinema', str(tmp_path), [binding, binding])
    with pytest.raises(ValueError):
        ClientProject('cinema', str(tmp_path), [binding], automation_mode='merge_everything')
