"""Explicit setup/export/reset commands; no hidden account or firewall changes."""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def environment_report(ports=(8002, 8100, 8101, 8102)):
    report = {'python': sys.version.split()[0], 'executables': {name: shutil.which(name) for name in ('git','gh','node','npm')}, 'ports': []}
    for port in ports:
        with socket.socket() as listener:
            try:
                listener.bind(('127.0.0.1', int(port)))
                available = True
            except OSError:
                available = False
        report['ports'].append({'port': port, 'available': available})
    return report


def export_client(repository):
    repository = Path(repository).resolve()
    target = repository / 'movie_booking'
    if target.exists() or target.is_symlink():
        raise ValueError('movie_booking already exists; refusing to overwrite client work')
    if (repository / 'requirements-cinema.txt').exists() or (repository / '.github/workflows/cinema-client.yml').exists():
        raise ValueError('CinemaFlow baseline file already exists')
    template = ROOT / 'demo/movie-client'
    shutil.copytree(template / 'movie_booking', target, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(template / 'tests', target / 'tests', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copyfile(template / 'requirements.txt', repository / 'requirements-cinema.txt')
    workflow = repository / '.github/workflows/cinema-client.yml'
    workflow.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template / '.github/workflows/ci.yml', workflow)
    ignore = repository / '.gitignore'
    with ignore.open('a', encoding='utf-8') as stream:
        stream.write('\n# CinemaFlow local runtime\n.venv/\n__pycache__/\n.pytest_cache/\n*.pyc\n')


def reset_rehearsal(directory):
    from demo.providers.state import Store
    directory = Path(directory)
    if directory.is_symlink() or not (directory / '.apishield-demo-state').is_file():
        raise ValueError('Reset requires a managed demo state directory')
    # Reset only the two named provider databases; never touch source or Git history.
    for name in ('payment', 'theatre'):
        path = directory / f'{name}.db'
        if path.is_symlink():
            raise ValueError('Unsafe provider database path')
        store = Store(path)
        with store.connect() as db:
            db.execute("UPDATE settings SET value='1' WHERE key='version'")
            db.execute('DELETE FROM payments')
            db.execute('DELETE FROM holds')


def configure_system_a(repository, provider_host, jobs_root, model):
    from apishield.browser_setup import read_registry
    from apishield.configuration import IntegrationConfig
    from apishield.dashboard_jobs import LocalJobs
    from apishield.jobs import _job_transaction, atomic_json
    from apishield.projects import ClientProject, ProviderBinding, combined_contract
    from apishield.automation import git
    import ipaddress
    ip = ipaddress.ip_address(provider_host)
    if ip.version != 4 or not (ip.is_private or ip.is_loopback) or ip.is_unspecified or ip.is_link_local or ip.is_multicast:
        raise ValueError('Use the second computer private Wi-Fi IPv4 address')
    repository = Path(repository).resolve()
    if not (repository / 'movie_booking/app.py').is_file():
        raise ValueError('Clone the merged CinemaFlow client baseline before configuring System A')
    if git(repository, 'status', '--porcelain'):
        raise ValueError('Commit or preserve client changes before configuring the demo')
    bindings = [ProviderBinding(name, 'cinema-' + name, f'http://{provider_host}:{port}', '', [f'movie_booking/{name}_client.py'])
                for name, port in [('theatre',8101),('payment',8102)]]
    jobs_root = Path(jobs_root).resolve()
    jobs_root.mkdir(parents=True, exist_ok=True)
    if jobs_root.is_relative_to(repository):
        raise ValueError('Keep APIShield state outside the client repository')
    project = ClientProject('cinemaflow', str(repository), bindings, target_repository='Surjithk73/APIGuardTesting', display_name='CinemaFlow Integration')
    docs = {name: json.loads((ROOT / f'demo/contracts/{name}-v1.json').read_text()) for name in ('theatre','payment')}
    with _job_transaction(jobs_root):
        registry = read_registry(jobs_root)
        if any(name in registry for name in ('cinemaflow','cinema-theatre','cinema-payment')):
            raise ValueError('CinemaFlow is already configured; use the existing settings instead of overwriting history')
        for name, document, code_paths in [(p.integration_id, docs[p.provider_id], p.source_files) for p in bindings] + [
                ('cinemaflow', combined_contract(docs), [f for p in bindings for f in p.source_files])]:
            directory = jobs_root / '_integrations' / name
            directory.mkdir(parents=True, exist_ok=True)
            atomic_json(directory / 'base.json', document)
            config = IntegrationConfig(repository, directory / 'base.json', directory / 'base.json', code_paths,
                test_commands=[['python','-m','pytest','movie_booking/tests','-q']], model=model,
                http_bindings=project.http_bindings() if name == 'cinemaflow' else {})
            atomic_json(directory / 'integration.json', config.to_dict())
            registry[name] = {'config': str(directory / 'integration.json'), 'example': False}
        atomic_json(jobs_root / 'integrations.json', registry)
    jobs = LocalJobs(jobs_root, {})
    try:
        jobs.automation.projects.save(project.to_dict(), 0)
        for binding in bindings:
            jobs.monitoring.configure(binding.integration_id, dict(source_url=binding.base_url+'/openapi.json',allow_local=True,
                interval_minutes=5,baseline_mode='saved',enabled=True), 0)
        # Authentication/publishing is still explicitly configured in the existing GitHub panel.
    finally:
        jobs.close()
    return {'project_id':'cinemaflow','jobs_root':str(jobs_root),'mode':'manual'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('check-environment')
    export = commands.add_parser('export-client'); export.add_argument('--repository',required=True)
    reset = commands.add_parser('reset'); reset.add_argument('--state',required=True)
    setup = commands.add_parser('system-a'); setup.add_argument('--repository',required=True); setup.add_argument('--provider-host',required=True)
    setup.add_argument('--jobs-root', default=str(Path.home()/'.apishield/jobs')); setup.add_argument('--model',default='gemini-2.5-flash')
    args = parser.parse_args()
    if args.command == 'check-environment':
        print(json.dumps(environment_report(),indent=2))
    elif args.command == 'export-client':
        export_client(args.repository)
        print('Client baseline exported; commit and publish it using the documented setup branch.')
    elif args.command == 'reset':
        reset_rehearsal(args.state)
        print('Dedicated provider state reset to V1. Client source and Git history were preserved.')
    else:
        print(json.dumps(configure_system_a(args.repository,args.provider_host,args.jobs_root,args.model),indent=2))


if __name__ == '__main__':
    main()
