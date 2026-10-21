import subprocess
from pathlib import Path
import pytest


def test_phone_profile_keeps_admin_on_laptop_and_receipts_use_publisher(tmp_path):
    from demo.phone import phone_configuration
    profile=phone_configuration(tmp_path/'phone')
    assert profile['deployment']['deployment_actor']=='Surjithk73'
    assert profile['deployment']['publisher']=='Surjithk73'
    assert profile['reviewer']=='surjk73'
    assert profile['deployment']['providers']=={'theatre':'http://127.0.0.1:8101','payment':'http://127.0.0.1:8102'}
    assert Path(profile['jobs']).is_relative_to(tmp_path)
    assert Path(profile['deployment']['releases']).is_relative_to(tmp_path)
    with pytest.raises(ValueError,match='publisher'):
        phone_configuration(tmp_path/'wrong',publisher='surjk73')


def test_phone_prepare_preview_does_not_connect_publisher_or_claim_deployment(tmp_path,monkeypatch):
    import demo.phone as phone
    from apishield.github_cli import GitHubError
    from demo.setup import export_client
    from apishield.project_store import ProjectStore
    class GitHub:
        def api(self,method,endpoint,payload,**kwargs):
            if endpoint=='user': return {'login':'Surjithk73'}
            raise GitHubError('No baseline on main',404)
    def source(path,branch):
        path.mkdir(parents=True)
        export_client(path)
        for args in [('init',),('config','user.name','Fixture'),('config','user.email','fixture@example.invalid'),('add','.'),('commit','-m','Client')]:
            subprocess.run(['git','-C',str(path),*args],check=True,capture_output=True)
    monkeypatch.setattr(phone,'prepare_source',source)
    result=phone.prepare_phone_demo(tmp_path/'phone',github=GitHub())
    assert result['mode']=='preview'
    assert 'merge' in result['message'].lower()
    project=ProjectStore(result['jobs']).load_project('cinemaflow')
    assert project.deployment_actor=='Surjithk73'
    assert project.automation_mode=='manual'
    target=Path(result['jobs'])/'_publication/targets/cinemaflow/state.json'
    assert not target.exists()


def test_phone_prepare_does_not_hide_authentication_failures(tmp_path):
    from demo.phone import prepare_phone_demo
    class GitHub:
        def api(self,*args,**kwargs): return {'login':'surjk73'}
    with pytest.raises(ValueError,match='Surjithk73'):
        prepare_phone_demo(tmp_path/'phone',github=GitHub())


def test_phone_merged_baseline_connects_publisher_for_deployment(tmp_path,monkeypatch):
    import demo.phone as phone
    from demo.setup import export_client
    from apishield.publication_state import PublicationStore
    from apishield.project_store import ProjectStore
    class GitHub:
        def api(self,*args,**kwargs): return {'login':'Surjithk73'}
        def inspect_target(self,repository,base,**kwargs):
            return {'repository':repository,'base':base,'account':{'login':'Surjithk73','id':73},'permission':'write'}
    def source(path,branch):
        assert branch=='main'
        path.mkdir(parents=True)
        export_client(path)
        for args in [('init',),('config','user.name','Fixture'),('config','user.email','fixture@example.invalid'),('add','.'),('commit','-m','Client')]:
            subprocess.run(['git','-C',str(path),*args],check=True,capture_output=True)
    monkeypatch.setattr(phone,'prepare_source',source)
    result=phone.prepare_phone_demo(tmp_path/'phone',github=GitHub())
    target=PublicationStore(result['jobs']).read_target('cinemaflow')
    assert result['mode']=='deployment'
    assert target['configured'] and target['account']['login']=='Surjithk73'
    assert ProjectStore(result['jobs']).load_project('cinemaflow').deployment_actor=='Surjithk73'
