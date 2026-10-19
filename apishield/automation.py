"""Durable project orchestration; candidates still use the existing AI engine."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import threading
import time
import uuid

from .configuration import IntegrationConfig, load_config
from .engine import _execution_lock
from .jobs import atomic_json, timestamp
from .project_store import ProjectStore
from .projects import combined_contract

TERMINAL = {'verified', 'failed', 'superseded', 'closed'}


def git(repository, *arguments):
    result = subprocess.run(['git', '-C', str(repository), *arguments], capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise ValueError('Client repository command failed; check Git connectivity and the configured revision')
    return result.stdout.strip()


class AutomationService:
    def __init__(self, jobs):
        self.jobs = jobs
        self.projects = ProjectStore(jobs.store.root)
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._loop, name='apishield-projects', daemon=True)
            self.thread.start()

    def close(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2)

    def _loop(self):
        while not self.stop_event.is_set():
            try:
                self.tick()
            except Exception:
                # Per-project diagnostics are persisted by tick; shutdown must stay safe.
                pass
            self.stop_event.wait(5)

    def set_automation_mode(self, project_id, mode, expected_revision):
        project = self.projects.load_project(project_id)
        if mode == 'automatic_edit':
            if not self.jobs.model_connection.ready:
                raise ValueError('Configure and test the AI connection before enabling automatic edit mode')
            if not project.target_repository:
                raise ValueError('Configure the GitHub publication target first')
            target = self.jobs.publication.store.read_target(project_id)
            if not target['configured'] or target.get('repository') != project.target_repository:
                raise ValueError('Connect the project GitHub publisher before enabling automatic edit mode')
            for provider in project.providers:
                monitor = self.jobs.monitoring.store.read(provider.integration_id)
                if not monitor['configured'] or not monitor['enabled']:
                    raise ValueError('Enable real monitoring for every provider before enabling automatic edit mode')
            from .github_cli import GhClient
            (self.jobs.publication.github or GhClient()).inspect_target(project.target_repository, project.base_branch, deadline=time.monotonic()+45)
        project.automation_mode = mode
        return self.projects.save(project.to_dict(), expected_revision)

    def observe(self, project_id, providers, source_sha):
        key = hashlib.sha256(json.dumps([project_id, providers, source_sha], sort_keys=True).encode()).hexdigest()
        cancelled = []
        with self.projects.transaction(project_id) as state:
            existing = next((w for w in state['workflows'] if w['identity'] == key), None)
            if existing:
                return json.loads(json.dumps(existing))
            for prior in state['workflows']:
                if prior['state'] not in TERMINAL:
                    if prior['state'] == 'generating' and prior.get('job_id'):
                        cancelled.append(prior['job_id'])
                    prior.update(state='superseded', updated_at=timestamp(), error='A newer provider or source snapshot requires a combined update')
            record = {'workflow_id': uuid.uuid4().hex, 'identity': key, 'project_id': project_id, 'providers': providers,
                'source_sha': source_sha, 'state': 'awaiting_request', 'job_id': None, 'publication_id': None,
                'prepare_requested': False, 'publish_requested': False, 'merge_sha': None, 'deployed_sha': None,
                'created_at': timestamp(), 'updated_at': timestamp(), 'error': None, 'events': []}
            state['workflows'].append(record)
            saved = json.loads(json.dumps(record))
        for job_id in cancelled:
            try:
                self.jobs.store.cancel(job_id)
            except FileNotFoundError:
                pass
        return saved

    def update(self, project_id, workflow_id, **changes):
        with self.projects.transaction(project_id) as state:
            record = next(w for w in state['workflows'] if w['workflow_id'] == workflow_id)
            if 'state' in changes and changes['state'] != record['state']:
                record['events'].append({'time': timestamp(), 'message': changes['state'].replace('_', ' ')})
            record.update(changes, updated_at=timestamp())
            return json.loads(json.dumps(record))

    def snapshots(self, project):
        documents, changes = {}, {}
        for provider in project.providers:
            state = self.jobs.monitoring.store.read(provider.integration_id)
            if state['error']:
                raise ValueError(f'{provider.provider_id}: {state["error"]}')
            if not state['baseline_hash'] or not state['last_observation_hash']:
                raise ValueError(f'Check {provider.provider_id} before analyzing the client')
            baseline, observed = state['baseline_hash'], state['last_observation_hash']
            old = self.jobs.monitoring.store.snapshot_path(provider.integration_id, baseline)
            new = self.jobs.monitoring.store.snapshot_path(provider.integration_id, observed)
            documents[provider.provider_id] = (json.loads(old.read_text()), json.loads(new.read_text()))
            if baseline != observed:
                change = next((c for c in reversed(state['changes']) if c['baseline_hash'] == baseline and c['observed_hash'] == observed), None)
                changes[provider.provider_id] = {'base_hash': baseline, 'observed_hash': observed,
                    'change_id': change['id'] if change else None, 'integration_id': provider.integration_id}
        return documents, changes

    def source(self, project, refresh=False):
        if git(project.repository, 'status', '--porcelain'):
            raise ValueError('Client checkout has uncommitted work; commit or preserve it before migration')
        if refresh:
            remote = git(project.repository, 'remote', 'get-url', 'origin').removesuffix('.git')
            if remote not in {f'https://github.com/{project.target_repository}', f'git@github.com:{project.target_repository}'}:
                raise ValueError('Client remote does not match the configured GitHub target')
            git(project.repository, 'fetch', 'origin', project.base_branch)
            git(project.repository, 'merge', '--ff-only', f'origin/{project.base_branch}')
        return git(project.repository, 'rev-parse', 'HEAD')

    def config(self, project, source_sha, documents):
        directory = self.projects.directory(project.project_id) / 'contracts'
        directory.mkdir(exist_ok=True)
        specs = []
        for index in (0, 1):
            document = combined_contract({name: values[index] for name, values in documents.items()})
            content = json.dumps(document, sort_keys=True).encode()
            path = directory / (hashlib.sha256(content).hexdigest() + '.json')
            if not path.exists():
                atomic_json(path, document)
            specs.append(path)
        child = load_config(self.jobs.integrations[project.providers[0].integration_id])
        return replace(child, repository=Path(project.repository), ref=source_sha, source_mode='committed',
            base_spec=specs[0], target_spec=specs[1], http_bindings=project.http_bindings(),
            code_paths=sorted({name for p in project.providers for name in p.source_files}), requirements=[],
            test_commands=[['python', '-m', 'pytest', 'movie_booking/tests', '-q']])

    def dispatch_change(self, project_id, workflow_id, automatic=False):
        project = self.projects.load_project(project_id)
        if automatic and project.automation_mode != 'automatic_edit':
            return None
        repository_lock = self.projects.root / ('repository-' + hashlib.sha256(str(Path(project.repository).resolve()).casefold().encode()).hexdigest())
        repository_lock.mkdir(parents=True, exist_ok=True)
        with _execution_lock(repository_lock) as owned:
            if not owned:
                raise ValueError('Another update owns this client repository')
            record = next(w for w in self.projects.workflows(project_id) if w['workflow_id'] == workflow_id)
            if record['state'] != 'awaiting_request':
                return record
            for other in self.projects.list():
                if Path(other['repository']).resolve() != Path(project.repository).resolve():
                    continue
                for prior in self.projects.workflows(other['project_id']):
                    if prior['workflow_id'] != workflow_id and prior.get('job_id'):
                        result = self.jobs.store.get(prior['job_id'])
                        if result['status'] in {'queued','running'}:
                            return record  # The cancelled/older worker must finish before the next paid request.
            if not self.jobs.model_connection.ready:
                raise ValueError('Configure the AI connection before requesting an update')
            documents, changes = self.snapshots(project)
            source_sha = self.source(project)
            if changes != record['providers'] or source_sha != record['source_sha']:
                raise ValueError('Provider or source snapshot changed; check again')
            config = self.config(project, source_sha, documents)
            job_id = uuid.uuid4().hex
            # Persist identity first, so interruption cannot silently dispatch a second paid request.
            self.update(project_id, workflow_id, state='generating', job_id=job_id)
            job = self.jobs.create_config_job(project_id, config, 'repair', job_id=job_id)
            job._initial.update(browser_ai=True, project_workflow={'workflow_id': workflow_id, 'project_id': project_id,
                'providers': changes, 'repository': project.target_repository, 'base': project.base_branch})
            atomic_json(job.path / 'result.json', job._initial)
            self.jobs.dispatch(job)
            return self.projects.workflows(project_id)[-1]

    def request_publication(self, project_id, workflow_id, publish=False):
        record = next(w for w in self.projects.workflows(project_id) if w['workflow_id'] == workflow_id)
        if record['state'] not in {'awaiting_publication', 'preparing', 'ready'}:
            raise ValueError('A validated update is required before preparing a PR')
        return self.update(project_id, workflow_id, prepare_requested=True, publish_requested=publish or record['publish_requested'])

    def tick(self):
        for item in self.projects.list():
            project = self.projects.load_project(item['project_id'])
            try:
                documents, changes = self.snapshots(project)
                source_sha = self.source(project)
                if changes:
                    record = self.observe(project.project_id, changes, source_sha)
                    if record['state'] == 'awaiting_request' and project.automation_mode == 'automatic_edit':
                        self.dispatch_change(project.project_id, record['workflow_id'], automatic=True)
                self.advance(project)
                with self.projects.transaction(project.project_id) as state:
                    state.pop('error', None)
            except Exception as error:
                with self.projects.transaction(project.project_id) as state:
                    state['error'] = str(error)[:1000]

    def advance(self, project):
        for record in self.projects.workflows(project.project_id):
            if record['state'] in TERMINAL:
                continue
            wid = record['workflow_id']
            if record['state'] == 'generating':
                try:
                    result = self.jobs.store.get(record['job_id'])
                except FileNotFoundError:
                    self.update(project.project_id, wid, state='failed', error='Update dispatch was interrupted; explicitly retry')
                    continue
                if result['status'] in {'queued', 'running'}:
                    continue
                if result['status'] != 'validated':
                    self.update(project.project_id, wid, state='failed', error=result.get('error', 'Candidate did not pass validation'))
                    continue
                automatic = project.automation_mode == 'automatic_edit'
                record = self.update(project.project_id, wid, state='awaiting_publication', prepare_requested=automatic, publish_requested=automatic)
            if record['state'] == 'awaiting_publication' and record['prepare_requested']:
                target = self.jobs.publication.store.read_target(project.project_id)
                prepared = self.jobs.publication.prepare(project.project_id, record['job_id'], target['revision'])
                record = self.update(project.project_id, wid, state='preparing', publication_id=prepared['id'])
            if record['publication_id']:
                published = self.jobs.publication.store.read(record['publication_id'])
                if published['status'] in {'failed', 'stale', 'cancelled'}:
                    self.update(project.project_id, wid, state='failed', error=published.get('error'))
                    continue
                if published['status'] == 'ready':
                    self.update(project.project_id, wid, state='ready')
                    if record['publish_requested']:
                        self.jobs.publication.publish(published['id'], published['revision'])
                elif published['status'] == 'published':
                    from .merge_tracking import reconcile_publication
                    result = reconcile_publication(published, self.jobs.publication.github)
                    status = result['state']
                    self.update(project.project_id, wid, state='pr_open' if status == 'pr_open' else status,
                                merge_sha=result['merge_sha'], pr_url=result['pr_url'],
                                pr_number=published['publication']['number'], error='Merged revision did not pass client CI' if status == 'ci_failed' else None)
                    if status == 'merged':
                        self.reconcile_deployment(project, record, published, result['merge_sha'])

    def reconcile_deployment(self, project, record, publication, merge_sha):
        from demo.deployment.receipt import read_receipt, verify_receipt
        receipt = read_receipt(self.jobs.publication.github, project.target_repository, publication['publication']['number'],
                               merge_sha, project.deployment_actor)
        if receipt is None:
            return
        current = {key: value['observed_hash'] for key, value in record['providers'].items()}
        if not verify_receipt(receipt, record, merge_sha, current):
            self.update(project.project_id, record['workflow_id'], state='failed', error='Deployment evidence is stale or validation failed')
            return
        # Verify the live source still matches before accepting the deployed baseline.
        _, changes = self.snapshots(project)
        if any(changes.get(key, {}).get('observed_hash') != digest for key, digest in current.items()):
            raise ValueError('Providers changed again before deployment verification')
        deployed = self.source(project, refresh=True)
        if deployed != merge_sha:
            raise ValueError('Client main advanced beyond this deployment; refresh deployment evidence')
        for provider in project.providers:
            if provider.provider_id in current:
                with self.jobs.monitoring.store.transaction(provider.integration_id) as state:
                    if state['last_observation_hash'] != current[provider.provider_id]:
                        raise ValueError('Provider observation changed before acceptance')
                    state.update(baseline_hash=current[provider.provider_id], revision=state['revision']+1)
        self.update(project.project_id, record['workflow_id'], state='verified', deployed_sha=merge_sha, receipt=receipt)
