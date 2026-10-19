import pytest
import json
from apishield.graph_semantics import detect_communities, validate_interpretation

GRAPH={'nodes':[{'id':'a','kind':'function','function':'pay'},{'id':'b','kind':'operation','method':'POST','endpoint':'/transfers'},{'id':'c','kind':'function','function':'balance'}], 'edges':[{'from':'a','to':'b','kind':'consumes','basis':'scanner'}]}


def test_communities_cover_each_node_once_without_inventing_links():
    groups=detect_communities(GRAPH)
    assert sorted(n for g in groups for n in g['members'])==['a','b','c']
    assert any(set(g['members'])=={'a','b'} for g in groups)
    assert GRAPH['edges']==[{'from':'a','to':'b','kind':'consumes','basis':'scanner'}]


def test_ai_groups_are_validated_and_links_are_marked_as_inferences():
    answer={'groups':[{'name':'Money movement','description':'Transfer flow','members':[0,1]},{'name':'Balances','description':'Balance flow','members':[2]}], 'links':[{'from':0,'to':2,'reason':'Potential business relationship','confidence':.6}]}
    overlay=validate_interpretation(answer,GRAPH)
    assert overlay['communities'][0]['members']==['a','b']
    assert overlay['inferred_edges'][0]['basis']=='ai_inference'
    assert overlay['inferred_edges'][0]['from']=='a'
    assert 'impact' not in overlay['inferred_edges'][0]
    for bad in (99,True):
        answer['links'][0]['from']=bad
        with pytest.raises(ValueError):validate_interpretation(answer,GRAPH)


def test_ai_missing_and_duplicate_assignments_are_rejected():
    for groups in ([{'name':'X','description':'','members':[0]}],[{'name':'X','description':'','members':[0,0,1,2]}]):
        with pytest.raises(ValueError):validate_interpretation({'groups':groups,'links':[]},GRAPH)

from test_dashboard_jobs import api, configured_source
from apishield.jobs import JobStore, atomic_json
from apishield.configuration import load_config
from apishield.graph_semantics import graph_hash, graph_view
from apishield.model_access import cloud_connection
from test_model_access import credential, fake_credentials

def stored_graph(tmp_path):
    config=load_config(configured_source(tmp_path))
    job=JobStore(tmp_path/'jobs').create(config,'scan')
    job.finish({'status':'completed','scan':{'sites':[]},'semantic_graph':GRAPH})
    job.cleanup()
    return job

def test_ai_route_preserves_base_graph_and_releases_failure_guard(api,tmp_path,monkeypatch,fake_credentials):
    import dashboard_api
    monkeypatch.setenv('GEMINI_API_KEY','')
    monkeypatch.setattr('apishield.graph_semantics.interpret_graph',lambda *args: (_ for _ in ()).throw(AssertionError('Unexpected model request')))
    job=stored_graph(tmp_path)
    route=f'/api/jobs/{job.id}/graph/ai'
    assert api.post(route,headers={'Origin':'https://outside.example'}).status_code==403
    assert api.post(route).status_code==409
    jobs=dashboard_api.app.state.local_jobs
    jobs.model_connection=cloud_connection(credential())
    calls=[]
    def failed(*args):
        calls.append(1)
        raise ValueError('Invalid grouping')
    monkeypatch.setattr('apishield.graph_semantics.interpret_graph',failed)
    assert api.post(route).status_code==422
    assert not jobs.graph_requests
    overlay={**validate_interpretation({'groups':[{'name':'Payments','description':'','members':[0,1,2]}],'links':[]},GRAPH),'source_graph_hash':graph_hash(GRAPH),'model':'test','created_at':'now'}
    monkeypatch.setattr('apishield.graph_semantics.interpret_graph',lambda *args:overlay)
    assert api.post(route).status_code==200
    response=api.get(f'/api/jobs/{job.id}').json()
    assert response['semantic_graph']==GRAPH
    assert response['graph_view']['ai']['communities'][0]['name']=='Payments'
    assert len(calls)==1
    assert 'graph_view' not in json.loads((tmp_path/'jobs'/job.id/'result.json').read_text())

def test_corrupted_or_stale_overlay_is_ignored(tmp_path):
    overlay=tmp_path/'graph-ai.json'
    atomic_json(overlay,{'source_graph_hash':graph_hash(GRAPH),'communities':[{'name':'X','description':'','members':['invented']}],'inferred_edges':[]})
    assert graph_view(tmp_path,GRAPH)['ai'] is None
    atomic_json(overlay,{'source_graph_hash':'stale'})
    assert graph_view(tmp_path,GRAPH)['ai'] is None
