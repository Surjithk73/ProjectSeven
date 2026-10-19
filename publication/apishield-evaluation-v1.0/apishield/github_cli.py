"""Bounded GitHub controller commands using the existing CLI credential store."""
import base64
import json
import os
from pathlib import Path
import re
import tempfile
import time
from types import SimpleNamespace
from urllib.parse import quote

from .commands import run_command


class GitHubError(ValueError):
    def __init__(self,message,code=None):
        super().__init__(message)
        self.code=code


def repository_name(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9._-]{1,100}',value) or value.endswith('.git'):
        raise ValueError('Enter a GitHub owner/repository name')
    return value


def sha(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):
        raise GitHubError('GitHub returned an unsupported object identity')
    return value


class _Command:
    def __init__(self,workspace,deadline,check):
        allowed={'HOME','USERPROFILE','APPDATA','LOCALAPPDATA','GH_CONFIG_DIR'}
        environment={key:value for key,value in os.environ.items() if key.upper() in allowed}
        environment.update(GH_PROMPT_DISABLED='1',GH_HOST='github.com',GIT_TERMINAL_PROMPT='0')
        self.config=SimpleNamespace(environment=environment,budgets=SimpleNamespace(command_timeout_seconds=45,output_limit_bytes=2*1024*1024))
        self.workspace=workspace
        self.deadline=deadline
        self.external_check=check
    def remaining(self):return max(0,self.deadline-time.monotonic())
    def check(self):
        if self.external_check:self.external_check()
        if not self.remaining():raise GitHubError('GitHub operation exceeded its deadline')
    def cancelled(self):
        if self.external_check:self.external_check()
        return False
    def event(self,*args,**kwargs):pass  # Raw CLI/authentication output is never persisted.


class GhClient:
    def __init__(self,effect=None):
        self.effect=effect

    def _run(self,argv,deadline,check=None,files=None):
        with tempfile.TemporaryDirectory(prefix='apishield-github-') as directory:
            root=Path(directory)
            arguments=list(argv)
            for name,value in (files or {}).items():
                path=root/name
                path.write_text(value,encoding='utf-8',newline='\n')
                arguments=[str(path) if item=='{'+name+'}' else item for item in arguments]
            outcome=run_command(arguments,_Command(root,deadline,check),'github_controller')
        if outcome.get('cancelled'):raise GitHubError('GitHub operation cancelled')
        if outcome.get('timed_out'):raise GitHubError('GitHub operation exceeded its deadline')
        if outcome.get('output_limited'):raise GitHubError('GitHub response exceeds 2 MiB')
        if outcome['exit_code']!=0:
            match=re.search(r'HTTP\s+(\d{3})',outcome.get('stderr',''))
            code=int(match.group(1)) if match else None
            message={401:'GitHub CLI authentication is unavailable; sign in with gh before retrying.',
                     403:'GitHub denied access; check the signed-in account and repository permission.',
                     404:'GitHub repository, branch or object was not found.'}.get(code,
                     'GitHub CLI request failed; check CLI sign-in, connectivity and repository access.')
            raise GitHubError(message,code)
        return outcome['stdout']

    def api(self,method,endpoint,payload,*,deadline,check=None):
        if method not in {'GET','POST','PUT','PATCH'} or not isinstance(endpoint,str) or endpoint.startswith('/') or not re.fullmatch(r'(?:user|repos/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+(?:/[^\s#]*)?)',endpoint):
            raise ValueError('Unsupported GitHub controller request')
        if method=='PUT' and ('/contents/' not in endpoint or not isinstance(payload,dict) or 'sha' in payload):
            raise ValueError('Controlled bootstrap can only create a new fixture file')
        if method=='PATCH' and ('/git/refs/heads/' not in endpoint or not isinstance(payload,dict) or payload.get('force') is not False):
            raise ValueError('GitHub force updates are unsupported')
        if self.effect and method!='GET':self.effect('before',endpoint,None)
        argv=['gh','api','--hostname','github.com','--method',method,endpoint,
              '--header','Accept: application/vnd.github+json','--header','X-GitHub-Api-Version: 2026-03-10']
        files=None
        if payload is not None:
            argv+=['--input','{request.json}'];files={'request.json':json.dumps(payload,ensure_ascii=False)}
        output=self._run(argv,deadline,check,files)
        try:
            data=json.loads(output)
            if not isinstance(data,(dict,list)):raise ValueError()
        except (ValueError,TypeError):raise GitHubError('GitHub returned an invalid response') from None
        if self.effect and method!='GET':self.effect('after',endpoint,data)
        return data

    def inspect_target(self,repository,base,*,deadline):
        repository=repository_name(repository)
        if not isinstance(base,str) or not base or len(base)>255 or '\x00' in base:
            raise ValueError('Enter a valid existing base branch')
        self._run(['git','check-ref-format','--branch',base],deadline)
        account=self.api('GET','user',None,deadline=deadline)
        repo=self.api('GET',f'repos/{repository}',None,deadline=deadline)
        if not repo.get('permissions',{}).get('push'):raise GitHubError('The signed-in account cannot write this repository',403)
        canonical=repository_name(repo['full_name'])
        if canonical.casefold()!=repository.casefold():raise GitHubError('GitHub repository identity did not match')
        ref=self.api('GET',f'repos/{canonical}/git/ref/heads/{quote(base,safe="/")}',None,deadline=deadline)
        commit=self.api('GET',f'repos/{canonical}/git/commits/{sha(ref["object"]["sha"])}',None,deadline=deadline)
        return {'repository':canonical,'base':base,'source_commit':sha(commit['sha']),'tree':sha(commit['tree']['sha']),
                'account':{'login':account['login'],'id':account['id']},'permission':'write','private':bool(repo.get('private')),
                'url':f'https://github.com/{canonical}'}

    def create_source_commit(self,target,files,message,*,deadline,check=None):
        repository=repository_name(target['repository'])
        entries=[]
        for file in files:
            blob=self.api('POST',f'repos/{repository}/git/blobs',{'content':base64.b64encode(file['content'].encode()).decode(),'encoding':'base64'},deadline=deadline,check=check)
            if sha(blob['sha'])!=file['blob_sha']:raise GitHubError('GitHub source blob did not match the reviewed proposal')
            entries.append({'path':file['path'],'mode':file['mode'],'type':'blob','sha':blob['sha']})
        tree=self.api('POST',f'repos/{repository}/git/trees',{'base_tree':sha(target['tree']),'tree':entries},deadline=deadline,check=check)
        actor=target['account']
        author={'name':actor['login'],'email':f'{actor["id"]}+{actor["login"]}@users.noreply.github.com'}
        commit=self.api('POST',f'repos/{repository}/git/commits',{'message':message,'tree':sha(tree['sha']),'parents':[sha(target['source_commit'])],
                        'author':author,'committer':author},deadline=deadline,check=check)
        if commit['tree']['sha']!=tree['sha'] or [parent['sha'] for parent in commit['parents']]!=[target['source_commit']]:
            raise GitHubError('GitHub commit did not match the reviewed tree and parent')
        return {'sha':sha(commit['sha']),'tree':sha(tree['sha']),'parent':target['source_commit']}

    def ensure_branch(self,target,branch,commit,*,deadline):
        endpoint=f'repos/{repository_name(target["repository"])}/git/ref/heads/{quote(branch,safe="/")}'
        try:
            existing=self.api('GET',endpoint,None,deadline=deadline)
        except GitHubError as error:
            if error.code!=404:raise
            try:
                existing=self.api('POST',f'repos/{target["repository"]}/git/refs',{'ref':'refs/heads/'+branch,'sha':sha(commit['sha'])},deadline=deadline)
            except GitHubError:
                existing=self.api('GET',endpoint,None,deadline=deadline)
        if sha(existing['object']['sha'])!=commit['sha']:raise GitHubError('GitHub branch collision; existing branch was left unchanged')
        return {'branch':branch,'sha':commit['sha']}

    def _pr(self,repository,base,head,data):
        number=data.get('number');url=data.get('html_url','')
        if type(number) is not int or number<1 or url!=f'https://github.com/{repository}/pull/{number}' or data['head']['ref']!=head or data['base']['ref']!=base:
            raise GitHubError('GitHub pull request did not match the reviewed target')
        return {'number':number,'url':url,'draft':bool(data['draft']),'state':data['state'],
                'head':head,'base':base,'commit':sha(data['head']['sha'])}

    def create_draft(self,repository,base,head,title,body,*,deadline):
        repository=repository_name(repository)
        if self.effect:self.effect('before','draft_pr',None)
        output=self._run(['gh','pr','create','--repo',repository,'--base',base,'--head',head,'--draft',
            '--title',title,'--body-file','{body.md}','--no-maintainer-edit'],deadline,files={'body.md':body}).strip()
        match=re.fullmatch(r'https://github\.com/'+re.escape(repository)+r'/pull/([1-9][0-9]*)',output)
        if not match:raise GitHubError('GitHub publication response is uncertain; reconcile before retrying')
        data=self.api('GET',f'repos/{repository}/pulls/{match.group(1)}',None,deadline=deadline)
        result=self._pr(repository,base,head,data)
        if not result['draft']:raise GitHubError('Created pull request was not a draft; reconcile the actual remote state')
        if self.effect:self.effect('after','draft_pr',result)
        return result

    def find_publication(self,target,branch,expected,*,deadline):
        repository=repository_name(target['repository'])
        query=f'state=all&head={quote(repository.split("/")[0]+":"+branch,safe="")}&base={quote(target["base"],safe="")}&per_page=100'
        rows=self.api('GET',f'repos/{repository}/pulls?{query}',None,deadline=deadline)
        if not isinstance(rows,list):raise GitHubError('GitHub returned an invalid publication list')
        matches=[row for row in rows if row.get('head',{}).get('ref')==branch and row.get('base',{}).get('ref')==target['base']]
        if not matches:return None
        if len(matches)!=1:raise GitHubError('More than one matching remote publication; review it manually')
        row=matches[0]
        if row['head']['sha']!=expected['sha'] or expected['marker'] not in (row.get('body') or ''):
            raise GitHubError('Remote publication collision; existing pull request was left unchanged')
        return self._pr(repository,target['base'],branch,row)
