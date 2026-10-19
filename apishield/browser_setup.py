"""Local browser onboarding. Repository commands remain fixed and server-owned."""
import ipaddress
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import uuid
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictStr

from .configuration import load_config, relative_path
from .dashboard_jobs import service
from .jobs import atomic_json
from .requirements import validate_requirements, requirements_hash

router = APIRouter()
example_lock = threading.Lock()
model_configuration_lock = threading.Lock()
SHIPPING_REQUIREMENT = dict(id='shipping-identity-weight',
    description='Preserve package identity and the exact integer gram weight supplied by the caller.',
    scope={'file':'src/parcel.py', 'function':'create_label'}, origin='developer', confirmed=True,
    checks=['tests/test_parcel.py::test_shipping_preserves_package_and_weight'])


def local_browser(request: Request):
    host = request.client.host if request.client else ''
    try:
        local = ipaddress.ip_address(host).is_loopback
    except ValueError:
        local = host == 'testclient'
    allowed = {'localhost', '127.0.0.1', '::1'}
    if not local or request.url.hostname not in allowed | ({'testserver'} if host == 'testclient' else set()):
        raise HTTPException(403, 'Workspace setup is available only on this computer')
    origin = request.headers.get('origin')
    if origin and (urlsplit(origin).hostname not in allowed or urlsplit(origin).scheme != 'http'):
        raise HTTPException(403, 'Open APIShield from its local browser address')


@router.get('/api/settings/model', dependencies=[Depends(local_browser)])
def model_settings(request: Request):
    return service(request).model_settings()


@router.post('/api/settings/model/cloud', dependencies=[Depends(local_browser)])
async def configure_cloud(request: Request):
    from .model_access import persist_cloud_connection
    raw = bytearray()
    try:
        async for chunk in request.stream():
            if len(raw) + len(chunk) > 65536:
                raise HTTPException(413, 'Service-account JSON must be at most 64 KiB')
            raw.extend(chunk)
        with model_configuration_lock:
            connection = persist_cloud_connection(bytes(raw))
            return service(request).select_model(connection)
    except ValueError:
        raise HTTPException(422, 'Select a valid Google service-account JSON without delegation or custom endpoints') from None
    finally:
        raw.clear()


@router.post('/api/settings/model/test', dependencies=[Depends(local_browser)])
def test_model(request: Request):
    return service(request).test_model()


@router.post('/api/settings/model/clear', dependencies=[Depends(local_browser)])
def clear_model(request: Request):
    from .model_access import clear_managed_connection
    with model_configuration_lock:
        return service(request).select_model(clear_managed_connection())


class IntegrationInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: StrictStr = Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')
    repository: StrictStr
    code_paths: list[StrictStr] = Field(min_length=1, max_length=30)
    test_path: StrictStr = 'tests'
    base_spec: dict
    target_spec: dict


def read_registry(root):
    path = root / 'integrations.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def register(jobs, body, *, example=False, replace=False):
    repository = Path(body.repository).resolve()
    if jobs.store.root.resolve().is_relative_to(repository):
        raise ValueError('Job storage must be outside your source repository')
    if body.name in {'shipping-example','banking-example'} and not example:
        raise ValueError('That name is reserved for a built-in example')
    if not body.base_spec.get('openapi') or not body.target_spec.get('openapi'):
        raise ValueError('Upload two JSON OpenAPI contracts with an openapi version')
    test_path = relative_path(body.test_path)
    if test_path.startswith('-'):
        raise ValueError('Test directory cannot be a command option')
    with jobs.lock:
        registry = read_registry(jobs.store.root)
        if replace and (body.name not in registry or registry[body.name].get('example')
                        or jobs.integrations.get(body.name) != registry[body.name]['config']):
            raise ValueError('Only integrations connected in this browser can be edited')
        if not replace and body.name in jobs.integrations:
            raise ValueError('That integration name already exists; choose a new name')
        requirements = (json.loads((repository / 'integration.json').read_text())['requirements']
                        if example and body.name == 'banking-example' else [SHIPPING_REQUIREMENT] if example else [])
        if replace:
            previous = load_config(registry[body.name]['config'])
            requirements = previous.requirements
            if previous.repository != repository or previous.code_paths != body.code_paths or previous.test_commands != [['python', '-m', 'pytest', test_path, '-q']]:
                requirements = [{**rule, 'confirmed':False} for rule in requirements]
        directory = jobs.store.root / '_integrations' / body.name / uuid.uuid4().hex
        directory.mkdir(parents=True, exist_ok=True)
        atomic_json(directory / 'base.json', body.base_spec)
        atomic_json(directory / 'target.json', body.target_spec)
        config_path = directory / 'integration.json'
        atomic_json(config_path, dict(version=1, repository=str(repository), code_paths=body.code_paths,
                    base_spec='base.json', target_spec='target.json',
                    test_commands=[['python', '-m', 'pytest', test_path, '-q']], requirements=requirements))
        load_config(config_path)
        registry[body.name] = {'config': str(config_path), 'example': example}
        atomic_json(jobs.store.root / 'integrations.json', registry)
        jobs.integrations[body.name] = str(config_path)
        if example:
            jobs.example_candidates[body.name] = repository / 'candidate.json'
    return {'name': body.name, 'repository': str(repository), 'example': example}


@router.get('/api/workspace', dependencies=[Depends(local_browser)])
def workspace(request: Request):
    jobs = service(request)
    refresh_example_requirements(jobs)
    registry = read_registry(jobs.store.root)
    details = []
    for name, path in sorted(jobs.integrations.items()):
        try:
            config = load_config(path)
            details.append({'name': name, 'repository': str(config.repository), 'code_paths': config.code_paths,
                            'test_commands': config.test_commands, 'example': name in jobs.example_candidates,
                            'editable': name in registry and not registry[name].get('example') and registry[name]['config'] == path})
        except (OSError, ValueError) as error:
            details.append({'name': name, 'error': str(error), 'example': False})
    return {'integrations': details, 'model_available': jobs.model_connection.ready}


@router.get('/api/integrations/{name}/overview', dependencies=[Depends(local_browser)])
def current_overview(name: str, request: Request):
    from .current_api import current_overview as build_overview
    from .dashboard_jobs import report
    try:
        return {'report': report(build_overview(service(request), name), request)}
    except KeyError:
        raise HTTPException(404, 'Unknown integration') from None
    except (OSError, ValueError) as error:
        raise HTTPException(422, str(error)) from error


@router.post('/api/jobs/{job_id}/apply', dependencies=[Depends(local_browser)])
def apply_repair(job_id: str, request: Request):
    from .local_apply import apply_local_repair
    jobs = service(request)
    try:
        result = jobs.store.get(job_id)
        if result.get('project_workflow'):
            raise ValueError('This client uses GitHub deployment; review and merge its PR instead of applying files on System A')
        return apply_local_repair(jobs, result['integration'], job_id)
    except (KeyError, FileNotFoundError):
        raise HTTPException(404, 'Repair or integration not found') from None
    except (OSError, ValueError) as error:
        raise HTTPException(409, str(error)) from error


@router.post('/api/integrations', status_code=201, dependencies=[Depends(local_browser)])
def create(body: IntegrationInput, request: Request):
    try:
        return register(service(request), body)
    except (ValueError, OSError) as error:
        raise HTTPException(422, str(error)) from error


@router.get('/api/integrations/{name}/config', dependencies=[Depends(local_browser)])
def edit_config(name: str, request: Request):
    jobs = service(request)
    registry = read_registry(jobs.store.root)
    if name not in registry or registry[name].get('example') or jobs.integrations.get(name) != registry[name]['config']:
        raise HTTPException(404, 'This integration is managed outside the browser')
    try:
        config = load_config(registry[name]['config'])
        return {'name':name, 'repository':str(config.repository), 'code_paths':config.code_paths,
                'test_path':config.test_commands[0][3],
                'base_spec':json.loads(config.base_spec.read_text()), 'target_spec':json.loads(config.target_spec.read_text()),
                'requirements':config.requirements}
    except (ValueError, OSError) as error:
        raise HTTPException(422, str(error)) from error


@router.put('/api/integrations/{name}', dependencies=[Depends(local_browser)])
def update(name: str, body: IntegrationInput, request: Request):
    if body.name != name:
        raise HTTPException(422, 'An existing integration cannot be renamed')
    try:
        return register(service(request), body, replace=True)
    except (ValueError, OSError) as error:
        raise HTTPException(422, str(error)) from error


class RequirementsInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    requirements: list[dict] = Field(max_length=100)
    expected_hash: StrictStr = Field(pattern=r'^[a-f0-9]{64}$')


def requirements_view(jobs, name, config):
    registry = read_registry(jobs.store.root)
    editable = name in registry and not registry[name].get('example') and jobs.integrations.get(name) == registry[name]['config']
    return {'requirements':config.requirements, 'requirements_hash':requirements_hash(config.requirements),
            'edit_token':requirements_hash(config.to_dict()), 'editable':editable}


def publish_requirements(jobs, name, config, rules):
    """Caller holds the registry lock; contracts and all other settings stay pinned."""
    directory = jobs.store.root / '_integrations' / name / uuid.uuid4().hex
    directory.mkdir(parents=True)
    path = directory / 'integration.json'
    atomic_json(path, {**config.to_dict(), 'requirements':rules})
    updated = load_config(path)
    registry = read_registry(jobs.store.root)
    registry[name] = {**registry[name], 'config':str(path)}
    atomic_json(jobs.store.root / 'integrations.json', registry)
    jobs.integrations[name] = str(path)
    return updated


def refresh_example_requirements(jobs):
    with jobs.lock:
        if 'shipping-example' in jobs.example_candidates:
            config = load_config(jobs.integrations['shipping-example'])
            if not config.requirements and config.repository == jobs.store.root / '_examples/shipping':
                publish_requirements(jobs, 'shipping-example', config, [SHIPPING_REQUIREMENT])


@router.get('/api/integrations/{name}/requirements', dependencies=[Depends(local_browser)])
def get_requirements(name: str, request: Request):
    jobs = service(request)
    if name not in jobs.integrations:
        raise HTTPException(404, 'Integration not found')
    try:
        refresh_example_requirements(jobs)
        return requirements_view(jobs, name, load_config(jobs.integrations[name]))
    except (OSError, ValueError) as error:
        raise HTTPException(422, str(error)) from error


@router.put('/api/integrations/{name}/requirements', dependencies=[Depends(local_browser)])
def save_requirements(name: str, body: RequirementsInput, request: Request):
    jobs = service(request)
    with jobs.lock:
        registry = read_registry(jobs.store.root)
        if name not in registry or registry[name].get('example') or jobs.integrations.get(name) != registry[name]['config']:
            raise HTTPException(403, 'Requirements are read-only for examples and server-managed integrations')
        try:
            config = load_config(jobs.integrations[name])
            if requirements_hash(config.to_dict()) != body.expected_hash:
                raise HTTPException(409, 'Requirements or integration settings changed since you opened this editor. Reload rules before saving.')
            rules = validate_requirements(body.requirements, config.code_paths)
            previous = {rule['id']:rule for rule in config.requirements}
            for rule in rules:
                old = previous.get(rule['id'])
                definition = lambda r: {k:v for k,v in r.items() if k != 'confirmed'}
                if old is None or definition(old) != definition(rule):
                    rule['confirmed'] = False
            updated = publish_requirements(jobs, name, config, rules)
            return requirements_view(jobs, name, updated)
        except (ValueError, OSError) as error:
            raise HTTPException(422, str(error)) from error


@router.post('/api/examples/shipping', status_code=201, dependencies=[Depends(local_browser)])
def example(request: Request):
    with example_lock:
        return prepare_example(request)


def prepare_example(request: Request):
    jobs = service(request)
    if 'shipping-example' in jobs.example_candidates:
        return {'name': 'shipping-example', 'example': True}
    source = Path(__file__).resolve().parents[1] / 'examples/shipping'
    repo = jobs.store.root / '_examples/shipping'
    try:
        # Only shipped source files are copied; no user-controlled path or argv.
        shutil.copytree(source, repo, dirs_exist_ok=True)
        for argv in (['git', 'init', str(repo)], ['git', '-C', str(repo), 'add', 'src', 'tests'],
                     ['git', '-C', str(repo), '-c', 'user.name=APIShield Example', '-c', 'user.email=example@apishield.local',
                      'commit', '--allow-empty', '-m', 'Shipping V1 example']):
            subprocess.run(argv, check=True, capture_output=True, timeout=15)
        return register(jobs, IntegrationInput(name='shipping-example', repository=str(repo), code_paths=['src'],
                        base_spec=json.loads((repo / 'base.json').read_text()),
                        target_spec=json.loads((repo / 'target.json').read_text())), example=True)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise HTTPException(422, f'Could not prepare shipping example: {error}') from error


@router.post('/api/examples/banking', status_code=201, dependencies=[Depends(local_browser)])
def banking_example(request: Request):
    with example_lock:
        jobs = service(request)
        if 'banking-example' in jobs.example_candidates:
            return {'name':'banking-example','example':True}
        source = Path(__file__).resolve().parents[1] / 'examples/banking'
        repo = jobs.store.root / '_examples/banking'
        try:
            shutil.copytree(source, repo, dirs_exist_ok=True)
            for argv in (['git','init',str(repo)], ['git','-C',str(repo),'add','src','frontend','tests'],
                         ['git','-C',str(repo),'-c','user.name=APIShield Example','-c','user.email=example@apishield.local','commit','--allow-empty','-m','Banking V1 example']):
                subprocess.run(argv, check=True, capture_output=True, timeout=15)
            return register(jobs, IntegrationInput(name='banking-example',repository=str(repo),code_paths=['src'],
                            base_spec=json.loads((repo/'base.json').read_text()),target_spec=json.loads((repo/'target.json').read_text())), example=True)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            raise HTTPException(422, f'Could not prepare banking example: {error}') from error
