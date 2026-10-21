"""Local-browser routes for real multi-provider projects and workflow evidence."""
from dataclasses import replace
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, StrictInt, Field
from typing import Literal

from .browser_setup import local_browser
from .dashboard_jobs import service
from .configuration import load_config
from .jobs import atomic_json

router = APIRouter(dependencies=[Depends(local_browser)])


def respond(action):
    try:
        return action()
    except (KeyError, StopIteration, FileNotFoundError):
        raise HTTPException(404, 'Project or workflow not found') from None
    except (ValueError, OSError) as error:
        raise HTTPException(422, str(error)) from None


class ModeInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    mode: Literal['manual', 'automatic_edit']
    expected_revision: StrictInt


class WorkflowInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    action: Literal['generate', 'prepare', 'publish', 'retry']


class DeploymentInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    actor: str = Field(pattern=r'^[A-Za-z0-9-]{1,39}$')
    expected_revision: StrictInt


@router.get('/api/projects')
def projects(request: Request):
    return respond(lambda: {'projects': service(request).automation.projects.list()})


def project_snapshot(jobs, project_id):
    project = jobs.automation.projects.load_project(project_id)
    providers = []
    for binding in project.providers:
        monitor = jobs.monitoring.store.read(binding.integration_id)
        endpoints = []
        digest = monitor['last_observation_hash'] or monitor['baseline_hash']
        document = None
        if digest:
            document = json.loads(jobs.monitoring.store.snapshot_path(binding.integration_id, digest).read_text())
        elif binding.integration_id in jobs.integrations:
            config = load_config(jobs.integrations[binding.integration_id])
            document = json.loads(config.base_spec.read_text())
        if document:
            endpoints = [{'provider_id': binding.provider_id, 'method': method.upper(), 'endpoint': path}
                         for path, operations in document.get('paths', {}).items() for method in operations if method in {'get','post','put','patch','delete'}]
        providers.append({**binding.__dict__, 'monitoring': monitor, 'endpoints': endpoints,
                          'observed_version': document.get('info', {}).get('version') if document else None})
    with jobs.automation.projects.transaction(project_id) as state:
        error = state.get('error')
    workflows = jobs.automation.projects.workflows(project_id)
    return {'project': project.to_dict(), 'providers': providers, 'workflows': workflows, 'error': error}


@router.get('/api/projects/{project_id}')
def project(project_id: str, request: Request):
    return respond(lambda: project_snapshot(service(request), project_id))


@router.get('/api/projects/{project_id}/workflows')
def workflows(project_id: str, request: Request):
    return respond(lambda: {'workflows': service(request).automation.projects.workflows(project_id)})


@router.patch('/api/projects/{project_id}/automation')
def mode(project_id: str, body: ModeInput, request: Request):
    return respond(lambda: service(request).automation.set_automation_mode(project_id, body.mode, body.expected_revision))


@router.post('/api/projects/{project_id}/connect-github')
def connect_github(project_id: str, request: Request):
    jobs = service(request)
    def connect():
        project = jobs.automation.projects.load_project(project_id)
        target = jobs.publication.store.read_target(project_id)
        return jobs.publication.configure(project_id, project.target_repository, project.base_branch, target['revision'])
    return respond(connect)


@router.patch('/api/projects/{project_id}/deployment')
def deployment_settings(project_id: str, body: DeploymentInput, request: Request):
    jobs = service(request)
    def save():
        project = jobs.automation.projects.load_project(project_id)
        project.deployment_actor = body.actor
        return jobs.automation.projects.save(project.to_dict(), body.expected_revision)
    return respond(save)


@router.post('/api/projects/{project_id}/check')
def check_all(project_id: str, request: Request):
    jobs = service(request)
    def run():
        project = jobs.automation.projects.load_project(project_id)
        checks = [jobs.monitoring.check(p.integration_id) for p in project.providers]
        _, changes = jobs.automation.snapshots(project)
        workflow = jobs.automation.observe(project_id, changes, jobs.automation.source(project)) if changes else None
        return {'checks': checks, 'workflow': workflow}
    return respond(run)


@router.post('/api/projects/{project_id}/providers/{provider_id}/check')
def check_provider(project_id: str, provider_id: str, request: Request):
    jobs = service(request)
    def run():
        provider = next(p for p in jobs.automation.projects.load_project(project_id).providers if p.provider_id == provider_id)
        return jobs.monitoring.check(provider.integration_id)
    return respond(run)


@router.post('/api/projects/{project_id}/workflows/{workflow_id}')
def workflow_action(project_id: str, workflow_id: str, body: WorkflowInput, request: Request):
    automation = service(request).automation
    def run():
        if body.action == 'retry':
            record = next(w for w in automation.projects.workflows(project_id) if w['workflow_id'] == workflow_id)
            if record['state'] != 'failed':
                raise ValueError('Only failed workflows can be explicitly retried')
            automation.update(project_id, workflow_id, state='awaiting_request', job_id=None, publication_id=None,
                              error=None, prepare_requested=False, publish_requested=False)
            return automation.dispatch_change(project_id, workflow_id)
        if body.action == 'generate':
            return automation.dispatch_change(project_id, workflow_id)
        return automation.request_publication(project_id, workflow_id, publish=body.action == 'publish')
    return respond(run)


@router.post('/api/projects/{project_id}/overview')
def overview(project_id: str, request: Request):
    jobs = service(request)
    def run():
        project = jobs.automation.projects.load_project(project_id)
        documents = {}
        for binding in project.providers:
            monitor = jobs.monitoring.store.read(binding.integration_id)
            config = load_config(jobs.integrations[binding.integration_id])
            old = jobs.monitoring.store.snapshot_path(binding.integration_id, monitor['baseline_hash']) if monitor['baseline_hash'] else config.base_spec
            new = jobs.monitoring.store.snapshot_path(binding.integration_id, monitor['last_observation_hash']) if monitor['last_observation_hash'] else old
            documents[binding.provider_id] = (json.loads(old.read_text()), json.loads(new.read_text()))
        source = jobs.automation.source(project)
        config = jobs.automation.config(project, source, documents)
        return jobs.submit_config(project_id, config, 'compare')
    return respond(run)
