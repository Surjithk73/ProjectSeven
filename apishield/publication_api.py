"""Local-only, explicit publication controls; no browser-supplied credentials."""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr

from .browser_setup import local_browser
from .dashboard_jobs import service
from .publication_state import PublicationConflict

router = APIRouter(dependencies=[Depends(local_browser)])


class RevisionInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: StrictInt


class TargetInput(RevisionInput):
    repository: StrictStr
    base: StrictStr


class PrepareInput(RevisionInput):
    job_id: StrictStr


def respond(action):
    try:
        return action()
    except PublicationConflict as error:
        raise HTTPException(409, str(error)) from error
    except (KeyError, FileNotFoundError):
        raise HTTPException(404, 'Publication or integration not found') from None
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    except OSError:
        raise HTTPException(503, 'Publication storage unavailable') from None


def coordinator(request, name=None):
    jobs = service(request)
    if name is not None and name not in jobs.integrations:
        raise HTTPException(404, 'Unknown integration')
    return jobs.publication


@router.get('/api/integrations/{name}/github')
def target(name: str, request: Request):
    publisher = coordinator(request, name)
    return respond(lambda: publisher.store.read_target(name))


@router.put('/api/integrations/{name}/github')
def configure(name: str, body: TargetInput, request: Request):
    publisher = coordinator(request, name)
    return respond(lambda: publisher.configure(name, body.repository, body.base, body.expected_revision))


@router.post('/api/integrations/{name}/proposals', status_code=202)
def prepare(name: str, body: PrepareInput, request: Request):
    publisher = coordinator(request, name)
    return respond(lambda: publisher.prepare(name, body.job_id, body.expected_revision))


@router.get('/api/proposals/{identity}')
def report(identity: str, request: Request):
    return respond(lambda: coordinator(request).store.read(identity))


@router.post('/api/proposals/{identity}/publish', status_code=202)
def publish(identity: str, body: RevisionInput, request: Request):
    return respond(lambda: coordinator(request).publish(identity, body.expected_revision))


@router.post('/api/proposals/{identity}/reconcile', status_code=202)
def reconcile(identity: str, request: Request):
    return respond(lambda: coordinator(request).reconcile(identity))


@router.post('/api/proposals/{identity}/cancel', status_code=202)
def cancel(identity: str, request: Request):
    return respond(lambda: coordinator(request).cancel_prepare(identity))
