"""Standalone research harness; production UI is never imported or started."""
import argparse
import ast
import csv
import difflib
import hashlib
import importlib.metadata
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from benchmarks.runners.evaluation import execute,judge,valid_image
from benchmarks.adapters.model_backend import Backend
BENCH=ROOT/'benchmarks'

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(value):return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=True)

def observed_git_head():
    try:return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError):return None

def structural(source):
    tree=ast.parse(source)
    return {'functions':[n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)],
            'literal_paths':sorted({n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('/')}),
            'basis':'python_ast; unresolved dynamic paths excluded'}

def localize_with_treatment(task,flags,discovered,changed,context,candidate):
    if isinstance(candidate,dict) and isinstance(candidate.get('predicted_locations'),list):
        return candidate['predicted_locations']
    if flags.get('enable_semantic_clustering') and isinstance(context.get('semantic_groups'),dict):
        coupled=context['semantic_groups'].get('coupled_ast_nodes')
        if isinstance(coupled,list):return coupled
    if flags.get('enable_structural_graph') and isinstance(context.get('structural_graph'),dict):
        funcs=[f'client.py:{fn}' for fn in context['structural_graph'].get('functions',[]) if not fn.startswith('get_health')]
        if funcs:return funcs
    return ['client.py:build_request'] if changed and discovered['literal_paths'] else []

def outcome(syntax,abstain,visible,hidden,generated=True,infrastructure=False):
    if infrastructure:return 'INFRASTRUCTURE_ERROR'
    if abstain:return 'ABSTAIN/REFUSED'
    if not syntax:return 'SYNTAX_ERROR'
    if visible==0 and hidden==0 and generated:return 'PASS'
    if visible==0 and hidden==1 and generated:return 'PLAUSIBLE_BUT_INCORRECT'
    return 'TEST_FAILURE'

def run_one(task,method,flags,args,destination):
    ident=f'{method}_{task["task_id"]}_rep{args.repetition}'
    artifacts=destination/'evidence'/ident;artifacts.mkdir(parents=True)
    start_ns=time.perf_counter_ns();start=datetime.now(timezone.utc)
    phases={k:0.0 for k in ['detection','graph','intent','inference','visible_tests','hidden_tests']}
    before=Path(task['source_directory'],'client.py').read_text(encoding='utf-8')
    old=read(task['old_contract_path']);new=read(task['new_contract_path'])
    t=time.perf_counter_ns()
    changed=canonical(old['paths']) != canonical(new['paths'])
    discovered=structural(before)
    truth=set(task['ground_truth_affected_locations'])
    phases['detection']=(time.perf_counter_ns()-t)/1e9
    context={'source':before,'old_contract':old,'new_contract':new,'allowed_edit_paths':['client.py']}
    if flags['enable_test_feedback']:
        context['public_test_source']=Path(task['public_test_suite']).read_text(encoding='utf-8')
    t=time.perf_counter_ns()
    graph=discovered if flags['enable_structural_graph'] else None
    if graph:context['structural_graph']=graph
    phases['graph']=(time.perf_counter_ns()-t)/1e9
    calls=[];model=None;candidate=None;error=None;syntax=True;abstain=False
    visible=hidden=None;invariants={};generated_ok=True;diff='';attempts=0
    generation_only=getattr(args,'generation_only',False)
    profile=read(BENCH/'profiles'/('gemini.json' if args.provider=='google-cloud' else 'llama_cpp.json'))
    def measured_generate(prompt, stage, phase):
        started=time.perf_counter_ns()
        try:return model.generate(prompt,stage)
        finally:phases[phase]+=(time.perf_counter_ns()-started)/1e9
    try:
        if args.mode=='live':
            model=Backend(args.provider,profile,artifacts/'model_calls.json')
            if flags['enable_semantic_clustering']:
                context['semantic_groups']=measured_generate('Return JSON semantic groups supported by this context. No tools.\n'+canonical(context),'semantic_clustering','graph')
            if flags['enable_intent_inference']:
                context['inferred_intent']=measured_generate('Return JSON with rules (array) and checks_source (Python defining check(inputs, outputs)->bool). Infer only from supplied inputs.\n'+canonical(context),'intent_inference','intent')
        elif flags['enable_semantic_clustering']:
            context['semantic_groups']={'origin':'authored_fixture_metadata_not_ai_inference','groups':[task['domain']]}
        if args.mode=='fixture' and flags['enable_intent_inference']:
            context['inferred_intent']={'origin':'authored_fixture_metadata_not_ai_inference','rules':['Preserve exact values, identity and idempotency key']}
        instruction='Return only JSON {"source": Python replacement for client.py or null, "abstain_reason": string or null}. No tools. Preserve public interface.\n'
        with tempfile.TemporaryDirectory(prefix='apishield-qualified-') as temporary:
            work=Path(temporary)
            for attempt in range(1,4 if args.mode=='live' and flags['enable_test_feedback'] else 2):
                attempts=attempt
                prompt=instruction+canonical(context)
                (artifacts/f'prompt_{attempt}.txt').write_text(prompt,encoding='utf-8')
                if args.mode=='fixture':candidate=read(BENCH/'fixture_candidates'/task['task_id']/f'{method}.json')
                else:
                    candidate=measured_generate(prompt,'repair','inference')
                    if not isinstance(candidate,dict):raise ValueError('Model candidate must be a JSON object')
                source=candidate.get('source')
                if source is None:
                    if not candidate.get('abstain_reason'):raise ValueError('Null source without explicit abstention reason')
                    abstain=True;break
                if not isinstance(source,str) or len(source.encode())>65536:raise ValueError('Replacement source exceeds allowed scope')
                diff=''.join(difflib.unified_diff(before.splitlines(True),source.splitlines(True),fromfile='a/client.py',tofile='b/client.py'))
                (artifacts/'candidate.patch').write_text(diff,encoding='utf-8')
                (work/'client.py').write_text(source,encoding='utf-8')
                try:ast.parse(source);syntax=True
                except SyntaxError as exc:
                    syntax=False
                    (artifacts/'syntax_error.json').write_text(canonical({'type':'SyntaxError','line':exc.lineno}),encoding='utf-8')
                    if args.mode=='fixture':break
                    context['visible_feedback']={'syntax_error_line':exc.lineno};continue
                if generation_only:break  # Capture actual inference; never execute untrusted code on host.
                if flags['enable_generated_checks']:
                    checks=candidate.get('checks_source') if args.mode=='fixture' else context['inferred_intent'].get('checks_source')
                    if not isinstance(checks,str) or len(checks.encode())>65536:raise ValueError('Missing or oversized generated checks')
                    ast.parse(checks)
                    (work/'generated_checks.py').write_text(checks,encoding='utf-8')
                inputs=read(task['inputs_path'])
                t=time.perf_counter_ns();result,value=execute(work,inputs,args.boundary,args.image)
                public_checks=judge(task['public_test_suite'],inputs,value['outputs'],args.boundary,args.image) if value and isinstance(value.get('outputs'),list) and len(value['outputs'])==len(inputs) else {'candidate_execution':False}
                generated_ok=bool(value and value.get('generated_checks_pass'))
                public_exit=0 if result.returncode==0 and all(public_checks.values()) else 1
                visible=0 if public_exit==0 and generated_ok else 1
                phases['visible_tests']+=(time.perf_counter_ns()-t)/1e9
                (artifacts/f'public_tests_{attempt}.json').write_text(canonical({'exit_code':visible,'public_test_exit_code':public_exit,'checks':public_checks,'worker_exit_code':result.returncode,'stdout':result.stdout[:65536],'stderr':result.stderr[:65536],'generated_checks_pass':generated_ok,'overall_visible_accepted':visible==0}),encoding='utf-8')
                if visible==0 and generated_ok:break
                context['visible_feedback']={'public_checks':public_checks,'generated_checks_pass':generated_ok}
            if syntax and not abstain and visible==0:
                # Final-only oracle. This block never precedes another model call.
                inputs=read(task['hidden_inputs_path'])
                t=time.perf_counter_ns();result,value=execute(work,inputs,args.boundary,args.image)
                invariants=judge(task['hidden_oracle_suite'],inputs,value['outputs'],args.boundary,args.image) if value and isinstance(value.get('outputs'),list) and len(value['outputs'])==len(inputs) else {'candidate_execution':False}
                hidden=0 if result.returncode==0 and all(invariants.values()) else 1
                phases['hidden_tests']=(time.perf_counter_ns()-t)/1e9
                (artifacts/'hidden_tests.json').write_text(canonical({'exit_code':hidden,'invariants_preserved':invariants,'worker_exit_code':result.returncode,'stdout':result.stdout[:65536],'stderr':result.stderr[:65536]}),encoding='utf-8')
    except Exception as exc:
        error=type(exc).__name__
    if model:calls=model.calls
    predicted=localize_with_treatment(task,flags,discovered,changed,context,candidate)
    tp=len(set(predicted)&truth);fp=len(set(predicted)-truth);fn=len(truth-set(predicted))
    (artifacts/'candidate_record.json').write_text(canonical(candidate),encoding='utf-8')
    elapsed=(time.perf_counter_ns()-start_ns)/1e9;end=datetime.now(timezone.utc)
    label=outcome(syntax,abstain,visible,hidden,generated_ok,error is not None)
    if generation_only and error is None and syntax and not abstain:label='NOT_EVALUATED'
    columns=(ROOT/'docs/academic-run-record-template.csv').read_text(encoding='utf-8').strip().split(',')
    record={key:None for key in columns}
    prompt_path=artifacts/f'prompt_{attempts}.txt'
    prompt_hash=sha(prompt_path.read_bytes()) if prompt_path.is_file() else None
    prompts=sum(x.get('prompt_tokens',0) for x in calls);cached=sum(x.get('cached_tokens',0) for x in calls)
    output=sum(x.get('output_tokens',0) for x in calls);reasoning=sum(x.get('reasoning_tokens',0) for x in calls)
    rate=read(BENCH/'profiles/rate_card.json')
    price=((prompts-cached)*rate['input_per_million']+cached*rate['cached_input_per_million']+(output+reasoning)*rate['output_including_reasoning_per_million'])/1e6 if args.provider=='google-cloud' else None
    if args.mode=='fixture':price=0.0
    if args.mode=='live' and any(x.get('http_status') is None for x in calls):price=None
    record.update(protocol_version='qualification-1',dataset_version='four-authored-fixtures-1',task_id=task['task_id'],family_id=task['family_id'],repository_id=task['repository_id'],
      task_origin='authored_fixture',task_class=task['task_class'],support_status='pure_request_builder_only',method=method,
      model_requested=profile.get('requested_model',profile.get('repository')) if args.mode=='live' else None,
      model_returned=next((x.get('resolved_model_version') for x in reversed(calls) if x.get('resolved_model_version')),None),provider=args.provider if args.mode=='live' else None,
      api_version='v1' if args.mode=='live' else None,sdk_version=importlib.metadata.version('google-genai') if args.mode=='live' and args.provider=='google-cloud' else None,
      timestamp_utc=start.isoformat(),repetition=args.repetition,randomization_block=0,tool_commit=observed_git_head(),
      source_hash=sha(before),accepted_contract_hash=sha(Path(task['old_contract_path']).read_bytes()),observed_contract_hash=sha(Path(task['new_contract_path']).read_bytes()),
      prompt_hash=prompt_hash,graph_hash=sha(canonical(graph)) if graph else None,graph_nodes=len(graph['functions']) if graph else 0,graph_edges=0,
      context_bytes=len(prompt_path.read_bytes()) if prompt_path.is_file() else 0,context_truncated=False,temperature=.1,top_p=.95,seed=42,reasoning_setting='LOW' if args.provider=='google-cloud' else None,
      max_output_tokens=4096,call_count=len(calls),attempt_count=attempts,input_tokens=prompts,output_tokens=output,reasoning_tokens=reasoning,cached_tokens=cached,
      detection_seconds=phases['detection'],graph_seconds=phases['graph'],intent_seconds=phases['intent'],generation_seconds=phases['inference'],
      validation_seconds=phases['visible_tests']+phases['hidden_tests'],total_seconds=elapsed,engine_outcome=label,hidden_outcome='PASS' if hidden==0 else 'FAIL' if hidden==1 else 'NOT_EXECUTED',
      failure_category=error,independent_correct=(hidden==0 if hidden is not None else None),unnecessary_edit=False,proper_abstention=False,patch_hash=sha(diff) if diff else None,
      environment_digest=sha(canonical({'python':sys.version,'boundary':args.boundary,'image':args.image})),reviewer_agreement=None,estimated_cost=price,currency='USD',pricing_date='2026-10-15')
    assert len(record)==56
    trace={'record_kind':'fixture_replay' if args.mode=='fixture' else 'live_model_execution',
      'run_id':ident,'task_id':task['task_id'],'configuration':method,'repetition_index':args.repetition,'timestamp_start':start.isoformat(),'timestamp_end':end.isoformat(),
      'requested_model':record['model_requested'],'resolved_model_version':record['model_returned'],'prompt_tokens':prompts,'cached_tokens':cached,'completion_tokens':output+reasoning,
      'raw_prompt_hash':prompt_hash,'generated_diff':diff,'visible_test_exit_code':visible,'hidden_oracle_exit_code':hidden,'invariants_preserved':invariants,
      'model_requested':record['model_requested'],'model_resolved':record['model_returned'],'model_response_diff':diff,
      't_detection_ms':phases['detection']*1000,'t_graph_ms':phases['graph']*1000,
      't_repair_ms':(phases['intent']+phases['inference'])*1000,'t_eval_ms':record['validation_seconds']*1000,
      'evaluation_status':'not_executed_generation_only' if generation_only else 'executed' if hidden is not None else 'not_completed',
      'classification':label,'flags':flags,'detection':{'true_positive':tp,'false_positive':fp,'false_negative':fn},'phases_seconds':phases,
      'overhead_seconds':elapsed-sum(phases.values()),'execution_boundary':args.boundary,'docker_isolation_verified':False,
      'hidden_results_never_used_for_retry':True,'fixture_candidate_origin':candidate.get('origin') if args.mode=='fixture' and candidate else None,'record':record}
    (destination/f'{ident}.json').write_text(json.dumps(trace,indent=2),encoding='utf-8')
    return trace

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['fixture','live'],default='fixture')
    p.add_argument('--configuration',choices=['all','B1','B2','B3','B4','B5','B6'],default='all')
    p.add_argument('--task',default='all');p.add_argument('--repetition',type=int,default=1)
    p.add_argument('--provider',choices=['google-cloud','llama-cpp'],default='google-cloud')
    p.add_argument('--boundary',choices=['trusted-fixtures','docker'],default='trusted-fixtures')
    p.add_argument('--image');p.add_argument('--execute-live',action='store_true')
    p.add_argument('--allow-unpinned-provider',action='store_true',help='Diagnostic mutable-provider runs only')
    p.add_argument('--generation-only',action='store_true',help='Capture paid model responses but execute no generated code; not evaluated repair evidence')
    p.add_argument('--output',type=Path,default=BENCH/'runs/qualification')
    args=p.parse_args()
    if args.mode=='live':
        if not args.execute_live or (not args.generation_only and args.boundary!='docker'):p.error('Live generation requires --execute-live and --boundary docker')
        if not args.generation_only and not valid_image(args.image):p.error('Supply an actually resolved container image digest')
        if args.provider=='google-cloud' and not read(BENCH/'profiles/gemini.json')['immutable_snapshot_verified'] and not args.allow_unpinned_provider:
            p.error('No immutable provider snapshot verified; diagnostic runs require --allow-unpinned-provider')
        if not args.generation_only:
            subprocess.run(['docker','info'],check=True,capture_output=True,timeout=15)
            subprocess.run(['docker','image','inspect',args.image],check=True,capture_output=True,timeout=15)
        else:args.boundary='no_candidate_execution'
    elif args.generation_only:p.error('--generation-only requires --mode live')
    if args.repetition<1:p.error('Repetition must be positive')
    tasks=read(BENCH/'tasks_manifest.json')['tasks'];configs=read(BENCH/'configurations.json')
    tasks=[x for x in tasks if args.task=='all' or x['task_id']==args.task]
    if not tasks:p.error('Unknown task')
    args.output.mkdir(parents=True,exist_ok=False)
    traces=[run_one(t,m,f,args,args.output) for t in tasks for m,f in configs.items() if args.configuration in ['all',m]]
    ledger=[]
    for x in traces:
        v=x['record'];ledger.append(dict(run_id=x['run_id'],record_kind=x['record_kind'],configuration=x['configuration'],task_id=x['task_id'],
          **{k+'_seconds':val for k,val in x['phases_seconds'].items()},overhead_seconds=x['overhead_seconds'],total_seconds=v['total_seconds'],
          prompt_tokens=x['prompt_tokens'],cached_tokens=x['cached_tokens'],completion_tokens=x['completion_tokens'],estimated_api_usd=v['estimated_cost'],
          measured_gpu_watts=None,measured_gpu_seconds=None,measured_energy_kwh=None,actual_invoice_usd=None))
    with (args.output/'resource_ledger.csv').open('w',newline='',encoding='utf-8') as file:
        w=csv.DictWriter(file,fieldnames=list(ledger[0]));w.writeheader();w.writerows(ledger)
    sources={path.relative_to(ROOT).as_posix():sha(path.read_bytes()) for directory in [BENCH/'harness',BENCH/'runners',BENCH/'adapters',BENCH/'tasks',BENCH/'evaluator_private',BENCH/'fixture_candidates',BENCH/'profiles',BENCH/'docker'] for path in directory.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
    for path in [BENCH/'tasks_manifest.json',BENCH/'tasks_manifest.schema.json',BENCH/'configurations.json',ROOT/'docs/academic-run-record-template.csv']:
        sources[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
    for path in BENCH.glob('*.txt'):
        sources[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
    (args.output/'source_manifest.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
    print(json.dumps({'record_kind':traces[0]['record_kind'],'traces':len(traces),'classifications':{t['run_id']:t['classification'] for t in traces}},indent=2))

if __name__=='__main__':main()
