from pathlib import Path
import pytest


def test_environment_report_and_port_conflict(tmp_path):
    from demo.setup import environment_report
    import socket
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0)); listener.listen()
        report = environment_report([listener.getsockname()[1]])
    assert report['ports'][0]['available'] is False
    assert report['python']


def test_reset_refuses_unmanaged_or_dirty_source(tmp_path):
    from demo.setup import reset_rehearsal
    with pytest.raises(ValueError, match='managed'):
        reset_rehearsal(tmp_path)
    (tmp_path / '.apishield-demo-state').touch()
    (tmp_path / 'personal.txt').write_text('preserve')
    reset_rehearsal(tmp_path)
    assert (tmp_path / 'personal.txt').read_text() == 'preserve'


def test_baseline_export_preserves_shipping_files(tmp_path):
    from demo.setup import export_client
    (tmp_path / 'shipping.txt').write_text('keep')
    export_client(tmp_path)
    assert (tmp_path / 'shipping.txt').read_text() == 'keep'
    assert (tmp_path / 'movie_booking/app.py').is_file()
    assert (tmp_path / 'movie_booking/tests/test_booking.py').is_file()
    assert (tmp_path / '.github/workflows/cinema-client.yml').is_file()
    with pytest.raises(ValueError, match='exists'):
        export_client(tmp_path)


def test_service_ports_are_valid_and_distinct():
    from demo.setup import service_ports
    assert service_ports(8200, 8201, 8202) == (8200, 8201, 8202)
    for ports in [(8100, 8100, 8102), (0, 8101, 8102), (8100, 8101, 65536)]:
        with pytest.raises(ValueError, match='ports'):
            service_ports(*ports)


def test_demo_paths_stay_inside_project():
    from demo.setup import ROOT, workspace_path
    assert workspace_path('.apishield/cinema/providers') == ROOT / '.apishield/cinema/providers'
    with pytest.raises(ValueError, match='ProjectSeven'):
        workspace_path(ROOT.parent / 'outside-demo')
    with pytest.raises(ValueError, match='ProjectSeven'):
        workspace_path('../outside-demo')


def test_copyable_lan_links_do_not_need_preconfigured_ip(monkeypatch):
    from demo.setup import connection_info
    import socket
    monkeypatch.setattr(socket, 'gethostname', lambda: 'CINEMA-PC')
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [
        (socket.AF_INET,socket.SOCK_STREAM,6,'',('192.168.7.25',0)),
        (socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',0)),
        (socket.AF_INET,socket.SOCK_STREAM,6,'',('169.254.1.1',0))])
    links=connection_info(8200,8201,8202)
    assert links['scope']=='LAN'
    assert links['connections'][0]['client_url']=='http://CINEMA-PC:8200'
    assert links['connections'][1]['theatre_url']=='http://192.168.7.25:8201'
    assert len(links['connections'])==2


def test_system_a_accepts_the_copied_http_link(monkeypatch):
    from demo.setup import demo_address
    import socket
    monkeypatch.setattr(socket,'getaddrinfo',lambda *a,**k: [(socket.AF_INET,socket.SOCK_STREAM,6,'',('192.168.7.25',0))])
    assert demo_address('http://CINEMA-PC:8200/') == ('cinema-pc',8200)
    assert demo_address('192.168.7.25',8100)==('192.168.7.25',8100)
    for value in ['http://user:password@cinema-pc:8100','http://cinema-pc:8100/?key=x','http://cinema-pc:8100/admin','http://cinema-pc:0']:
        with pytest.raises(ValueError): demo_address(value)
    monkeypatch.setattr(socket,'getaddrinfo',lambda *a,**k: [(socket.AF_INET,socket.SOCK_STREAM,6,'',('8.8.8.8',0))])
    with pytest.raises(ValueError,match='LAN'): demo_address('public.example')


def test_system_a_keeps_config_and_source_inside_project(tmp_path):
    import subprocess
    from demo.setup import ROOT, configure_system_a, export_client
    from apishield.project_store import ProjectStore
    repo=tmp_path/'client';repo.mkdir()
    export_client(repo)
    for args in [('init',),('config','user.name','Fixture'),('config','user.email','fixture@example.invalid'),('add','.'),('commit','-m','V1 client')]:
        subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True)
    jobs=tmp_path/'jobs'
    result=configure_system_a(repo,'http://127.0.0.1:8200',jobs,'gemini-3.8-flash',theatre_port=8201,payment_port=8202)
    project=ProjectStore(jobs).load_project(result['project_id'])
    assert project.client_url=='http://127.0.0.1:8200'
    assert project.deployment_actor=='surjk73'
    assert project.providers[0].base_url=='http://127.0.0.1:8201'
    assert jobs.is_relative_to(ROOT)
    with pytest.raises(ValueError,match='ProjectSeven'):
        configure_system_a(repo,'http://127.0.0.1:8200',ROOT.parent/'outside-jobs','gemini-3.8-flash',theatre_port=8201,payment_port=8202)
