"""Local contract monitoring: durable claims, comparison jobs and browser routes."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, StrictBool, StrictInt, StrictStr
from typing import Literal

from .configuration import Budgets, IntegrationConfig, load_config
from .contract_fetch import fetch_contract, parse_contract
from .jobs import atomic_json
from .monitor_state import MonitorConflict, MonitorStore


def config_token(path):
    path = str(path)
    return hashlib.sha256(path.encode() + Path(path).read_bytes()).hexdigest()


def recorded_config(data):
    data = dict(data)
    for key in ('repository','base_spec','target_spec'):
        data[key] = Path(data[key])
    data['budgets'] = Budgets(**data['budgets'])
    return IntegrationConfig(**data)


class MonitorService:
    def __init__(self, jobs):
        self.jobs = jobs
        self.store = MonitorStore(jobs.store.root)
        self.fetcher = fetch_contract
        self.stopped = threading.Event()
        self.thread = None
        self._recover()

    def _recover(self):
        from .dashboard_jobs import _pid_alive
        for name in list(self.jobs.integrations):
            reservation = None
            try:
                with self.store.transaction(name) as state:
                    claim = state['active_check']
                    if claim and not _pid_alive(claim.get('pid')):
                        reservation = self._reservation(name,state,claim)
                        self._retain_change(state,reservation)
                        state.update(active_check=None,error='Monitoring check interrupted by process loss; check again to retry.')
                if reservation:
                    self._fail_reservation(name,reservation,'Comparison interrupted before dispatch; rescan code to retry.')
            except ValueError:
                # Preserve corrupt files. GET and further checks report the diagnostic.
                continue

    def _reservation(self, name, state, claim):
        reservation=claim.get('reservation')
        if not reservation or state['revision']!=claim['revision']:
            return None
        try:
            return reservation if config_token(self.jobs.integrations[name])==claim['config_token'] else None
        except (ValueError,OSError):
            return None

    @staticmethod
    def _retain_change(state,reservation):
        if reservation and not any(item['id']==reservation['id'] for item in state['changes']):
            state['changes'].append(reservation)
            if state['baseline_hash'] is None:
                state['baseline_hash']=reservation['baseline_hash']

    def _fail_reservation(self, name, reservation, error):
        """Materialize missing reserved evidence; never allocate another identity."""
        job_id=reservation['job_id']
        try:
            result=self.jobs.store.get(job_id)
        except FileNotFoundError:
            job=self.jobs.create_config_job(name,recorded_config(reservation['config']),'compare',job_id=job_id)
            job.finish({'status':'failed','error':error,'monitor_change_id':reservation['id']})
            job.cleanup()
        else:
            if result['status'] in {'queued','running'}:
                self.jobs.store.cancel(job_id)
                atomic_json(self.jobs.store._path(job_id)/'result.json',{**result,'status':'failed','error':error})

    def configure(self, integration, settings, expected_revision):
        if integration not in self.jobs.integrations:
            raise KeyError('Unknown integration')
        return self.store.configure(integration,settings,expected_revision,config_token(self.jobs.integrations[integration]))

    def start(self):
        if self.thread is not None:
            return
        self.thread = threading.Thread(target=self._loop, daemon=True, name='apishield-contract-monitor')
        self.thread.start()

    def _loop(self):
        while not self.stopped.is_set():
            self.tick(datetime.now(timezone.utc))
            self.stopped.wait(1)

    def tick(self, now):
        with self.jobs.lock:
            names = list(self.jobs.integrations)
        for name in names:
            if self.stopped.is_set():
                break
            try:
                state = self.store.read(name)
                if state['enabled'] and not state['active_check'] and state['next_due'] and datetime.fromisoformat(state['next_due']) <= now:
                    self.check(name)
            except (ValueError, KeyError, OSError):
                continue

    def check(self, integration):
        if self.stopped.is_set():
            raise MonitorConflict('Monitoring is shutting down')
        if integration not in self.jobs.integrations:
            raise KeyError('Unknown integration')
        config_path = self.jobs.integrations[integration]
        claim = {'id':uuid.uuid4().hex, 'pid':os.getpid(),'config_token':None}
        with self.store.transaction(integration) as state:
            if not state['configured']:
                raise ValueError('Configure a contract source first')
            if state['active_check']:
                raise MonitorConflict('A check is already running for this integration')
            claim.update(revision=state['revision'])
            now = datetime.now(timezone.utc)
            state.update(active_check=claim,last_attempt=now.isoformat(),error=None,
                         next_due=(now+timedelta(minutes=state['interval_minutes'])).isoformat() if state['enabled'] else None)
            captured = json.loads(json.dumps(state))
        try:
            token=config_token(config_path)
            config=load_config(config_path)
            with self.store.transaction(integration) as state:
                if state['active_check'] != claim or state['revision'] != claim['revision'] or self.stopped.is_set():
                    if state['active_check']==claim:
                        state['active_check']=None
                    raise MonitorConflict('Monitoring changed while preparing the check; retry')
                claim['config_token']=token
                state['active_check']=dict(claim)
                captured['active_check']=dict(claim)
            self.jobs.executor.submit(self._run_check,integration,config,captured)
        except (RuntimeError,ValueError,OSError) as error:
            self._finish_error(integration,claim,str(error))
            raise
        return {'check_id':claim['id'], 'status':'checking'}

    def _current(self, integration, state, captured):
        claim = captured['active_check']
        return (not self.stopped.is_set() and state['active_check'] == claim
                and state['revision'] == claim['revision']
                and config_token(self.jobs.integrations[integration]) == claim['config_token'])

    def _finish_error(self, integration, claim, error):
        reservation=None
        with self.store.transaction(integration) as state:
            if state['active_check'] == claim:
                state['active_check'] = None
                if state['revision'] == claim['revision']:
                    state['error'] = error
                    reservation=self._reservation(integration,state,claim)
                    self._retain_change(state,reservation)
        if reservation:
            self._fail_reservation(integration,reservation,error)

    def _run_check(self, integration, config, captured):
        reserved = None
        published = False
        claim = captured['active_check']
        try:
            fetched = self.fetcher(captured['source_url'],captured['allow_local'])
            with self.jobs.lock:
                with self.store.transaction(integration) as state:
                    if not self._current(integration,state,captured):
                        if state['active_check'] == claim:
                            state['active_check'] = None
                        return
            observed = self.store.retain(integration,fetched)
            baseline = captured['baseline_hash']
            if baseline is None:
                baseline = (self.store.retain(integration,parse_contract(config.base_spec.read_bytes()))
                            if captured['baseline_mode'] == 'saved' else observed)
            change_id = hashlib.sha256(f'{integration}:{baseline}:{observed}'.encode()).hexdigest()
            existing = next((item for item in captured['changes'] if item['id'] == change_id),None)
            if observed != baseline and existing is None:
                comparison = replace(config,base_spec=self.store.snapshot_path(integration,baseline),
                                     target_spec=self.store.snapshot_path(integration,observed))
                job_id=uuid.uuid4().hex
                reservation={'id':change_id,'baseline_hash':baseline,'observed_hash':observed,
                    'config_token':claim['config_token'],'job_id':job_id,'job_ids':[job_id],
                    'created_at':fetched.fetched_at,'config':comparison.to_dict()}
                with self.jobs.lock:
                    with self.store.transaction(integration) as state:
                        if not self._current(integration,state,captured):
                            if state['active_check']==claim:
                                state['active_check']=None
                            return
                        claim['reservation']=reservation
                        state['active_check']=json.loads(json.dumps(claim))
                reserved = self.jobs.create_config_job(integration,comparison,'compare',job_id=job_id)
                # Resolve once before dispatch; later engine export uses this commit.
                from .workspace import _git
                commit = _git(reserved,'rev-parse','--verify',f'{config.ref}^{{commit}}')
                reserved.config = replace(comparison,ref=commit)
                atomic_json(reserved.path/'config.json',reserved.config.to_dict())
                reserved._initial['monitor_change_id'] = change_id
                atomic_json(reserved.path/'result.json',reserved._initial)
            with self.jobs.lock:
                with self.store.transaction(integration) as state:
                    if not self._current(integration,state,captured):
                        if state['active_check'] == claim:
                            state['active_check'] = None
                        return
                    state.update(baseline_hash=baseline,last_observation_hash=observed,
                                 last_success=fetched.fetched_at,error=None,active_check=None)
                    if reserved:
                        state['changes'].append({'id':change_id,'baseline_hash':baseline,'observed_hash':observed,
                            'config_token':claim['config_token'],'job_id':reserved.id,'job_ids':[reserved.id], 'created_at':fetched.fetched_at,
                            'config':reserved.config.to_dict()})
                        published = True
            if reserved:
                self.jobs.dispatch(reserved)
        except Exception as error:
            self._finish_error(integration,claim,str(error))
        finally:
            if reserved and (not published or reserved.id not in self.jobs.active):
                # If dispatch already completed, leave its terminal evidence untouched.
                result = self.jobs.store.get(reserved.id)
                if result['status'] in {'queued','running'} and reserved.id not in self.jobs.active:
                    reserved.finish({'status':'failed' if published else 'cancelled',
                                     'error':'Comparison was not dispatched; check source state and retry explicitly.'})
                    reserved.cleanup()

    def repair(self, integration, change_id):
        state = self.store.read(integration)
        change = next((item for item in state['changes'] if item['id']==change_id),None)
        if change is None:
            raise KeyError('Unknown monitor change')
        if not self.jobs.model_connection.ready:
            raise ValueError('Configure a model connection before explicitly requesting repair')
        config=recorded_config(change['config'])
        if len(config.ref)!=40 or any(char not in '0123456789abcdef' for char in config.ref):
            raise ValueError('Comparison did not pin a source revision; rescan code before requesting repair')
        config=replace(config,base_spec=self.store.snapshot_path(integration,change['baseline_hash']),
                       target_spec=self.store.snapshot_path(integration,change['observed_hash']))
        return self.jobs.submit_config(integration,config,'repair')

    def rescan(self, integration, change_id):
        state=self.store.read(integration)
        change=next((item for item in state['changes'] if item['id']==change_id),None)
        if change is None:
            raise KeyError('Unknown monitor change')
        path=self.jobs.integrations[integration]
        token=config_token(path)
        config=replace(load_config(path),base_spec=self.store.snapshot_path(integration,change['baseline_hash']),
                       target_spec=self.store.snapshot_path(integration,change['observed_hash']))
        job=self.jobs.create_config_job(integration,config,'compare')
        try:
            from .workspace import _git
            job.config=replace(config,ref=_git(job,'rev-parse','--verify',f'{config.ref}^{{commit}}'))
            atomic_json(job.path/'config.json',job.config.to_dict())
            with self.jobs.lock:
                with self.store.transaction(integration) as current:
                    if current['revision'] != state['revision'] or config_token(self.jobs.integrations[integration]) != token:
                        raise MonitorConflict('Integration changed; retry the rescan')
                    record=next(item for item in current['changes'] if item['id']==change_id)
                    record.setdefault('job_ids',[record['job_id']]).append(job.id)
                    record.update(job_id=job.id,config=job.config.to_dict(),config_token=token)
            return self.jobs.dispatch(job)
        except Exception:
            job.finish({'status':'failed','error':'Rescan could not be dispatched; retry explicitly'})
            job.cleanup()
            raise

    def close(self):
        self.stopped.set()
        if self.thread:
            self.thread.join(timeout=2)
        for name in list(self.jobs.integrations):
            reservation=None
            try:
                with self.store.transaction(name) as state:
                    claim=state['active_check']
                    if claim and claim.get('pid')==os.getpid():
                        reservation=self._reservation(name,state,claim)
                        self._retain_change(state,reservation)
                        state.update(active_check=None,error='Monitoring check interrupted by shutdown; check again to retry.')
                if reservation:
                    self._fail_reservation(name,reservation,'Comparison interrupted by shutdown; rescan code to retry.')
            except ValueError:
                continue


router = APIRouter()


class MonitorInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source_url: StrictStr
    allow_local: StrictBool = False
    interval_minutes: StrictInt = 60
    baseline_mode: Literal['saved','first_fetch']
    enabled: StrictBool
    expected_revision: StrictInt


class AcceptInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    change_id: StrictStr
    expected_revision: StrictInt


def monitor(request, name, mutate=False):
    from .browser_setup import local_browser,read_registry
    from .dashboard_jobs import service
    local_browser(request)
    jobs = service(request)
    if name not in jobs.integrations:
        raise HTTPException(404,'Unknown integration')
    registry=read_registry(jobs.store.root)
    entry=registry.get(name,{})
    editable=not entry.get('example') and entry.get('config')==jobs.integrations[name]
    if mutate and not editable:
        raise HTTPException(403,'Server-managed integrations are read-only in the browser')
    return jobs.monitoring,editable


def respond(action):
    try:
        return action()
    except MonitorConflict as error:
        raise HTTPException(409,str(error)) from error
    except KeyError as error:
        raise HTTPException(404,str(error)) from error
    except (ValueError,OSError) as error:
        raise HTTPException(422,str(error)) from error


@router.get('/api/integrations/{name}/monitoring')
def get_monitor(name: str, request: Request):
    coordinator,editable=monitor(request,name)
    def read():
        state=coordinator.store.read(name)
        state.pop('snapshots')
        for change in state['changes']:
            change.pop('config',None)
            if change.get('job_id'):
                try:
                    change['job_status']=coordinator.jobs.store.get(change['job_id'])['status']
                    change['job_available']=True
                except FileNotFoundError:
                    change.update(job_status='failed',job_available=False)
        state['editable']=editable
        return state
    return respond(read)


@router.put('/api/integrations/{name}/monitoring')
def put_monitor(name: str, body: MonitorInput, request: Request):
    coordinator,_=monitor(request,name,True)
    data=body.model_dump(); revision=data.pop('expected_revision')
    respond(lambda:coordinator.configure(name,data,revision))
    return get_monitor(name,request)


@router.post('/api/integrations/{name}/monitoring/check',status_code=202)
def check_monitor(name: str, request: Request):
    coordinator,_=monitor(request,name,True)
    return respond(lambda:coordinator.check(name))


@router.post('/api/integrations/{name}/monitoring/accept')
def accept_monitor(name: str, body: AcceptInput, request: Request):
    coordinator,_=monitor(request,name,True)
    respond(lambda:coordinator.store.accept(name,body.change_id,body.expected_revision))
    return get_monitor(name,request)


@router.post('/api/integrations/{name}/monitoring/changes/{change_id}/repair',status_code=202)
def repair_monitor(name: str, change_id: str, request: Request):
    coordinator,_=monitor(request,name,True)
    return respond(lambda:coordinator.repair(name,change_id))


@router.post('/api/integrations/{name}/monitoring/changes/{change_id}/rescan',status_code=202)
def rescan_monitor(name: str, change_id: str, request: Request):
    coordinator,_=monitor(request,name,True)
    return respond(lambda:coordinator.rescan(name,change_id))
