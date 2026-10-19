import json
import os
import threading

from test_dashboard_jobs import api, configured_source
from test_model_access import credential, fake_credentials


def test_cloud_selection_private_session_and_clear(api,monkeypatch,fake_credentials,tmp_path):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    response=api.post('/api/settings/model/cloud',content=credential())
    assert response.status_code==200,response.text
    assert response.json()['connection']['project']=='test-project-123'
    assert 'PRIVATE-FIXTURE' not in response.text and 'GEMINI_API_KEY' not in os.environ
    assert api.get('/api/workspace').json()['model_available']
    import dashboard_api
    jobs=dashboard_api.app.state.local_jobs
    from apishield.configuration import load_config
    job=jobs.create_config_job('fixture',load_config(configured_source(tmp_path)),'repair')
    retained=job._model_connection
    api.post('/api/settings/model/cloud',content=credential(project_id='replacement-project-123'))
    assert job._model_connection is retained and retained.provider=='google_cloud'
    assert job._initial['model_connection']['provider']=='google_cloud'
    assert api.post('/api/settings/model/clear').status_code==200
    assert not jobs.model_connection.ready
    assert not api.get('/api/workspace').json()['model_available']
    assert job._model_connection.ready
    for path in job.path.rglob('*'):
        if path.is_file():
            assert b'PRIVATE-FIXTURE' not in path.read_bytes()
    jobs.close();del dashboard_api.app.state.local_jobs
    assert not api.get('/api/settings/model').json()['configured']


def test_rejected_cloud_setup_preserves_selection_and_never_echoes(api,fake_credentials):
    api.post('/api/settings/model/cloud',content=credential())
    for raw in [b'PRIVATE-FIXTURE',b' '*65537,b'{"private_key":"PRIVATE-FIXTURE"}']:
        response=api.post('/api/settings/model/cloud',content=raw)
        assert response.status_code in {413,422}
        assert 'PRIVATE-FIXTURE' not in response.text
    assert api.get('/api/settings/model').json()['connection']['provider']=='google_cloud'
    assert api.post('/api/settings/model/cloud',content=credential(),headers={'Origin':'https://evil.example'}).status_code==403
    assert api.get('/api/settings/model',headers={'Host':'evil.example'}).status_code==403


def test_late_connection_test_cannot_mark_replacement_tested(api,monkeypatch,fake_credentials):
    from apishield import model_access
    started=threading.Event();release=threading.Event()
    def test(connection):
        started.set();assert release.wait(3);return {'success':True,'model':'gemini-3.8-flash','usage':{}}
    monkeypatch.setattr(model_access,'test_connection',test)
    api.post('/api/settings/model/cloud',content=credential())
    results=[]
    thread=threading.Thread(target=lambda:results.append(api.post('/api/settings/model/test').json()))
    thread.start();assert started.wait(3)
    api.post('/api/settings/model/cloud',content=credential(project_id='replacement-project-123'))
    release.set();thread.join(3)
    assert results[0]['stale']
    assert api.get('/api/settings/model').json()['test'] is None


def test_explicit_generator_keeps_credentials_out_of_prompt(monkeypatch,fake_credentials):
    from apishield.generation import generate_candidate
    from apishield.model_access import cloud_connection
    from contextlib import contextmanager
    from types import SimpleNamespace
    captured=[]
    @contextmanager
    def client(connection,deadline,check=None):
        assert connection.provider=='google_cloud'
        def generate(**kwargs):
            captured.append(kwargs)
            return SimpleNamespace(text='{"needs_input":"Missing address"}',usage_metadata=None)
        yield SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    monkeypatch.setattr('apishield.generation.model_client',client)
    context={'model':'gemini-3.8-flash','request_timeout_seconds':2,'sources':{}}
    assert generate_candidate(context,connection=cloud_connection(credential()))['needs_input']=='Missing address'
    assert 'PRIVATE-FIXTURE' not in json.dumps(captured[0]['contents'])
    assert captured[0]['config'].max_output_tokens==4096


def test_clear_never_falls_back_to_environment_key(api,monkeypatch):
    from apishield.generation import generate_candidate
    from google import genai
    monkeypatch.setenv('GEMINI_API_KEY','AMBIENT-KEY')
    api.post('/api/settings/model/clear')
    import dashboard_api
    connection=dashboard_api.app.state.local_jobs.model_connection
    monkeypatch.setattr(genai,'Client',lambda **kwargs:(_ for _ in ()).throw(AssertionError('must not infer')))
    assert generate_candidate({},connection=connection)['needs_input']


def test_subprocess_never_inherits_google_credentials(tmp_path,monkeypatch):
    from apishield.configuration import load_config
    from apishield.commands import sanitized_environment
    monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS','PRIVATE-PATH')
    monkeypatch.setenv('GEMINI_API_KEY','PRIVATE-KEY')
    env=sanitized_environment(load_config(configured_source(tmp_path)))
    assert 'PRIVATE-' not in json.dumps(env)
