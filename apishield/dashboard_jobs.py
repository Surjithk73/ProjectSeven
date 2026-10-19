"""Allowlisted local dashboard adapter to the same engine as the CLI."""
from concurrent.futures import ThreadPoolExecutor
import ctypes
import json
import os
from pathlib import Path
import re
import shutil
import threading
from dataclasses import replace
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict, StrictStr

from .configuration import load_config
from .jobs import JobStore, atomic_json

router = APIRouter()
_creation_lock = threading.Lock()


def _pid_alive(pid):
    if type(pid) is not int or pid <= 0:
        return False
    if os.name == 'nt':
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.restype = ctypes.c_void_p
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() == 5
        try:
            code = ctypes.c_ulong()
            return bool(kernel.GetExitCodeProcess(ctypes.c_void_p(handle), ctypes.byref(code))) and code.value == 259
        finally:
            kernel.CloseHandle(ctypes.c_void_p(handle))
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


class LocalJobs:
    def __init__(self, root, integrations):
        if not isinstance(integrations, dict) or any(not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', name)
                or not isinstance(path, str) or not path for name, path in integrations.items()):
            raise ValueError('APISHIELD_INTEGRATIONS must map names to trusted config paths')
        self.integrations = dict(integrations)
        self.store = JobStore(root)
        from .browser_setup import read_registry
        registry = read_registry(self.store.root)
        self.example_candidates = {}
        for name, entry in registry.items():
            if name not in self.integrations:
                self.integrations[name] = entry['config']
                if entry.get('example') and name in {'shipping-example', 'banking-example'}:
                    self.example_candidates[name] = self.store.root / '_examples' / name.removesuffix('-example') / 'candidate.json'
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='apishield-local')
        self.lock = threading.Lock()
        from .model_access import environment_connection
        self.model_connection = environment_connection()
        self.model_revision = 0
        self.model_test = None
        self.active = {}
        self.closed = False
        self._recover_interrupted()
        from .monitoring import MonitorService
        self.monitoring = MonitorService(self)
        from .publication import PublicationService
        self.publication = PublicationService(self)
        from .automation import AutomationService
        self.automation = AutomationService(self)

    def model_settings(self):
        with self.lock:
            return {'configured':self.model_connection.ready,'connection':self.model_connection.metadata(),
                    'revision':self.model_revision,'model':'gemini-3.8-flash','test':self.model_test}

    def select_model(self, connection):
        with self.lock:
            self.model_connection = connection
            self.model_revision += 1
            self.model_test = None
        return self.model_settings()

    def test_model(self):
        from .model_access import test_connection
        with self.lock:
            connection, revision = self.model_connection, self.model_revision
        result = test_connection(connection)
        with self.lock:
            stale = revision != self.model_revision
            if not stale:
                self.model_test = result
        return {**result,'revision':revision,'stale':stale}

    def _capture_model(self, job):
        if job.operation == 'repair' or job._initial.get('current_overview'):
            job._model_connection = self.model_connection
            job._initial['model_connection'] = {**self.model_connection.metadata(),'model':job.config.model}

    def _recover_interrupted(self):
        for result in self.store.list_jobs():
            if result['status'] not in {'queued', 'running'}:
                continue
            path = self.store._path(result['job_id'])
            try:
                owner = json.loads((path / 'owner.json').read_text())
            except (OSError, ValueError):
                continue
            if owner.get('owner') == 'dashboard' and not _pid_alive(owner.get('pid')):
                self.store.cancel(result['job_id'])
                final = {**result, 'status': 'failed',
                    'error': 'Dashboard job interrupted by process loss; start a new job to retry.'}
                workspace = path / 'workspace'
                try:
                    if workspace.is_symlink():
                        workspace.unlink()
                    elif workspace.exists():
                        if workspace.resolve().parent != path.resolve():
                            raise ValueError('Unsafe interrupted workspace path')
                        shutil.rmtree(workspace)
                except (OSError, ValueError) as error:
                    final['cleanup_error'] = str(error)
                atomic_json(path / 'result.json', final)

    def submit(self, integration, operation, proposal='model'):
        with self.lock:
            if self.closed:
                raise ValueError('Dashboard jobs are shutting down')
            if integration not in self.integrations:
                raise KeyError('Unknown server-configured integration')
            candidate = None
            if proposal == 'example':
                raise ValueError('Browser repairs use AI only; supplied example repairs are unavailable')
            config = load_config(self.integrations[integration])
            context = None
            if operation != 'scan':
                from .current_api import capture_api_context
                context = capture_api_context(self, integration)
                config = replace(config, base_spec=context['base_spec'], target_spec=context['target_spec'])
            config = replace(config, source_mode='working', requirements=[])
            job = self.store.create(config, operation)
            self._capture_model(job)
            job._initial['integration'] = integration
            job._initial['browser_ai'] = operation == 'repair'
            if context:
                job._initial['api_context'] = {key: str(value) if isinstance(value, Path) else value for key, value in context.items()}
            atomic_json(job.path / 'result.json', job._initial)
            atomic_json(job.path / 'owner.json', {'owner': 'dashboard', 'pid': os.getpid(), 'integration': integration})
            future = self.executor.submit(self._run, job, candidate) if candidate else self.executor.submit(self._run, job)
            self.active[job.id] = (future, job)
        return {'job_id': job.id, 'status': 'queued', 'integration': integration,
                'api_context': job._initial.get('api_context')}

    def _run(self, job, candidate=None):
        try:
            from .engine import run_job
            run_job(job.config, job.operation, self.store, job=job, **({'candidate_path': candidate} if candidate else {}))
        except Exception as error:
            job.event('adapter_error', error=str(error))
            job.finish({'status': 'failed', 'error': str(error)})
            job.cleanup()
        finally:
            job._model_connection = None
            with self.lock:
                self.active.pop(job.id, None)

    def create_config_job(self, integration, config, operation, *, job_id=None):
        """Reserve evidence before dispatch so monitoring can persist job identity."""
        with self.lock:
            if self.closed:
                raise ValueError('Dashboard jobs are shutting down')
            job = self.store.create(config, operation, job_id=job_id)
            self._capture_model(job)
            job._initial['integration'] = integration
            atomic_json(job.path / 'result.json', job._initial)
            atomic_json(job.path / 'owner.json', {'owner':'dashboard','pid':os.getpid(),'integration':integration})
            return job

    def dispatch(self, job):
        with self.lock:
            if self.closed:
                raise ValueError('Dashboard jobs are shutting down')
            future = self.executor.submit(self._run, job)
            self.active[job.id] = (future, job)
        return {'job_id':job.id, 'status':'queued', 'integration':job._initial['integration']}

    def submit_config(self, integration, config, operation):
        return self.dispatch(self.create_config_job(integration, config, operation))

    def close(self):
        self.automation.close()
        self.publication.close()
        self.monitoring.close()
        with self.lock:
            self.closed = True
            active = list(self.active.values())
        for future, job in active:
            self.store.cancel(job.id)
            if future.cancel():
                job.finish({'status': 'cancelled', 'error': 'Dashboard shut down before execution'})
                job.cleanup()
        self.executor.shutdown(wait=False, cancel_futures=True)


def service(request: Request):
    return local_service(request.app)


def local_service(app):
    with _creation_lock:
        if not hasattr(app.state, 'local_jobs'):
            from config import get_setting
            try:
                integrations = json.loads(get_setting('APISHIELD_INTEGRATIONS', '{}'))
                root = Path(get_setting('APISHIELD_JOBS_DIR', str(Path.home() / '.apishield/jobs')))
                app.state.local_jobs = LocalJobs(root, integrations)
                app.state.local_jobs.monitoring.start()
                app.state.local_jobs.automation.start()
            except (ValueError, OSError) as error:
                raise HTTPException(503, f'Local job configuration invalid: {error}') from error
        return app.state.local_jobs


class JobRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    integration: StrictStr
    operation: Literal['scan', 'compare', 'repair'] = 'scan'
    proposal: Literal['model', 'example'] = 'model'


@router.get('/api/integrations')
def integrations(request: Request):
    return {'integrations': sorted(service(request).integrations)}


@router.get('/api/jobs')
def jobs(request: Request):
    return {'jobs': service(request).store.list_jobs()}


@router.post('/api/jobs', status_code=202)
def start(body: JobRequest, request: Request):
    try:
        return service(request).submit(body.integration, body.operation, body.proposal)
    except KeyError as error:
        raise HTTPException(404, str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(422, str(error)) from error


@router.get('/api/jobs/{job_id}')
def report(job_id: str, request: Request):
    try:
        from .engine import recover_interrupted
        store = service(request).store
        result = recover_interrupted(store, job_id)
        from .overview import retained_overview
        value = {**result, 'contract_overview':retained_overview(store._path(job_id), result)}
        if result.get('error'):
            from .activity import failure_explanation
            value['failure_explanation'] = failure_explanation(result)
        if result.get('semantic_graph'):
            from .graph_semantics import graph_view
            value['graph_view']=graph_view(store._path(job_id),result['semantic_graph'])
            value['graph_view']['can_generate']=service(request).model_connection.ready
        if result.get('application', {}).get('status') == 'applied':
            # Keep the reviewed snapshot/patch intact, but show working-source
            # graph evidence when an applied repair is reopened from history.
            from .current_api import current_overview
            current_id = current_overview(service(request), result['integration'])
            value['current_graph_report'] = report(current_id, request)
        return value
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(404, str(error)) from error


@router.get('/api/jobs/{job_id}/activity')
def activity(job_id: str, request: Request):
    from .activity import read_activity
    try:
        return read_activity(service(request).store, job_id)
    except (ValueError, OSError) as error:
        raise HTTPException(404, str(error)) from error


@router.post('/api/jobs/{job_id}/cancel')
def cancel(job_id: str, request: Request):
    try:
        return service(request).store.cancel(job_id)
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(404, str(error)) from error


@router.get('/api/jobs/{job_id}/patch', response_class=PlainTextResponse)
def patch(job_id: str, request: Request):
    result = report(job_id, request)
    if result.get('status') != 'validated':
        raise HTTPException(409, 'A patch is available only for a validated candidate')
    path = service(request).store._path(job_id) / 'candidate.patch'
    if path.is_symlink() or not path.is_file():
        raise HTTPException(404, 'Validated patch artifact unavailable')
    return path.read_text(encoding='utf-8')
