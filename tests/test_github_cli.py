import hashlib
import json
from pathlib import Path
import time

import pytest

from apishield.commands import sanitized_environment

SHA='a'*40
TREE='b'*40


def test_cli_arguments_environment_and_body_never_expose_credentials(monkeypatch,tmp_path):
    from apishield.github_cli import GhClient
    captured=[]
    monkeypatch.setenv('GH_TOKEN','PRIVATE-GH-TOKEN');monkeypatch.setenv('GITHUB_TOKEN','PRIVATE-GITHUB-TOKEN')
    monkeypatch.setenv('GEMINI_API_KEY','PRIVATE-MODEL');monkeypatch.setenv('GH_HOST','evil.example')
    monkeypatch.setenv('GH_DEBUG','api');monkeypatch.setenv('HTTPS_PROXY','http://private.example')
    monkeypatch.setenv('GH_CONFIG_DIR',str(tmp_path/'configured-cli'))
    def command(argv,job,label):
        captured.append((argv,sanitized_environment(job.config)))
        if '--input' in argv:
            assert json.loads(Path(argv[argv.index('--input')+1]).read_text())=={'fixture':'value'}
        return dict(exit_code=0,stdout='{"sha":"'+SHA+'"}',stderr='',timed_out=False,output_limited=False,cancelled=False)
    monkeypatch.setattr('apishield.github_cli.run_command',command)
    result=GhClient().api('POST','repos/owner/repo/git/blobs',{'fixture':'value'},deadline=time.monotonic()+1)
    assert result['sha']==SHA
    argv,env=captured[0]
    assert argv[:4]==['gh','api','--hostname','github.com']
    assert env['GH_PROMPT_DISABLED']=='1' and env['GH_HOST']=='github.com'
    assert env['GH_CONFIG_DIR']==str(tmp_path/'configured-cli')
    assert not any(name in env for name in ['GH_TOKEN','GITHUB_TOKEN','GEMINI_API_KEY','GH_DEBUG','HTTPS_PROXY'])
    assert not Path(argv[argv.index('--input')+1]).exists()


@pytest.mark.parametrize('outcome',[
    dict(exit_code=1,stderr='HTTP 403 PRIVATE-GH-TOKEN'),
    dict(exit_code=None,stderr='PRIVATE-PATH'),dict(exit_code=0,stdout='PRIVATE-GH-TOKEN'),
    dict(exit_code=0,stdout='{}',timed_out=True),dict(exit_code=0,stdout='{}',output_limited=True)])
def test_cli_errors_safe_and_bounded(monkeypatch,outcome):
    from apishield.github_cli import GhClient
    def command(argv,job,label):
        assert job.config.budgets.command_timeout_seconds==45
        assert job.config.budgets.output_limit_bytes==2*1024*1024
        assert job.remaining()<=0.5
        return {**dict(exit_code=0,stdout='',stderr='',timed_out=False,output_limited=False,cancelled=False),**outcome}
    monkeypatch.setattr('apishield.github_cli.run_command',command)
    with pytest.raises(ValueError) as failure:GhClient().api('GET','user',None,deadline=time.monotonic()+0.5)
    assert 'PRIVATE' not in str(failure.value)


def test_two_file_commit_uses_one_tree_preserving_base(monkeypatch):
    from apishield.github_cli import GhClient
    calls=[]
    files=[]
    for name,content in [('src/a.py','A = 1\n'),('src/b.py','B = 2\n')]:
        data=content.encode();files.append(dict(path=name,content=content,mode='100644',blob_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
    def api(self,method,endpoint,payload,**kwargs):
        calls.append((endpoint,payload))
        if endpoint.endswith('/blobs'):
            import base64
            data=base64.b64decode(payload['content']);return {'sha':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
        if endpoint.endswith('/trees'):return {'sha':TREE}
        return {'sha':SHA,'tree':{'sha':TREE},'parents':[{'sha':'c'*40}]}
    monkeypatch.setattr(GhClient,'api',api)
    target={'repository':'owner/repo','base':'main','source_commit':'c'*40,'tree':'d'*40,'account':{'login':'fixture','id':7}}
    result=GhClient().create_source_commit(target,files,'Synthetic repair',deadline=time.monotonic()+2)
    assert result['sha']==SHA
    assert len(calls)==4
    assert calls[2][1]['base_tree']=='d'*40
    assert [item['path'] for item in calls[2][1]['tree']]==['src/a.py','src/b.py']
    assert calls[3][1]['parents']==['c'*40]
    assert calls[3][1]['author']['email']=='7+fixture@users.noreply.github.com'
    assert calls[3][1]['committer']==calls[3][1]['author']


@pytest.mark.parametrize('matching',[True,False])
def test_existing_branch_is_reused_only_when_exactly_matching(monkeypatch,matching):
    from apishield.github_cli import GhClient
    writes=[]
    def api(self,method,endpoint,payload,**kwargs):
        if method=='POST':writes.append(endpoint)
        return {'object':{'sha':SHA if matching else 'f'*40}}
    monkeypatch.setattr(GhClient,'api',api)
    target={'repository':'owner/repo','base':'main'}
    if matching:
        assert GhClient().ensure_branch(target,'codex/apishield-fixture',{'sha':SHA},deadline=time.monotonic()+2)['sha']==SHA
    else:
        with pytest.raises(ValueError,match='collision'):GhClient().ensure_branch(target,'codex/apishield-fixture',{'sha':SHA},deadline=time.monotonic()+2)
    assert not writes


def test_create_draft_uses_exact_noninteractive_flags_and_newlines(monkeypatch):
    from apishield.github_cli import GhClient
    captured=[]
    def command(argv,job,label):
        captured.append(argv)
        assert Path(argv[argv.index('--body-file')+1]).read_text()=='First line\n\nSecond line'
        return dict(exit_code=0,stdout='https://github.com/owner/repo/pull/1\n',stderr='',timed_out=False,output_limited=False,cancelled=False)
    monkeypatch.setattr('apishield.github_cli.run_command',command)
    monkeypatch.setattr(GhClient,'api',lambda *args,**kwargs:{'number':1,'html_url':'https://github.com/owner/repo/pull/1','draft':True,'head':{'ref':'codex/apishield-fixture','sha':SHA},'base':{'ref':'main'},'state':'open'})
    result=GhClient().create_draft('owner/repo','main','codex/apishield-fixture','Title','First line\n\nSecond line',deadline=time.monotonic()+2)
    assert result['draft'] is True
    assert '--draft' in captured[0] and '--head' in captured[0] and '--no-maintainer-edit' in captured[0]
    assert '--fill' not in captured[0] and '--dry-run' not in captured[0]


def test_existing_closed_publication_is_found_without_recreation(monkeypatch):
    from apishield.github_cli import GhClient
    def api(self,method,endpoint,payload,**kwargs):
        assert method=='GET'
        return [{'number':2,'html_url':'https://github.com/owner/repo/pull/2','draft':False,'state':'closed',
                 'head':{'ref':'codex/apishield-fixture','sha':SHA},'base':{'ref':'main'},'body':'Proposal fixture'}]
    monkeypatch.setattr(GhClient,'api',api)
    result=GhClient().find_publication({'repository':'owner/repo','base':'main'},'codex/apishield-fixture',{'sha':SHA,'marker':'Proposal fixture'},deadline=time.monotonic()+2)
    assert result['state']=='closed' and result['number']==2


def test_inspect_target_reports_only_safe_identity_and_checks_permission(monkeypatch):
    from apishield.github_cli import GhClient
    client=GhClient();calls=[]
    monkeypatch.setattr(client,'_run',lambda *args,**kwargs:'main')
    def api(method,endpoint,payload,**kwargs):
        calls.append(endpoint)
        return {'user':{'login':'fixture','id':7,'PRIVATE-TOKEN':'hidden'},
                'repos/owner/repo':{'full_name':'owner/repo','permissions':{'push':True},'private':True},
                'repos/owner/repo/git/ref/heads/main':{'object':{'sha':SHA}},
                'repos/owner/repo/git/commits/'+SHA:{'sha':SHA,'tree':{'sha':TREE}}}[endpoint]
    monkeypatch.setattr(client,'api',api)
    target=client.inspect_target('owner/repo','main',deadline=time.monotonic()+2)
    assert target['source_commit']==SHA and target['tree']==TREE
    assert target['account']=={'login':'fixture','id':7} and 'hidden' not in json.dumps(target)
    monkeypatch.setattr(client,'api',lambda *args,**kwargs:{'login':'fixture','id':7,'permissions':{'push':False}})
    with pytest.raises(ValueError,match='cannot write'):client.inspect_target('owner/repo','main',deadline=time.monotonic()+2)


def test_real_controller_output_cap_and_absolute_timeout():
    import sys
    from apishield.github_cli import GhClient
    client=GhClient()
    with pytest.raises(ValueError,match='2 MiB'):
        client._run([sys.executable,'-B','-c','print("x"*(2*1024*1024+1))'],time.monotonic()+10)
    started=time.monotonic()
    with pytest.raises(ValueError,match='deadline'):
        client._run([sys.executable,'-B','-c','import time;time.sleep(30)'],started+0.25)
    assert time.monotonic()-started<7


def test_real_missing_executable_never_echoes_sensitive_path():
    from apishield.github_cli import GhClient
    with pytest.raises(ValueError) as failure:
        GhClient()._run(['NONEXISTENT-PRIVATE-GH-PATH'],time.monotonic()+3)
    assert 'PRIVATE' not in str(failure.value)


@pytest.mark.parametrize('method,endpoint,payload',[
    ('PUT','repos/owner/repo/contents/README.md',{'message':'Synthetic fixture bootstrap','content':'Zml4dHVyZQ==','branch':'main'}),
    ('PATCH','repos/owner/repo/git/refs/heads/main',{'sha':SHA,'force':False})])
def test_controlled_fixture_bootstrap_uses_bounded_adapter(monkeypatch,method,endpoint,payload):
    from apishield.github_cli import GhClient
    captured=[]
    def command(argv,job,label):
        captured.append(argv)
        return dict(exit_code=0,stdout='{}',stderr='',timed_out=False,output_limited=False,cancelled=False)
    monkeypatch.setattr('apishield.github_cli.run_command',command)
    GhClient().api(method,endpoint,payload,deadline=time.monotonic()+2)
    assert captured[0][captured[0].index('--method')+1]==method


def test_controlled_adapter_refuses_force_updates():
    from apishield.github_cli import GhClient
    with pytest.raises(ValueError,match='force'):
        GhClient().api('PATCH','repos/owner/repo/git/refs/heads/main',{'sha':SHA,'force':True},deadline=time.monotonic()+2)
