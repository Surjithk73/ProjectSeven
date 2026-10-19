import pytest

from test_dashboard_jobs import api
from test_publication import publishing, wait


@pytest.fixture
def publication_api(api, publishing):
    coordinator, github, job, jobs = publishing
    api.app.state.local_jobs = jobs
    jobs.publication = coordinator
    jobs.close = lambda: None
    yield api, coordinator, github, job


def test_target_and_proposal_review_then_explicit_publish(publication_api):
    client, service, github, job = publication_api
    target = client.get('/api/integrations/parcel/github')
    assert target.status_code == 200
    assert target.json()['revision'] == 1
    response = client.post('/api/integrations/parcel/proposals', json={'job_id': job.id, 'expected_revision': 1})
    assert response.status_code == 202
    proposal = wait(service, response.json()['id'])
    assert github.calls == []
    preview = client.get('/api/proposals/' + proposal['id']).json()
    assert preview['body'] == proposal['body']
    assert 'GitHub CI: not verified' in preview['body']
    response = client.post('/api/proposals/' + proposal['id'] + '/publish', json={'expected_revision': proposal['revision']})
    assert response.status_code == 202
    assert wait(service, proposal['id'])['status'] == 'published'
    assert github.calls == ['commit', 'branch', 'pr']


def test_target_revision_and_strict_input(publication_api):
    client, service, github, job = publication_api
    path = '/api/integrations/parcel/github'
    assert client.put(path, json={'repository': 'owner/repo', 'base': 'main', 'expected_revision': 0}).status_code == 409
    assert client.put(path, json={'repository': 'owner/repo', 'base': 'main', 'expected_revision': 1}).json()['revision'] == 2
    assert client.put(path, json={'repository': 'owner/repo', 'base': 'main', 'expected_revision': 2, 'token': 'secret'}).status_code == 422
    assert client.post('/api/integrations/parcel/proposals', json={'job_id': job.id, 'expected_revision': 2, 'commands': []}).status_code == 422
    assert client.get('/api/integrations/unknown/github').status_code == 404
    assert github.calls == []


@pytest.mark.parametrize('method,path,body', [('get','/api/integrations/parcel/github',None), ('put','/api/integrations/parcel/github',{'repository':'owner/repo','base':'main','expected_revision':1}), ('get','/api/proposals/'+'a'*64,None), ('post','/api/proposals/'+'a'*64+'/reconcile',None)])
def test_publication_routes_reject_external_origins(publication_api,method,path,body):
    client, *_ = publication_api
    options = {'headers': {'Origin': 'https://external.example'}}
    if body is not None: options['json'] = body
    assert getattr(client,method)(path,**options).status_code == 403


def test_publication_routes_reject_external_host(publication_api):
    client, *_ = publication_api
    assert client.get('/api/integrations/parcel/github',headers={'Host':'external.example'}).status_code == 403
