"""One-laptop orchestration profile; phone is a browser and human reviewer."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from apishield.github_cli import GhClient, GitHubError
from apishield.jobs import atomic_json
from .setup import DEMO_ROOT, configure_system_a, service_ports, workspace_path, connection_info

REPOSITORY = 'Surjithk73/APIGuardTesting'
PUBLISHER = 'Surjithk73'
REVIEWER = 'surjk73'


def phone_configuration(root=None, publisher=PUBLISHER, client_port=8100, theatre_port=8101, payment_port=8102):
    if publisher.casefold() != PUBLISHER.casefold():
        raise ValueError('Use the existing laptop publisher account Surjithk73; the phone reviewer is separate')
    client_port, theatre_port, payment_port = service_ports(client_port,theatre_port,payment_port)
    root = workspace_path(root or DEMO_ROOT/'phone')
    return {'root':str(root), 'source':str(root/'client-source'), 'jobs':str(root/'jobs'),
        'state':str(root/'providers'), 'reviewer':REVIEWER, 'config':str(root/'deployment.json'),
        'deployment':{'project_id':'cinemaflow','repository':REPOSITORY,'base':'main','publisher':PUBLISHER,
            'deployment_actor':PUBLISHER,'client_port':client_port,'releases':str(root/'releases'),
            'providers':{'theatre':f'http://127.0.0.1:{theatre_port}','payment':f'http://127.0.0.1:{payment_port}'}},
        'links':connection_info(client_port,theatre_port,payment_port)}


def git(directory,*args):
    result=subprocess.run(['git','-C',str(directory),*args],capture_output=True,text=True,timeout=90,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if result.returncode:
        raise ValueError('Client source operation failed: '+result.stderr.strip()[:600])
    return result.stdout.strip()


def prepare_source(directory,branch):
    directory=workspace_path(directory)
    if not directory.exists():
        directory.parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(['git','clone','--branch',branch,f'https://github.com/{REPOSITORY}.git',str(directory)],
            capture_output=True,text=True,timeout=90,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        if result.returncode: raise ValueError('Could not clone the demo client; check GitHub connectivity')
    if git(directory,'status','--porcelain'):
        raise ValueError('Phone demo client source has local changes; preserve them before starting')
    if git(directory,'remote','get-url','origin').rstrip('/').removesuffix('.git').casefold()!=f'https://github.com/{REPOSITORY}'.casefold():
        raise ValueError('Phone demo source has an unexpected remote; it was left unchanged')
    git(directory,'fetch','origin')
    git(directory,'checkout','--detach','origin/'+branch)
    if not (directory/'movie_booking/app.py').is_file():
        raise ValueError('CinemaFlow client baseline is missing; review setup PR #2')


def prepare_phone_demo(root=None,github=None):
    github=github or GhClient()
    deadline=time.monotonic()+45
    account=github.api('GET','user',None,deadline=deadline)
    if account['login'].casefold()!=PUBLISHER.casefold():
        raise ValueError('Keep the laptop signed in as Surjithk73. Review as surjk73 on the phone.')
    profile=phone_configuration(root)
    from .phone_reset import rehearsal_settings
    rehearsal=rehearsal_settings(Path(profile['root']))
    base=rehearsal['base'] if rehearsal else 'main'
    profile['deployment']['base']=base
    try:
        github.api('GET',f'repos/{REPOSITORY}/contents/movie_booking/app.py?ref={base}',None,deadline=deadline)
        mode='deployment';branch=base
        message='Merged-release deployment enabled. Review migration PRs as surjk73 on the phone.'
        if rehearsal: message+=f' Rehearsal PR target: {base}.'
    except GitHubError as error:
        if error.code!=404 or rehearsal: raise
        mode='preview';branch='feature/cinemaflow-client'
        message='Preview only: review and merge setup PR #2 as surjk73, wait for main CI, then restart this launcher to enable deployment.'
    source=Path(profile['source'])
    prepare_source(source,branch)
    from apishield.project_store import ProjectStore
    store=ProjectStore(profile['jobs'])
    try:
        project=store.load_project('cinemaflow')
    except KeyError:
        configure_system_a(source,'http://127.0.0.1:8100',profile['jobs'],'gemini-3.8-flash',deployment_actor=PUBLISHER)
        project=store.load_project('cinemaflow')
    if Path(project.repository).resolve()!=source.resolve() or any(p.base_url not in profile['deployment']['providers'].values() for p in project.providers):
        raise ValueError('Existing phone project settings differ from this profile; nothing was overwritten')
    if project.deployment_actor!=PUBLISHER or project.base_branch!=base:
        project.deployment_actor=PUBLISHER
        project.base_branch=base
        store.save(project.to_dict(),project.revision)
    if mode=='deployment':
        from apishield.dashboard_jobs import LocalJobs
        jobs=LocalJobs(profile['jobs'],{})
        try:
            jobs.publication.github=github
            target=jobs.publication.store.read_target('cinemaflow')
            if not target['configured']:
                jobs.publication.configure('cinemaflow',REPOSITORY,base,target['revision'])
            elif target['base']!=base:
                raise ValueError('GitHub target differs from the rehearsal branch; reset or inspect project settings')
        finally:
            jobs.close()
    profile.update(mode=mode,message=message,source_sha=git(source,'rev-parse','HEAD'))
    atomic_json(Path(profile['config']),profile['deployment'])
    atomic_json(Path(profile['root'])/'profile.json',profile)
    return profile


def run_phone_demo(root=None,api_port=8005,no_browser=False):
    from apishield.engine import _execution_lock
    from .phone_reset import control_directory
    root=workspace_path(root or DEMO_ROOT/'phone')
    with _execution_lock(control_directory(root)) as owned:
        if not owned:
            print('The phone demo is already running or resetting. Use Stop Phone Demo.bat before restarting.',flush=True)
            return
        _run_phone_demo(root,api_port,no_browser)


def _run_phone_demo(root,api_port,no_browser):
    import sys
    import webbrowser
    import httpx
    from apishield.engine import _execution_lock
    from apishield.commands import _WindowsTree
    from .setup import ROOT, environment_report
    root=workspace_path(root or DEMO_ROOT/'phone')
    root.mkdir(parents=True,exist_ok=True)
    with _execution_lock(root) as owned:
        if not owned:
            print('The phone demo is already running. Use the links in '+str(root/'profile.json'),flush=True)
            return
        (root/'.phone-demo').touch()
        (root/'stop.request').unlink(missing_ok=True)
        environment={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(ROOT),
            'TEMP':str(DEMO_ROOT/'temp'),'TMP':str(DEMO_ROOT/'temp'),'PIP_CACHE_DIR':str(DEMO_ROOT/'cache/pip')}
        Path(environment['TEMP']).mkdir(parents=True,exist_ok=True)
        os.environ.update({k:environment[k] for k in ('TEMP','TMP','PIP_CACHE_DIR','PYTHONDONTWRITEBYTECODE')})
        old_preview=DEMO_ROOT/'providers'
        if (old_preview/'.apishield-demo-state').is_file():
            (old_preview/'stop.request').touch()
        deadline=time.monotonic()+15
        while any(not p['available'] for p in environment_report((8100,8101,8102))['ports']):
            if time.monotonic()>deadline:
                raise ValueError('CinemaFlow ports are occupied. Stop the previous managed preview before starting.')
            time.sleep(.25)
        selected_port=next((port for port in range(api_port,min(api_port+10,65536)) if environment_report([port])['ports'][0]['available']),None)
        if selected_port is None: raise ValueError('No free APIShield demo port is available; existing applications were left running')
        print('Preparing laptop GitHub connection and client source...',flush=True)
        profile=prepare_phone_demo(root)
        profile['api_port']=selected_port
        profile['dashboard_url']=f'http://127.0.0.1:{selected_port}/?project=cinemaflow'
        atomic_json(root/'profile.json',profile)
        print(profile['message'],flush=True)
        if not (ROOT/'frontend/dist/index.html').is_file():
            raise ValueError('Build the APIShield frontend first with npm --prefix frontend run build')
        logs=root/'logs';logs.mkdir(exist_ok=True)
        children=[];trees=[]
        def child(name,args,extra=None):
            tree=_WindowsTree() if os.name=='nt' else None
            with (logs/(name+'.log')).open('ab') as output:
                process=subprocess.Popen([sys.executable,'-B',*args],cwd=ROOT,env={**environment,**(extra or {})},
                    stdout=output,stderr=output,start_new_session=os.name!='nt',
                    creationflags=(subprocess.CREATE_NO_WINDOW|0x4) if os.name=='nt' else 0)
                children.append(process)
                trees.append(tree)
                if tree: tree.attach_and_resume(process)
            return process
        try:
            args=['-m','demo.runtime','--state',profile['state'],'--providers-host','127.0.0.1']
            args+=['--deployment-config',profile['config']] if profile['mode']=='deployment' else ['--client-repository',profile['source']]
            child('cinema',args)
            extra={'APISHIELD_JOBS_DIR':profile['jobs'],'APISHIELD_INTEGRATIONS':'{}'}
            if (ROOT/'tools/oasdiff.exe').is_file():extra['OASDIFF_BIN']=str(ROOT/'tools/oasdiff.exe')
            child('apishield',['-m','uvicorn','dashboard_api:app','--host','127.0.0.1','--port',str(selected_port)],extra)
            deadline=time.monotonic()+240
            with httpx.Client(trust_env=False,timeout=2) as client:
                while True:
                    if any(p.poll() is not None for p in children):
                        raise ValueError('A demo service exited during startup. Inspect '+str(logs))
                    try:
                        client.get('http://127.0.0.1:8100/health').raise_for_status()
                        client.get(f'http://127.0.0.1:{selected_port}/api/projects/cinemaflow').raise_for_status()
                        break
                    except httpx.HTTPError:
                        if time.monotonic()>deadline:raise ValueError('Startup timed out; inspect the phone demo logs')
                        time.sleep(.5)
            print('LAPTOP APIShield: '+profile['dashboard_url'],flush=True)
            print('LAPTOP provider controls: http://127.0.0.1:8100 (API providers tab)',flush=True)
            print('PHONE: open a reachable link below on the same Wi-Fi:',flush=True)
            for connection in profile['links']['connections']:print('  '+connection['client_url'],flush=True)
            print('PHONE GitHub reviewer: surjk73. No phone installations are needed.',flush=True)
            print('Only client port 8100 is shared; APIShield and providers are local to the laptop.',flush=True)
            print('Keep this launcher running. Double-click Stop Phone Demo.bat to stop its services.',flush=True)
            if not no_browser:
                webbrowser.open(profile['dashboard_url'])
                webbrowser.open('http://127.0.0.1:8100')
            while not (root/'stop.request').exists():
                if any(p.poll() is not None for p in children):raise ValueError('A demo service stopped; inspect '+str(logs))
                time.sleep(.5)
        finally:
            for process in children:
                if process.poll() is None:process.terminate()
            for tree in trees:
                if tree:tree.stop()
            for process in children:process.wait(timeout=15)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root')
    actions=parser.add_mutually_exclusive_group()
    actions.add_argument('--start',action='store_true')
    actions.add_argument('--stop',action='store_true')
    actions.add_argument('--reset',action='store_true')
    parser.add_argument('--api-port',type=int,default=8005)
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    try:
        if args.start:
            if not 1<=args.api_port<=65535:raise ValueError('Use a valid APIShield port')
            run_phone_demo(args.root,args.api_port,args.no_browser)
        elif args.reset:
            from .phone_reset import reset_phone_demo
            print('Stopping the phone demo and preparing a clean V1 rehearsal...',flush=True)
            result=reset_phone_demo(args.root)
            print('Complete reset finished. Previous data archived at '+result['archive'])
            print('Next PR target: '+result['base'])
            print('Double-click Start Phone Demo.bat, then refresh APIShield and CinemaFlow.')
        elif args.stop:
            root=workspace_path(args.root or DEMO_ROOT/'phone')
            if not (root/'.phone-demo').is_file():raise ValueError('No managed phone demo has been started')
            (root/'stop.request').touch()
            print('Stop requested for phone-demo services. Data and unrelated apps are preserved.')
        else:
            print(json.dumps(prepare_phone_demo(args.root)))
    except (ValueError,OSError,GitHubError) as error:
        raise SystemExit(str(error)) from None
    except KeyboardInterrupt:
        print('Phone demo stopped.')


if __name__=='__main__':
    main()
