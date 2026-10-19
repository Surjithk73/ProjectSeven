"""Own the independent System B processes; stop only children started here."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

from apishield.engine import _execution_lock
from apishield.jobs import atomic_json
from .setup import ROOT, DEMO_ROOT, environment_report, service_ports, workspace_path, connection_info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', default=str(DEMO_ROOT / 'providers'))
    parser.add_argument('--stop', action='store_true')
    parser.add_argument('--client-repository')
    parser.add_argument('--deployment-config')
    parser.add_argument('--host', choices=['127.0.0.1','0.0.0.0'], default='0.0.0.0')
    for name, port in [('client',8100),('theatre',8101),('payment',8102)]:
        parser.add_argument('--' + name + '-port', type=int, default=port)
    args = parser.parse_args()
    root = workspace_path(args.state)
    root.mkdir(parents=True, exist_ok=True)
    if args.stop:
        if not (root / '.apishield-demo-state').is_file():
            raise ValueError('Not a managed CinemaFlow runtime')
        (root / 'stop.request').touch()
        return
    with _execution_lock(root) as owned:
        if not owned:
            raise ValueError('A CinemaFlow runtime already owns this state folder')
        client_port, theatre_port, payment_port = service_ports(args.client_port, args.theatre_port, args.payment_port)
        if args.deployment_config:
            from urllib.parse import urlsplit
            config_path = workspace_path(args.deployment_config)
            config = json.loads(config_path.read_text(encoding='utf-8'))
            workspace_path(config['releases'])
            provider_urls = [urlsplit(config['providers'][name]) for name in ('theatre', 'payment')]
            if any(url.scheme != 'http' or url.hostname not in {'127.0.0.1', 'localhost'} for url in provider_urls):
                raise ValueError('Managed System B providers must use local HTTP URLs')
            client_port, theatre_port, payment_port = service_ports(config.get('client_port',8100), *(url.port or 80 for url in provider_urls))
        ports = (theatre_port,payment_port) if args.deployment_config else (client_port,theatre_port,payment_port)
        if any(not p['available'] for p in environment_report(ports)['ports']):
            raise ValueError('A demo port is occupied; stop the managed demo or choose free ports before starting')
        (root / '.apishield-demo-state').touch()
        (root / 'stop.request').unlink(missing_ok=True)
        environment = {**os.environ,'CINEMA_STATE_DIR':str(root),'CINEMA_PAYMENT_URL':f'http://127.0.0.1:{payment_port}',
            'CINEMA_THEATRE_URL':f'http://127.0.0.1:{theatre_port}','PYTHONPATH':str(ROOT),'CINEMA_INSTANCE_ID':uuid.uuid4().hex}
        processes = []
        trees = []
        def start(label, argv, cwd=ROOT, env=None):
            from apishield.commands import _WindowsTree
            tree = _WindowsTree() if os.name == 'nt' else None
            log = (root / (label+'.log')).open('ab')
            try:
                process = subprocess.Popen([sys.executable,*argv],cwd=cwd,env=env or environment,stdout=log,stderr=log,
                    start_new_session=os.name != 'nt',
                    creationflags=(subprocess.CREATE_NO_WINDOW | 0x4) if os.name=='nt' else 0)
                processes.append(process)
                if tree:
                    tree.attach_and_resume(process)
                trees.append(tree)
            finally:
                log.close()
        try:
            for name,port in [('theatre',theatre_port),('payment',payment_port)]:
                start(name,['-m','uvicorn',f'demo.providers.{name}:create_app','--factory','--host',args.host,'--port',str(port)])
            if args.deployment_config:
                start('deployment',['-m','demo.deployment.agent','--config',str(Path(args.deployment_config).resolve()),'--bootstrap'])
            else:
                client = workspace_path(args.client_repository) if args.client_repository else ROOT/'demo/movie-client'
                if not (client/'movie_booking/app.py').is_file():
                    raise ValueError('Movie client source is absent from the selected directory')
                client_env = {**environment,'PYTHONPATH':str(client)}
                start('client',['-m','uvicorn','movie_booking.app:create_app','--factory','--host',args.host,'--port',str(client_port)],client,client_env)
            atomic_json(root/'connection-info.json', connection_info(client_port,theatre_port,payment_port))
            atomic_json(root/'runtime.json',{'pid':os.getpid(),'children':[p.pid for p in processes]})
            while not (root/'stop.request').exists():
                if any(p.poll() is not None for p in processes):
                    raise ValueError('A demo process exited; inspect its log in the runtime state folder')
                time.sleep(1)
        finally:
            for process in processes:
                if process.poll() is None:
                    process.terminate()
            for tree in trees:
                if tree:
                    tree.stop()
            for process in processes:
                process.wait(timeout=15)


if __name__ == '__main__':
    main()
