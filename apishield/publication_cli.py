"""CLI adapter to the same durable publication coordinator as the browser."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import time
from types import SimpleNamespace

from .jobs import JobStore
from .publication import PublicationService
from .publication_state import PublicationStore


def open_service(root,job_id, integration=None):
    store=JobStore(root)
    result=store.get(job_id)
    name=integration or result.get('integration') or 'cli-'+hashlib.sha256(job_id.encode()).hexdigest()[:24]
    jobs=SimpleNamespace(store=store,integrations={name:str(store._path(job_id)/'config.json')},
                         executor=ThreadPoolExecutor(max_workers=1),closed=False)
    return PublicationService(jobs)


def wait(publisher,identity):
    deadline=time.monotonic()+190
    while time.monotonic()<deadline:
        record=publisher.store.read(identity)
        if record['status'] not in {'preparing','publishing','reconciling'}:return record
        time.sleep(.1)
    raise ValueError('Operation still pending; use proposal report or reconcile')


def execute(arguments):
    state=PublicationStore(arguments.jobs_dir)
    if arguments.proposal_action=='report':return state.read(arguments.identity)
    record=None if arguments.proposal_action=='prepare' else state.read(arguments.identity)
    publisher=open_service(arguments.jobs_dir,arguments.identity if record is None else record['source_job_id'],
                           **({'integration':record['integration']} if record else {}))
    try:
        if record is None:
            integration=next(iter(publisher.jobs.integrations))
            target=publisher.store.read_target(integration)
            if not target['configured'] or target.get('repository')!=arguments.repository or target.get('base')!=arguments.base:
                target=publisher.configure(integration,arguments.repository,arguments.base,target['revision'])
            record=publisher.prepare(integration,arguments.identity,target['revision'])
        elif arguments.proposal_action=='publish':record=publisher.publish(record['id'],record['revision'])
        else:record=publisher.reconcile(record['id'])
        return wait(publisher,record['id'])
    finally:
        publisher.close()
        publisher.jobs.executor.shutdown(wait=True,cancel_futures=True)
