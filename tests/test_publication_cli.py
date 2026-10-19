import json
from apishield.cli import main
from test_publication import publishing


def test_cli_prepare_has_no_remote_writes_then_publish_is_explicit(publishing,monkeypatch,capsys):
    service,github,job,jobs=publishing
    monkeypatch.setattr('apishield.publication_cli.open_service',lambda root,job_id=None,**kwargs:service)
    monkeypatch.setattr(service,'close',lambda:None)
    monkeypatch.setattr(jobs.executor,'shutdown',lambda **kwargs:None)
    assert main(['proposal','prepare',job.id,'--repository','owner/repo','--base','main','--jobs-dir',str(jobs.store.root)]) == 0
    prepared=json.loads(capsys.readouterr().out)
    assert prepared['status']=='ready' and 'GitHub CI: not verified' in prepared['body']
    assert github.calls==[]
    assert main(['proposal','publish',prepared['id'],'--jobs-dir',str(jobs.store.root)]) == 0
    published=json.loads(capsys.readouterr().out)
    assert published['status']=='published'
    assert github.calls==['commit','branch','pr']
    assert main(['proposal','report',prepared['id'],'--jobs-dir',str(jobs.store.root)]) == 0
    assert json.loads(capsys.readouterr().out)['publication']==published['publication']
