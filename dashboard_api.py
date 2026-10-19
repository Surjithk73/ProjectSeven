"""Demo control API; NexusPay provider is served separately on port 8001."""
import asyncio
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
import json
from pathlib import Path
import subprocess
import sys
import threading

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, StrictBool
from config import get_setting
from sig_engine.graph_builder import ensure_sig_current
from mcp_server.process_runner import run_agent_process, ProcessCleanupError


@dataclass
class AppState:
    provider_version: str = 'v1'
    provider_available: bool = False
    agent_status: str = 'idle'
    last_diff: str = ''
    code_before: str = ''
    code_after: str = ''
    ips_score: int | None = None
    agent_log: str = ''
    sig_graph: dict = field(default_factory=dict)
    auto_heal_enabled: bool = False
    auto_merge_enabled: bool = False
    pr_url: str = ''
    pr_number: int = 0
    validation: dict = field(default_factory=dict)
    result: dict = field(default_factory=dict)


state = AppState()
agent_lock = threading.Lock()


def provider_request(method, path, body=None):
    url = get_setting('PROVIDER_URL', 'http://127.0.0.1:8001').rstrip('/') + path
    try:
        call = httpx.get if method == 'GET' else httpx.post
        options = {'timeout': 3.0}
        if body is not None:
            options['json'] = body
        response = call(url, **options)
        response.raise_for_status()
        state.provider_available = True
        return response.json()
    except (httpx.HTTPError, ValueError) as error:
        state.provider_available = False
        raise HTTPException(503, 'NexusPay provider unavailable or returned invalid data') from error


def load_current_client_code():
    try:
        return Path('client_app/payment_service.py').read_text(encoding='utf-8')
    except OSError:
        return ''


def _run_agent_subprocess(mode='webhook', auto_merge=False, use_sig_context=True,
                          trigger_reason='break_detected', lock_reserved=False):
    import os
    if not (lock_reserved or agent_lock.acquire(blocking=False)):
        return
    path = Path('agent/result.json')
    state.agent_status = 'running'
    state.code_before = load_current_client_code()
    state.ips_score, state.pr_url, state.pr_number = None, '', 0
    state.validation, state.result = {}, {}
    originals = None
    keep_lock = False
    try:
        from agent.langgraph_loop import _client_files, _restore
        root = Path('client_app').resolve()
        originals = {file: file.read_bytes() for file in _client_files(root)}
        path.unlink(missing_ok=True)
        env = os.environ.copy()
        env.update(USE_SIG_CONTEXT='1' if use_sig_context else '0', TRIGGER_REASON=trigger_reason,
                   API_VERSION=state.provider_version, PYTHONPATH=str(Path.cwd()))
        command = [sys.executable, '-u', 'agent/langgraph_loop.py', mode]
        process = run_agent_process(command, timeout=300, env=env, cwd=str(Path.cwd()))
        def decode(value):
            return value.decode(errors='replace') if isinstance(value, bytes) else value or ''
        state.agent_log = decode(process.stdout) + decode(process.stderr)
        result = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(result, dict):
            raise ValueError('Malformed agent result')
        outcome, validation = result.get('final_status'), result.get('validation', {})
        if outcome not in {'validated', 'failed', 'no_change', 'needs_input', 'pr_opened'}:
            raise ValueError('Missing valid agent outcome')
        if outcome in {'validated', 'pr_opened'} and (process.returncode != 0 or validation.get('tests_passed') is not True):
            raise ValueError('Agent reported validation without passed tests')
        if outcome == 'no_change' and process.returncode != 0:
            raise ValueError('Agent exited unsuccessfully')
        state.agent_status, state.validation, state.result = outcome, validation, result
        state.last_diff = result.get('diff', '')
        score = result.get('ips_score', validation.get('ips_score'))
        state.ips_score = score if type(score) is int and 0 <= score <= 100 else None
        state.pr_url = result.get('pr_url', '') or ''
        state.pr_number = result.get('pr_number', 0) or 0
    except ProcessCleanupError as error:
        keep_lock = True
        state.agent_status = 'needs_input'
        state.agent_log += f'\n{error}. Repair lock retained to prevent overlapping edits.'
    except Exception as error:
        if originals is not None:
            _restore(root, originals)
        state.agent_status = 'failed'
        state.agent_log += f'\nAgent result unavailable: {error}'
    finally:
        state.code_after = load_current_client_code()
        if not keep_lock:
            agent_lock.release()


def sync_provider_version():
    version = provider_request('GET', '/api/version')['version']
    if version not in {'v1', 'v2', 'v3'}:
        raise HTTPException(503, 'Provider returned unknown version')
    if version != state.provider_version and not agent_lock.locked():
        state.provider_version = version
        state.agent_status = {'v1': 'idle', 'v2': 'break_detected', 'v3': 'upgrade_available'}[version]
    return version


async def monitor_runtime_errors():
    while True:
        await asyncio.sleep(max(1, int(get_setting('POLL_INTERVAL_SECONDS', '10'))))
        if not state.auto_heal_enabled or agent_lock.locked():
            continue
        try:
            version = await asyncio.to_thread(sync_provider_version)
            if state.agent_status in {'break_detected', 'upgrade_available'}:
                reason = 'upgrade_available' if version == 'v3' else 'break_detected'
                await asyncio.to_thread(_run_agent_subprocess, 'webhook', False, True, reason)
        except (HTTPException, KeyError):
            continue


@asynccontextmanager
async def lifespan(app):
    from apishield.dashboard_jobs import local_service
    local_service(app)
    task = asyncio.create_task(monitor_runtime_errors())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
    local_jobs = getattr(app.state, 'local_jobs', None)
    if local_jobs:
        local_jobs.close()
        del app.state.local_jobs


app = FastAPI(title='APIShield Demo Control API', lifespan=lifespan)
from apishield.dashboard_jobs import router as local_jobs_router
app.include_router(local_jobs_router)
from apishield.project_api import router as project_router
app.include_router(project_router)
from apishield.browser_setup import router as browser_setup_router
app.include_router(browser_setup_router)
from apishield.monitoring import router as monitoring_router
app.include_router(monitoring_router)
from apishield.publication_api import router as publication_router
app.include_router(publication_router)
from apishield.banking import router as banking_router
app.include_router(banking_router)
from apishield.graph_semantics import router as graph_semantics_router
app.include_router(graph_semantics_router)
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import JSONResponse


@app.exception_handler(RequestValidationError)
async def validation_error(request, error):
    if request.url.path.startswith('/api/settings/model'):
        return JSONResponse(status_code=422, content={'detail':'Enter a valid API key (1–1024 characters); no other fields are accepted.'})
    return await request_validation_exception_handler(request,error)


app.add_middleware(CORSMiddleware, allow_origins=[
    'http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174', 'http://127.0.0.1:5174'],
    allow_methods=['GET', 'POST', 'PUT'], allow_headers=['Content-Type'])


class Toggle(BaseModel):
    enabled: StrictBool


class ProviderSwitch(BaseModel):
    version: str


class Trigger(BaseModel):
    model_config = ConfigDict(extra='forbid')
    healing_mode: str = 'webhook'
    use_sig_context: StrictBool = True


@app.get('/api/state')
def get_state():
    try:
        sync_provider_version()
    except (HTTPException, KeyError):
        pass
    try:
        ensure_sig_current(client_dir='client_app')
        state.sig_graph = json.loads(Path('sig_engine/sig_store.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        state.sig_graph = {}
    return {**vars(state), 'current_code': load_current_client_code()}


@app.post('/api/settings/auto-heal')
def toggle_auto_heal(body: Toggle):
    state.auto_heal_enabled = body.enabled
    return {'auto_heal': body.enabled}


@app.post('/api/settings/auto-merge')
def toggle_auto_merge(body: Toggle):
    if body.enabled:
        raise HTTPException(400, 'Repairs require human review; automatic merging is disabled')
    return {'auto_merge': False}


@app.post('/api/agent/merge')
def manual_merge():
    raise HTTPException(409, 'Review and merge through your normal GitHub workflow')


@app.post('/api/provider/switch')
def switch_provider(body: ProviderSwitch):
    if body.version not in {'v1', 'v2', 'v3'}:
        raise HTTPException(400, 'Invalid provider version')
    if not agent_lock.acquire(blocking=False):
        raise HTTPException(409, 'Cannot switch provider during a repair')
    try:
        version = provider_request('POST', '/api/version', {'version': body.version})['version']
        if version != body.version:
            raise HTTPException(503, 'Provider did not activate the requested version')
        state.provider_version = version
        state.agent_status = {'v1': 'idle', 'v2': 'break_detected', 'v3': 'upgrade_available'}[version]
        state.last_diff = ''
        state.code_before = state.code_after = state.agent_log = ''
        state.ips_score, state.pr_url, state.pr_number = None, '', 0
        state.validation, state.result = {}, {}
        Path('agent/reasoning_log.jsonl').unlink(missing_ok=True)
        return {'active_version': version, 'agent_status': state.agent_status}
    finally:
        agent_lock.release()


@app.get('/api/provider/logs')
def get_logs():
    return provider_request('GET', '/api/provider/logs')


@app.get('/api/raw_spec')
def get_raw_spec():
    return provider_request('GET', '/api/raw_spec')


@app.get('/api/client/transactions')
def get_transactions():
    try:
        response = httpx.get(get_setting('BFF_URL', 'http://127.0.0.1:8003') + '/api/transactions', timeout=3)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as error:
        raise HTTPException(503, 'SwiftPay BFF unavailable') from error


@app.post('/api/agent/trigger')
async def trigger_agent(body: Trigger = Trigger()):
    if body.healing_mode not in {'webhook', 'github'}:
        raise HTTPException(400, 'Unknown repair mode')
    if not agent_lock.acquire(blocking=False):
        raise HTTPException(409, 'A repair is already running')
    try:
        actual = await asyncio.to_thread(provider_request, 'GET', '/api/version')
        state.provider_version = actual['version']
    except Exception:
        agent_lock.release()
        raise
    reason = 'upgrade_available' if state.provider_version == 'v3' else 'break_detected'
    state.agent_status = 'running'
    await asyncio.to_thread(_run_agent_subprocess, body.healing_mode, False, body.use_sig_context, reason, True)
    return {'status': state.agent_status, 'result': state.result, 'log': state.agent_log}


@app.get('/api/agent/reasoning')
def get_reasoning_log():
    path = Path('agent/reasoning_log.jsonl')
    if not path.exists():
        return {'logs': []}
    logs = []
    for line in path.read_text(encoding='utf-8').splitlines():
        try:
            logs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return {'logs': logs}


frontend_dist = Path(__file__).resolve().parent / 'frontend/dist'
if (frontend_dist / 'index.html').is_file():
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    app.mount('/assets', StaticFiles(directory=frontend_dist / 'assets'), name='frontend-assets')

    @app.get('/', include_in_schema=False)
    @app.get('/banking', include_in_schema=False)
    @app.get('/demo', include_in_schema=False)
    @app.get('/agent', include_in_schema=False)
    @app.get('/provider', include_in_schema=False)
    def browser_app():
        return FileResponse(frontend_dist / 'index.html')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('dashboard_api:app', host='127.0.0.1', port=8002, reload=False)
