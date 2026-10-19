from test_model_access import credential, fake_credentials
from test_dashboard_jobs import api


def test_current_overview_exists_before_any_comparison_and_tracks_working_edits(api):
    import dashboard_api
    from apishield.configuration import load_config
    api.post('/api/examples/banking')
    before = api.get('/api/integrations/banking-example/overview')
    assert before.status_code == 200, before.text
    value = before.json()
    assert value['report']['operation'] == 'scan'
    assert len(value['report']['scan']['sites']) == 6
    assert not any(node.get('impact') for node in value['report']['semantic_graph']['nodes'])
    repo = load_config(dashboard_api.app.state.local_jobs.integrations['banking-example']).repository
    source = repo / 'src/bankclient.py'
    source.write_text(source.read_text() + '\nCURRENT_EDIT = True\n')
    after = api.get('/api/integrations/banking-example/overview').json()
    assert after['report']['source_hash'] != value['report']['source_hash']
    assert api.get('/api/integrations/banking-example/overview').json()['report']['job_id'] == after['report']['job_id']


def test_concurrent_overviews_capture_model_and_generate_once(api, monkeypatch, fake_credentials):
    import dashboard_api
    from concurrent.futures import ThreadPoolExecutor
    from apishield.current_api import current_overview
    from apishield.model_access import cloud_connection
    from apishield.graph_semantics import detect_communities, graph_hash
    api.post('/api/examples/banking')
    jobs = dashboard_api.app.state.local_jobs
    jobs.select_model(cloud_connection(credential()))
    calls = []
    def fake(graph, connection, model):
        import time
        calls.append(connection)
        assert connection is not None and connection.ready
        time.sleep(.1)
        return {'communities': detect_communities(graph), 'inferred_edges': [], 'source_graph_hash': graph_hash(graph)}
    monkeypatch.setattr('apishield.graph_semantics.interpret_graph', fake)
    with ThreadPoolExecutor(2) as pool:
        ids = list(pool.map(lambda _: current_overview(jobs, 'banking-example'), range(2)))
    assert ids[0] == ids[1]
    assert len(calls) == 1
    assert jobs.store.get(ids[0]).get('ai_graph_status') == 'completed'
