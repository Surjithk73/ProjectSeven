import json
from pathlib import Path


def test_child_provider_binding_localizes_plain_contract_paths(tmp_path):
    from apishield.analysis import scan_sources
    from apishield.comparison import impacted_sites
    from apishield.repository_graph import build_repository_graph
    (tmp_path/'client.py').write_text("class Client:\n    def seats(self,show_id):\n        return self.client.get(f'/shows/{show_id}/seats')\n")
    bindings={'client.py':{'provider_id':'theatre','base_url':'http://localhost:8101','receiver':'self.client'}}
    scan=scan_sources(tmp_path,['client.py'],bindings,qualify_operations=False)
    comparison={'changed_operations':[{'method':'GET','endpoint':'/shows/{show_id}/seats'}]}
    assert len(impacted_sites(scan,comparison))==1
    graph=build_repository_graph(tmp_path,scan,[],comparison['changed_operations'])
    assert any(n.get('impact')=='direct' and n.get('function')=='Client.seats' for n in graph['nodes'])


def test_binding_migration_preserves_contract_baseline_and_user_settings(tmp_path):
    from demo.setup import ensure_provider_bindings
    from apishield.project_store import ProjectStore
    from apishield.projects import ClientProject,ProviderBinding
    root=tmp_path/'jobs'
    project=ClientProject('cinemaflow',str(tmp_path),[ProviderBinding('theatre','cinema-theatre','http://localhost:8101',source_files=['client.py'])])
    ProjectStore(root).save(project.to_dict(),0)
    path=root/'_integrations/cinema-theatre/integration.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'model':'custom-model','http_bindings':{}}))
    baseline=path.parent/'base.json';baseline.write_text('retained baseline')
    ensure_provider_bindings(root,project)
    result=json.loads(path.read_text())
    assert result['http_bindings']==project.http_bindings()
    assert result['model']=='custom-model' and baseline.read_text()=='retained baseline'
