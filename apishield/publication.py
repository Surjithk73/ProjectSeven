"""Explicit prepare/publish/reconcile lifecycle shared by browser and CLI."""
import hashlib
import json
import re
import shutil
import threading
import time
import uuid
from urllib.parse import quote

from .github_cli import GhClient,GitHubError
from .jobs import JobCancelled,timestamp
from .publication_prepare import prepare_repair,retained_patch,evidence_hash
from .publication_state import PublicationStore,PublicationConflict,proposal_identity


class PublicationError(ValueError):pass


def _digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def _summary(prepared,identity,target=None):
    def text(value):
        value=str(value)
        from .commands import redact
        value=redact(value)
        value=re.sub(r'(?i)\b(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s+(?:https?://github\.com/[\w.-]+/[\w.-]+/issues/\d+|(?:[\w.-]+/[\w.-]+)?#\d+)','[issue reference omitted]',value)
        value=re.sub(r'(?:\b[A-Za-z]:[\\/]|/(?:Users|home|tmp|var|private|mnt|srv|opt|workspaces)/)[^\s`]+','[local path omitted]',value)
        return value.replace('\r',' ').replace('\n',' ')[:2000]
    title=f'[APIShield] Repair {len(prepared["files"])} API integration source file(s)'
    lines=['This draft proposes the complete locally validated API migration.','',
        f'Base: `{prepared["source_commit"]}`',f'Patch SHA256: `{prepared["patch_sha256"]}`',
        f'Local repair: `{prepared["source_job_id"]}`',f'Offline revalidation: `{prepared["verification_job_id"]}`','',
        'Changed source files:',*['- `'+file['path']+'`' for file in prepared['files']],'',
        f'Local validation: passed {prepared["validation"]["test_commands"]} configured test command(s).',
        f'Proposal source: {prepared["validation"].get("proposal_source","unavailable")}',
        'GitHub CI: not verified','',
        'Confirmed requirement checks:']
    rules=prepared['validation']['requirements']
    lines.extend('- '+text(rule['id'])+': '+text(rule['description'])+' — '+text(rule['status'])+'; checks: '+', '.join('`'+text(check)+'`' for check in (rule['checks'] or [])) for rule in rules)
    if not rules:lines.append('No confirmed requirement checks were selected for this repair.')
    connection=prepared['validation'].get('model_connection')
    if connection and prepared['validation'].get('proposal_source')=='model':
        lines.extend(['',f'Model: `{text(connection.get("model","unavailable"))}`; provider: `{text(connection.get("provider","unavailable"))}`'])
    if (prepared['validation'].get('generation_guidance') or {}).get('kind') == 'prewritten_demo_reference':
        lines.extend(['','Guided demonstration: generation included a prewritten reference patch. This is not an unseeded evaluation run.'])
    lines.extend(['','Human review is required before merging. Local validation does not establish complete semantic correctness.',
                  '',f'<!-- APIShield proposal {identity} -->'])
    return title,'\n'.join(lines)


class PublicationService:
    def __init__(self,jobs,github=None):
        self.jobs=jobs;self.github=github
        self.store=PublicationStore(jobs.store.root)
        self.lock=threading.RLock();self.active={};self.closed=False
        for record in self.store.list():
            if record['status'] in {'preparing','publishing','reconciling'}:
                with self.store.ownership(record['id']) as owned:
                    if owned:
                        self.store.update(record['id'],status='reconciliation_needed' if record['status']!='preparing' else 'failed',
                            error='Operation interrupted; reconcile remote publication or prepare again explicitly.')
                        verification=record.get('verification_job_id')
                        if record['status']=='preparing' and verification:
                            try:
                                from .engine import _execution_lock
                                from .jobs import atomic_json
                                path=self.jobs.store._path(verification)
                                with _execution_lock(path) as worker_owned:
                                    value=self.jobs.store.get(verification)
                                    if worker_owned and value['status'] in {'queued','running'}:
                                        self.jobs.store.cancel(verification)
                                        atomic_json(path/'result.json',{**value,'status':'failed','error':'Publication verification interrupted; prepare again explicitly.'})
                                        (path/'candidate.patch').unlink(missing_ok=True)
                                    if worker_owned:
                                        workspace=path/'workspace'
                                        if workspace.is_symlink():workspace.unlink()
                                        elif workspace.exists():
                                            if workspace.resolve().parent!=path.resolve():raise PublicationError('Unsafe verification workspace')
                                            shutil.rmtree(workspace)
                            except FileNotFoundError:pass

    def configure(self,integration,repository,base,expected_revision):
        if integration not in self.jobs.integrations:raise KeyError('Unknown integration')
        current=self.store.read_target(integration)
        if current['revision']!=expected_revision:raise PublicationConflict('GitHub target changed; refresh and prepare again')
        target=(self.github or GhClient()).inspect_target(repository,base,deadline=time.monotonic()+45)
        return self.store.save_target(integration,target,expected_revision)

    def _target(self,record):
        target=self.store.read_target(record['integration'])
        if target['revision']!=record['target_revision'] or target.get('repository')!=record['target']['repository'] or target.get('base')!=record['target']['base']:
            raise PublicationConflict('GitHub target changed; prepare a current proposal')
        return target

    def _check(self,record,deadline):
        if self.closed or self.jobs.closed or self.store.read(record['id'])['cancel_requested']:
            raise JobCancelled('Publication preparation cancelled or application stopped')
        if time.monotonic()>=deadline:raise PublicationError('Publication exceeded its 180-second deadline')
        self._target(record)
        context = self.jobs.store.get(record['source_job_id']).get('project_workflow')
        if context:
            workflows = self.jobs.automation.projects.workflows(context['project_id'])
            workflow = next((item for item in workflows if item['workflow_id'] == context['workflow_id']), None)
            if not workflow or workflow['state'] in {'superseded','failed','closed','verified'}:
                raise PublicationConflict('Client workflow was superseded or stopped; no stale publication is allowed')
            project = self.jobs.automation.projects.load_project(context['project_id'])
            _, changes = self.jobs.automation.snapshots(project)
            if changes != context['providers']:
                raise PublicationConflict('Provider snapshots changed; regenerate the combined update before publication')

    def _artifacts(self,record):
        result,patch=retained_patch(self.jobs.store,record['source_job_id'])
        if result['source_commit']!=record['source_commit'] or result['patch_sha256']!=record['patch_sha256']:
            raise PublicationError('Repair evidence changed after preparation')
        prepared=record.get('prepared')
        if prepared:
            verified=self.jobs.store.get(prepared['verification_job_id'])
            if verified['status']!='validated' or evidence_hash(self.jobs.store,prepared['verification_job_id'])!=prepared['evidence_sha256'] or _digest(prepared)!=record['prepared_hash'] or _digest([record['title'],record['body']])!=record['review_hash']:
                raise PublicationError('Offline verification evidence changed; prepare again')
        return result

    def _base(self,record,client,deadline):
        self._target(record)
        target=client.inspect_target(record['target']['repository'],record['target']['base'],deadline=deadline)
        self._target(record)
        if target['source_commit']!=record['source_commit']:
            raise PublicationConflict('Remote base advanced or differs from the pinned repair; regenerate the repair')
        if target['account']!=record['target']['account']:
            raise PublicationConflict('GitHub CLI account changed after preview; reconfigure and prepare again')
        return target

    def _queue(self,identity,operation,record=None,*,expected_revision=None):
        with self.lock:
            if self.closed or self.jobs.closed:raise PublicationError('Publication service is shutting down')
            ownership=self.store.ownership(identity);owned=ownership.__enter__()
            if not owned:
                ownership.__exit__(None,None,None)
                return self.store.read(identity)
            try:
                if operation=='publish':
                    current=self.store.read(identity)
                    if current['status'] in {'published','publishing','reconciling'}:
                        ownership.__exit__(None,None,None);return current
                    if current['status']!='ready':raise PublicationError('Prepare or reconcile a ready proposal before publication')
                    if current['revision']!=expected_revision:raise PublicationConflict('Proposal revision changed; review its current preview')
                    self._target(current);self._artifacts(current)
                if record is not None:
                    existing=self.store.reserve(identity,record)
                    if existing['created_at']!=record['created_at'] and (existing['status'] in {'published','preparing','publishing','reconciling','reconciliation_needed'} or existing['effects']):
                        ownership.__exit__(None,None,None);return existing
                    if existing['created_at']!=record['created_at']:
                        record['revision']=existing.get('revision',0)+1
                        with self.store.transaction(identity) as state:state.clear();state.update(record)
                self.store.update(identity,status={'prepare':'preparing','publish':'publishing','reconcile':'reconciling'}[operation],
                                  phase=operation+'_reserved',error=None,cancel_requested=False)
                future=self.jobs.executor.submit(self._worker,identity,operation,ownership)
                self.active[identity]=(future,ownership,operation)
            except Exception:
                ownership.__exit__(None,None,None)
                raise
            return self.store.read(identity)

    def prepare(self,integration,job_id,expected_revision):
        if integration not in self.jobs.integrations:raise KeyError('Unknown integration')
        target=self.store.read_target(integration)
        if not target['configured']:raise PublicationError('Configure an existing GitHub repository/base first')
        if target['revision']!=expected_revision:raise PublicationConflict('GitHub target changed; refresh and prepare again')
        result,patch=retained_patch(self.jobs.store,job_id)
        if result.get('integration') not in {None,integration}:raise PublicationError('Repair belongs to another integration')
        identity=proposal_identity(target['repository'],target['base'],result['source_commit'],result['patch_sha256'])
        record={'version':1,'revision':0,'id':identity,'integration':integration,'source_job_id':job_id,'source_commit':result['source_commit'],
            'patch_sha256':result['patch_sha256'],'target':target,'target_revision':expected_revision,
            'branch':'codex/apishield-'+identity[:24],'status':'preparing','phase':'prepare_reserved','prepared':None,
            'prepared_hash':None,'review_hash':None,'verification_job_id':None,'title':None,'body':None,'commit':None,'publication':None,'effects':[],
            'error':None,'cancel_requested':False,'created_at':timestamp(),'updated_at':timestamp()}
        return self._queue(identity,'prepare',record)

    def publish(self,identity,expected_revision):
        record=self.store.read(identity)
        if record['status']=='published':return record
        if record['status'] in {'publishing','reconciling'}:return record
        if record['status']!='ready':raise PublicationError('Prepare or reconcile a ready proposal before publication')
        if record['revision']!=expected_revision:raise PublicationConflict('Proposal revision changed; review its current preview')
        self._target(record);self._artifacts(record)
        return self._queue(identity,'publish',expected_revision=expected_revision)

    def reconcile(self,identity):
        record=self.store.read(identity)
        if record['status'] in {'preparing','publishing','reconciling'}:return record
        if not record.get('prepared'):raise PublicationError('No prepared publication to reconcile')
        return self._queue(identity,'reconcile')

    def cancel_prepare(self,identity):
        record=self.store.read(identity)
        if record['status']!='preparing':raise PublicationError('Only local preparation can be cancelled; reconcile remote effects instead')
        return self.store.update(identity,cancel_requested=True)

    def _worker(self,identity,operation,ownership):
        deadline=time.monotonic()+180
        try:
            record=self.store.read(identity)
            if operation=='prepare':self._prepare(record,deadline)
            elif operation=='publish':self._publish(record,deadline)
            else:self._reconcile(record,deadline)
        except Exception as error:
            record=self.store.read(identity)
            status='stale' if isinstance(error,PublicationConflict) else 'cancelled' if isinstance(error,JobCancelled) and operation=='prepare' else 'reconciliation_needed' if operation!='prepare' and record.get('effects') else 'failed'
            message=str(error) if isinstance(error,(PublicationConflict,PublicationError,GitHubError,JobCancelled)) else 'Publication operation did not complete; inspect local evidence and reconcile remote state before retrying.'
            self.store.update(identity,status=status,error=message)
        finally:
            ownership.__exit__(None,None,None)
            with self.lock:self.active.pop(identity,None)

    def _prepare(self,record,deadline):
        check=lambda:self._check(record,deadline)
        check();self._artifacts(record)
        client=self.github or GhClient()
        self._base(record,client,deadline)
        verification=uuid.uuid4().hex
        self.store.update(record['id'],verification_job_id=verification)
        prepared=prepare_repair(self.jobs.store,record['source_job_id'],check,verification_job_id=verification)
        check();self._base(record,client,deadline)
        title,body=_summary(prepared,record['id'],record['target'])
        workflow = self.jobs.store.get(record['source_job_id']).get('project_workflow')
        if workflow:
            body += '\n\n<!-- APIShield workflow ' + json.dumps(workflow, sort_keys=True, separators=(',', ':')) + ' -->'
        self.store.update(record['id'],status='ready',phase='prepared',revision=record['revision']+1,prepared=prepared,
                          prepared_hash=_digest(prepared),review_hash=_digest([title,body]),title=title,body=body)

    def _branch(self,record,client,deadline):
        try:
            data=client.api('GET',f'repos/{record["target"]["repository"]}/git/ref/heads/{quote(record["branch"],safe="/")}',None,deadline=deadline)
        except GitHubError as error:
            if error.code==404:return None
            raise
        expected=record.get('commit')
        if not expected or data['object']['sha']!=expected['sha']:
            raise PublicationError('GitHub branch collision; existing branch was left unchanged')
        return data['object']['sha']

    def _publish(self,record,deadline):
        identity=record['id'];check=lambda:self._check(record,deadline)
        check();self._artifacts(record)
        def effect(stage,endpoint,data):
            if stage=='before':
                check();self._artifacts(record)
            with self.store.transaction(identity) as state:
                state['phase']=endpoint
                state['effects'].append({'stage':stage,'endpoint':endpoint,'sha':data.get('sha',data.get('commit')) if isinstance(data,dict) else None})
        client=self.github or GhClient(effect=effect)
        self._branch(record,client,deadline)
        marker=f'APIShield proposal {identity}'
        if record.get('commit'):
            existing=client.find_publication(record['target'],record['branch'],{'sha':record['commit']['sha'],'marker':marker},deadline=deadline)
            if existing:self.store.update(identity,status='published',phase='published',publication=existing);return
        target=self._base(record,client,deadline)
        if not record.get('commit'):
            effect('before','commit',None)
            commit=client.create_source_commit(target,record['prepared']['files'],f'APIShield repair {identity}',deadline=deadline,check=check)
            self.store.update(identity,commit=commit)
            record['commit']=commit
            effect('after','commit',commit)
        check();self._artifacts(record);self._base(record,client,deadline)
        effect('before','branch',None)
        client.ensure_branch(target,record['branch'],record['commit'],deadline=deadline)
        effect('after','branch',record['commit'])
        check();self._artifacts(record);self._base(record,client,deadline)
        existing=client.find_publication(record['target'],record['branch'],{'sha':record['commit']['sha'],'marker':marker},deadline=deadline)
        if not existing:
            effect('before','draft_pr',None)
            body = record['body']
            if '<!-- APIShield workflow ' in body:
                body += '\n<!-- APIShield candidate ' + record['commit']['sha'] + ' -->'
            existing=client.create_draft(target['repository'],target['base'],record['branch'],record['title'],body,deadline=deadline)
        if existing['commit']!=record['commit']['sha']:raise PublicationError('Remote draft commit did not match the reviewed proposal')
        self.store.update(identity,status='published',phase='published',publication=existing)

    def _reconcile(self,record,deadline):
        client=self.github or GhClient()
        self._branch(record,client,deadline)
        existing=None
        if record.get('commit'):existing=client.find_publication(record['target'],record['branch'],{'sha':record['commit']['sha'],'marker':f'APIShield proposal {record["id"]}'},deadline=deadline)
        if existing:self.store.update(record['id'],status='published',phase='published',publication=existing)
        else:
            self._check(record,deadline);self._artifacts(record);self._base(record,client,deadline)
            self.store.update(record['id'],status='ready',phase='reconciled',error=None)

    def close(self):
        with self.lock:
            self.closed=True
            for identity,(future,ownership,operation) in list(self.active.items()):
                if future.cancel():
                    self.store.update(identity,status='cancelled' if operation=='prepare' else 'reconciliation_needed',error='App stopped before operation ran')
                    ownership.__exit__(None,None,None);self.active.pop(identity,None)
