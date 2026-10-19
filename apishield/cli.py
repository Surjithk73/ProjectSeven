"""Local engine commands; adapters do not parse subprocess log messages."""
import argparse
import json
from pathlib import Path
import sys

from .configuration import load_config
from .jobs import JobStore


def parser():
    result = argparse.ArgumentParser(prog='apishield', description='Inspect Python API integrations in disposable, commit-pinned jobs.')
    commands = result.add_subparsers(dest='command', required=True)
    proposal = commands.add_parser('proposal')
    actions = proposal.add_subparsers(dest='proposal_action',required=True)
    for action in ('prepare','publish','reconcile','report'):
        command = actions.add_parser(action)
        command.add_argument('identity')
        command.add_argument('--jobs-dir',type=Path,default=Path.home()/'.apishield/jobs')
        if action=='prepare':
            command.add_argument('--repository',required=True)
            command.add_argument('--base',required=True)
    for operation in ('scan', 'compare', 'repair', 'report', 'cancel'):
        command = commands.add_parser(operation)
        command.add_argument('--jobs-dir', type=Path, default=Path.home() / '.apishield' / 'jobs')
        if operation in ('report', 'cancel'):
            command.add_argument('job_id')
        else:
            command.add_argument('--config', type=Path, required=True)
        if operation == 'repair':
            command.add_argument('--candidate', type=Path, help='Explicit offline candidate JSON; never falls back to inference.')
            command.add_argument('--provider',choices=['google_cloud'])
            command.add_argument('--credentials',type=Path,help='Explicit service-account JSON for Google Cloud')
    return result


def main(argv=None):
    command_parser = parser()
    arguments = command_parser.parse_args(argv)
    if arguments.command=='repair':
        if arguments.candidate and (arguments.provider or arguments.credentials):
            command_parser.error('Offline candidates cannot be combined with model connection flags')
        if (arguments.provider=='google_cloud') != bool(arguments.credentials):
            command_parser.error('Google Cloud requires --credentials; credentials are only valid with --provider google_cloud')
    store = JobStore(arguments.jobs_dir)
    job = None
    try:
        if arguments.command == 'proposal':
            from .publication_cli import execute
            result = execute(arguments)
        elif arguments.command == 'report':
            from .engine import recover_interrupted
            result = recover_interrupted(store, arguments.job_id)
        elif arguments.command == 'cancel':
            result = store.cancel(arguments.job_id)
        else:
            config = load_config(arguments.config)
            connection = None
            if arguments.command=='repair' and not arguments.candidate:
                from .model_access import file_connection,environment_connection
                connection = file_connection(arguments.credentials) if arguments.provider=='google_cloud' else environment_connection()
            from .engine import run_job
            job = store.create(config, arguments.command)
            result = run_job(config, arguments.command, store,
                             candidate_path=getattr(arguments, 'candidate', None), job=job,model_connection=connection)
    except KeyboardInterrupt:
        if job is None:
            result = {'status': 'cancelled', 'error': 'Interrupted before job allocation'}
        else:
            store.cancel(job.id)
            result = job.finish({'status': 'cancelled', 'error': 'Interrupted from CLI'})
            job.cleanup()
    except Exception as error:
        if job is None:
            result = {'status': 'error', 'error': str(error)}
        else:
            result = job.finish({'status': 'failed', 'error': str(error)})
            job.cleanup()
    print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    return {'failed': 1, 'stale':2,'reconciliation_needed':2,'needs_input': 2, 'cancelled': 130, 'error': 2}.get(result.get('status'), 0)


if __name__ == '__main__':
    sys.exit(main())
