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
DEMO_ROOT = ROOT / '.apishield/cinema'


def workspace_path(value):
    path = Path(value)
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if path == ROOT or not path.is_relative_to(ROOT):
        raise ValueError('Demo folders must stay inside the ProjectSeven folder')
    return path


def _lan_address(value):
    import ipaddress
    ip = ipaddress.ip_address(value)
    return ip.version == 4 and (ip.is_private or ip.is_loopback) and not (ip.is_unspecified or ip.is_link_local or ip.is_multicast)


def demo_address(value, client_port=8100):
    from urllib.parse import urlsplit
    if not isinstance(value, str) or any(ord(c) < 33 for c in value) or '\\' in value:
        raise ValueError('Paste the CinemaFlow HTTP link from System B')
    parts = urlsplit(value if '://' in value else 'http://' + value)
    if (parts.scheme != 'http' or not parts.hostname or parts.username is not None or parts.password is not None
            or parts.path not in {'','/'} or parts.query or parts.fragment):
        raise ValueError('Use a credential-free LAN HTTP origin, without a path or query')
    port = parts.port if parts.port is not None else client_port
    if not 1 <= port <= 65535:
        raise ValueError('Use a valid client port')
    try:
        addresses = {entry[4][0] for entry in socket.getaddrinfo(parts.hostname, port, socket.AF_INET, socket.SOCK_STREAM)}
    except OSError as error:
        raise ValueError('System B hostname could not be resolved; use an alternative link printed on B') from error
    if not addresses or not all(_lan_address(ip) for ip in addresses):
        raise ValueError('The CinemaFlow link must resolve to a trusted IPv4 LAN address')
    return parts.hostname, port


def connection_info(client_port=8100, theatre_port=8101, payment_port=8102):
    service_ports(client_port, theatre_port, payment_port)
    hostname = socket.gethostname()
    hosts = [hostname]
    try:
        hosts += sorted({entry[4][0] for entry in socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
                         if _lan_address(entry[4][0]) and not entry[4][0].startswith('127.')})
    except OSError:
        pass
    return {'scope':'LAN', 'local_url':f'http://127.0.0.1:{client_port}', 'connections':[
        {'client_url':f'http://{host}:{client_port}', 'theatre_url':f'http://{host}:{theatre_port}',
         'payment_url':f'http://{host}:{payment_port}'} for host in dict.fromkeys(hosts)]}


def service_ports(client_port=8100, theatre_port=8101, payment_port=8102):
    ports = tuple(int(p) for p in (client_port, theatre_port, payment_port))
    if len(set(ports)) != 3 or any(p < 1 or p > 65535 for p in ports):
        raise ValueError('Demo ports must be distinct values between 1 and 65535')
    return ports


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
    repository = workspace_path(repository)
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
    directory = workspace_path(directory)
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


def configure_system_a(repository, provider_host, jobs_root, model, client_port=8100, theatre_port=8101, payment_port=8102):
    client_port, theatre_port, payment_port = service_ports(client_port, theatre_port, payment_port)
    from apishield.browser_setup import read_registry
    from apishield.configuration import IntegrationConfig
    from apishield.dashboard_jobs import LocalJobs
    from apishield.jobs import _job_transaction, atomic_json
    from apishield.projects import ClientProject, ProviderBinding, combined_contract
    from apishield.automation import git
    provider_host, client_port = demo_address(provider_host, client_port)
    service_ports(client_port, theatre_port, payment_port)
    repository = workspace_path(repository)
    if not (repository / 'movie_booking/app.py').is_file():
        raise ValueError('Clone the merged CinemaFlow client baseline before configuring System A')
    if git(repository, 'status', '--porcelain'):
        raise ValueError('Commit or preserve client changes before configuring the demo')
    bindings = [ProviderBinding(name, 'cinema-' + name, f'http://{provider_host}:{port}', '', [f'movie_booking/{name}_client.py'])
                for name, port in [('theatre',theatre_port),('payment',payment_port)]]
    jobs_root = workspace_path(jobs_root)
    if jobs_root.is_relative_to(repository):
        raise ValueError('Keep APIShield state outside the client repository')
    jobs_root.mkdir(parents=True, exist_ok=True)
    project = ClientProject('cinemaflow', str(repository), bindings, target_repository='Surjithk73/APIGuardTesting', display_name='CinemaFlow Integration', deployment_actor='surjk73', client_url=f'http://{provider_host}:{client_port}')
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
    links = commands.add_parser('connection-info')
    validate = commands.add_parser('validate-path'); validate.add_argument('--path',required=True)
    export = commands.add_parser('export-client'); export.add_argument('--repository',required=True)
    reset = commands.add_parser('reset'); reset.add_argument('--state',required=True)
    setup = commands.add_parser('system-a'); setup.add_argument('--repository',required=True); setup.add_argument('--provider-host',required=True)
    setup.add_argument('--jobs-root', default=str(DEMO_ROOT / 'jobs')); setup.add_argument('--model',default='gemini-3.8-flash')
    for name, port in [('client',8100),('theatre',8101),('payment',8102)]:
        setup.add_argument('--' + name + '-port', type=int, default=port)
        links.add_argument('--' + name + '-port', type=int, default=port)
    args = parser.parse_args()
    if args.command == 'check-environment':
        print(json.dumps(environment_report(),indent=2))
    elif args.command == 'connection-info':
        print(json.dumps(connection_info(args.client_port,args.theatre_port,args.payment_port),indent=2))
    elif args.command == 'validate-path':
        print(workspace_path(args.path))
    elif args.command == 'export-client':
        export_client(args.repository)
        print('Client baseline exported; commit and publish it using the documented setup branch.')
    elif args.command == 'reset':
        reset_rehearsal(args.state)
        print('Dedicated provider state reset to V1. Client source and Git history were preserved.')
    else:
        print(json.dumps(configure_system_a(args.repository,args.provider_host,args.jobs_root,args.model,args.client_port,args.theatre_port,args.payment_port),indent=2))


if __name__ == '__main__':
    main()
