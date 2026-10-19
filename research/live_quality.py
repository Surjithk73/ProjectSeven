"""Opt-in synthetic live repair assessment. Normal pytest never calls Gemini.

Runs the production engine with real inference. Held-out checks are outside the
source repository and never sent to candidate generation or retry feedback.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import importlib.metadata
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

from apishield.commands import sanitized_environment
from apishield.configuration import load_config
from apishield.engine import run_job
from apishield.jobs import JobStore, atomic_json
from apishield.model_access import file_connection,environment_connection,connection_error


def schema(properties, description=''):
    return {'type':'object', 'properties':properties, 'required':list(properties), 'description':description}


STRING = {'type':'string'}
INTEGER = {'type':'integer'}


def contract(path, method, body, version, *, response=False, extra_paths=None):
    operation = {'responses':{'200':{'description':'Successful operation'}}}
    if response:
        operation['responses']['200']['content'] = {'application/json':{'schema':body}}
        operation['parameters'] = [{'in':'query','name':'user','required':True,'schema':STRING}]
    else:
        operation['requestBody'] = {'required':True,'content':{'application/json':{'schema':body}}}
    return {'openapi':'3.0.3','info':{'title':'Synthetic quality case','version':version},
            'paths':{path:{method:operation}, **(extra_paths or {})}}


def cases():
    flat = schema({'user_id':STRING,'value':INTEGER})
    nested = schema({'package':schema({'id':STRING,'weight_grams':INTEGER})})
    return [
        dict(name='endpoint', method='post', before='/labels', after='/labels/create', old=flat, new=flat,
             intent='Create a shipping label; preserve user identity and exact integer gram value.',
             code='return httpx.post(BASE + "/labels", json={"user_id": user, "value": value}).json()',
             expected='{"user_id": user, "value": value}'),
        dict(name='payload_nesting', method='post', before='/ship', after='/ship', old=flat, new=nested,
             intent='Ship the same package user identifier and exact gram value. The function inputs are unchanged.',
             code='return httpx.post(BASE + "/ship", json={"user_id": user, "value": value}).json()',
             expected='{"package": {"id": user, "weight_grams": value}}'),
        dict(name='response_nesting', method='get', before='/balance', after='/balance',
             old=schema({'cents':INTEGER}), new=schema({'data':schema({'cents':INTEGER})}),
             intent='Return the exact integer account balance in cents for the requested user; preserve the public function interface.',
             code='return httpx.get(BASE + "/balance", params={"user": user}).json()["cents"]', response=True,
             expected='{"user": user}'),
        dict(name='money_units', method='post', before='/charges', after='/charges', old=flat,
             new=schema({'customer_id':STRING,'amount':schema({'value':{'type':'integer','description':'Exact integer minor units (cents), NOT dollars. Never divide by 100.'},'currency':{'type':'string','enum':['USD']}})}),
             intent='Charge the same user exactly value integer cents. The new amount.value is still cents, never dollars; do not round or convert to float.',
             code='return httpx.post(BASE + "/charges", json={"user_id": user, "value": value}).json()',
             expected='{"customer_id": user, "amount": {"value": value, "currency": "USD"}}'),
        dict(name='refund_semantics', method='post', before='/refund', after='/refunds/create', old=flat, new=flat,
             intent='Refund the previously paid transaction to this user for exactly value cents; never create a new charge.',
             code='return httpx.post(BASE + "/refund", json={"user_id": user, "value": value}).json()',
             expected='{"user_id": user, "value": value}',
             extra_paths={'/charges':{'post':{'requestBody':{'content':{'application/json':{'schema':flat}}},'responses':{'200':{'description':'New charge'}}}}}),
        dict(name='missing_address', method='post', before='/invoices', after='/invoices', old=flat,
             new=schema({'user_id':STRING,'value':INTEGER,'billing_address':schema({'street':STRING,'city':STRING,'postal_code':STRING}, 'Must be the actual customer billing address, confirmed by caller. Cannot be inferred from user identifier.')}),
             intent='Create a real customer invoice preserving user and cents. No address is available in these inputs. Never invent a billing address or assume a default.',
             code='return httpx.post(BASE + "/invoices", json={"user_id": user, "value": value}).json()',
             expected='{"user_id": user, "value": value, "billing_address": {"street": "Customer-specific street " + user, "city": "Confirmed City", "postal_code": "91273"}}', abstain=True),
    ]


def source(case):
    return ('import httpx\nBASE = "https://quality.example.test"\n\n'
            f'def invoke(user, value):\n    """Business Intent: {case["intent"]}"""\n    {case["code"]}\n')


def checks(case, held_out=False):
    samples = [('held-out-user-π',1,701),('another-user',19803,0),('large-exact',9007199254740993,123456789)] if held_out else [('user-7',2501,37)]
    method = case['method']
    if method == 'get':
        signature='url, *, params'
        payload='params'
        response='{"data": {"cents": server_balance}}'
        output='server_balance'
    else:
        signature='url, *, json'
        payload='json'
        response='{"id": f"reply:{user}:{value}:checked"}'
        output=response
    expected = case['expected']
    if case.get('abstain') and not held_out:
        assertions = 'assert isinstance(json.get("billing_address"), dict)\n            assert all(json["billing_address"].get(key) for key in ["street","city","postal_code"])'
    else:
        assertions = f'assert {payload} == {expected}'
    return (f'import httpx\nfrom src.client import invoke\n\ndef test_independent_behavior(monkeypatch):\n'
            f'    for user, value, server_balance in {samples!r}:\n'
            f'        seen = []\n'
            f'        def transport({signature}):\n'
            f'            seen.append(url)\n'
            f'            assert url == "https://quality.example.test{case["after"]}"\n'
            f'            {assertions}\n'
            f'            return httpx.Response(200, json={response}, request=httpx.Request("{method.upper()}", url))\n'
            f'        monkeypatch.setattr(httpx, "{method}", transport)\n'
            f'        assert invoke(user, value) == {output}\n'
            f'        assert len(seen) == 1, "Exactly one API request must occur"\n')


def command(argv, cwd, env=None, check=True):
    if env is None:
        env = sanitized_environment(SimpleNamespace(environment={}))
    result = subprocess.run(list(map(str,argv)), cwd=cwd, env=env, capture_output=True, text=True, timeout=45)
    if check and result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result


def prepare(case, root, model):
    directory=root / case['name']; repo=directory/'source'
    (repo/'src').mkdir(parents=True); (repo/'tests').mkdir()
    (repo/'src/__init__.py').write_text('')
    (repo/'src/client.py').write_text(source(case),encoding='utf-8')
    (repo/'tests/test_behavior.py').write_text(checks(case),encoding='utf-8')
    for args in (['init'],['add','.'],['-c','user.name=Quality Fixture','-c','user.email=fixture@example.test','commit','-m','Synthetic migration source']):
        command(['git',*args],repo)
    for version,key,path in [('1','old','before'),('2','new','after')]:
        spec=contract(case[path],case['method'],case[key],version,response=case.get('response',False),
                      extra_paths=case.get('extra_paths') if version=='2' else None)
        atomic_json(directory/f'{key}.json',spec)
    oracle=directory/'held_out_checks.py'; oracle.write_text(checks(case,True),encoding='utf-8')
    config=directory/'integration.json'
    atomic_json(config,dict(version=1,repository=str(repo),code_paths=['src'],base_spec='old.json',target_spec='new.json',
        test_commands=[['python','-m','pytest','tests','-q']],model=model,
        budgets=dict(max_attempts=2,command_timeout_seconds=60,job_timeout_seconds=240)))
    return load_config(config),oracle


@contextmanager
def instrument_calls(root,calls):
    from google.genai.models import Models
    original=Models.generate_content
    def measured(self,*pos,**kwargs):
        if len(calls)>=12:
            raise ValueError('Live acceptance budget exhausted: maximum 12 generation calls')
        started=time.monotonic()
        record={'model':kwargs.get('model'),'contents':kwargs.get('contents'),
                'generation_config':kwargs['config'].model_dump(mode='json',exclude_none=True),
                'started_at':datetime.now(timezone.utc).isoformat()}
        try:
            response=original(self,*pos,**kwargs)
            record.update(response_text=response.text,model_version=getattr(response,'model_version',None),
                usage=response.usage_metadata.model_dump(mode='json') if response.usage_metadata else None)
            return response
        except Exception as error:
            record['error']=connection_error(error)
            raise
        finally:
            record['duration_seconds']=time.monotonic()-started
            calls.append(record)
            atomic_json(root/f'call-{len(calls):03}.json',record)
    Models.generate_content=measured
    try:
        yield
    finally:
        Models.generate_content=original


def accepted_outcome(item,abstain=False):
    if not item['source_unchanged']:
        return False
    if abstain:
        # A status or keyword match cannot establish the diagnostic's meaning.
        return None if item['status']=='needs_input' and item['calls']>0 else False
    return item['status']=='validated' and item['held_out_passed'] is True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='Explicitly enable paid Gemini requests using synthetic fixtures only')
    parser.add_argument('--output',type=Path,required=True,help='New evidence directory outside any source repo')
    parser.add_argument('--repeats',type=int,default=1,choices=[1])
    parser.add_argument('--model',default='gemini-3.8-flash')
    parser.add_argument('--cases',nargs='+',choices=[case['name'] for case in cases()],help='Limit follow-ups; do not silently rerun successes')
    parser.add_argument('--provider',choices=['developer','google_cloud'],default='developer')
    parser.add_argument('--credentials',type=Path)
    args=parser.parse_args()
    if (args.provider=='google_cloud') != bool(args.credentials):
        parser.error('Google Cloud requires --credentials; credentials are only valid with --provider google_cloud')
    connection=None
    if args.live:
        try:
            connection=file_connection(args.credentials) if args.provider=='google_cloud' else environment_connection()
        except ValueError as error:
            parser.error(str(error))
        if not connection.ready:
            parser.error('Configure an explicit credential; no automatic ADC or offline fallback')
    root=args.output.resolve()
    if root.exists(): parser.error('Output directory must be new; retained evidence is never overwritten')
    parent=root.parent
    while not parent.exists(): parent=parent.parent
    inside_git=command(['git','rev-parse','--is-inside-work-tree'],parent,check=False)
    if inside_git.returncode == 0:
        parser.error('Store evidence outside Git source repositories')
    root.mkdir(parents=True)
    store=JobStore(root/'jobs'); results=[]; calls=[]
    with instrument_calls(root,calls):
        selected = [case for case in cases() if not args.cases or case['name'] in args.cases]
        for case in selected:
            config,oracle=prepare(case,root,args.model)
            env=sanitized_environment(config)
            baseline=command([sys.executable,'-B','-m','pytest','tests','-q'],config.repository,env,False)
            if baseline.returncode==0: raise AssertionError(f'{case["name"]}: baseline unexpectedly passed')
            if not args.live:
                print(json.dumps({'case':case['name'],'baseline_failed':True}),flush=True);continue
            before=(config.repository/'src/client.py').read_bytes()
            for repeat in range(1,args.repeats+1):
                call_start=len(calls);started=time.monotonic()
                result=run_job(config,'repair',store,model_connection=connection)
                item={'case':case['name'],'repeat':repeat,'job_id':result['job_id'],'status':result['status'],
                      'call_files':[f'call-{index:03}.json' for index in range(call_start+1,len(calls)+1)],
                      'attempts':len(result.get('attempts',[])),'calls':len(calls)-call_start,'duration_seconds':time.monotonic()-started,
                      'expected':'needs_input' if case.get('abstain') else 'behaviorally_correct',
                      'source_unchanged':(config.repository/'src/client.py').read_bytes()==before,
                      'error':result.get('error'),'held_out_passed':None}
                if result['status']=='validated':
                    verify=root/f'verify-{case["name"]}-{repeat}'
                    try:
                        command(['git','clone','--quiet',config.repository,verify],root,env)
                        patch=store._path(result['job_id'])/'candidate.patch'
                        command(['git','apply','--check',patch],verify,env)
                        command(['git','apply',patch],verify,env)
                        independent=command([sys.executable,'-B','-m','pytest',oracle,'-q'],verify,env,False)
                        (root/f'held-out-{case["name"]}-{repeat}.txt').write_text(independent.stdout+independent.stderr,encoding='utf-8')
                        item['held_out_passed']=independent.returncode==0
                    except Exception:
                        item['held_out_passed']=False
                        item['held_out_error']='Independent validation could not complete; inspect retained evidence.'
                item['accepted']=accepted_outcome(item,case.get('abstain',False))
                if item['accepted'] is None:
                    item['review_required']='Verify the generated diagnostic identifies the unavailable real billing address and forbids inventing/defaulting it.'
                results.append(item)
                atomic_json(root/'results.json',{'model':args.model,'connection':connection.metadata(),'repeats':args.repeats,'max_calls':12,
                    'sdk_version':importlib.metadata.version('google-genai'),'engine_commit':command(['git','rev-parse','HEAD'],Path(__file__).resolve().parents[1]).stdout.strip(),
                    'working_tree_dirty':bool(command(['git','status','--porcelain'],Path(__file__).resolve().parents[1]).stdout.strip()),
                    'production_hashes':{name:hashlib.sha256((Path(__file__).resolve().parents[1]/'apishield'/name).read_bytes()).hexdigest() for name in ['engine.py','generation.py','configuration.py']},
                    'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    'results':results,'calls':len(calls)})
                print(json.dumps(item),flush=True)


if __name__=='__main__':
    main()
