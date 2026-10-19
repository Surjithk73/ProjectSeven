# APIShield artifact appendix: exact contents

Prepared 15 October 2026. These are authored fixture qualification records, not model-generated experimental results. Unknown model/engine/invoice fields are explicitly unobserved, not fabricated. No artifact badge or empirical-study validation is asserted.

# APIShield artifact and reproducibility appendix

Status on 15 October 2026: runnable qualification package, not a completed model benchmark and not an awarded artifact badge. Exact contents are supplied in ARTIFACT_APPENDIX.md. All retained sample traces are real executions of authored candidate fixtures; none is an LLM response. They cannot substantiate the earlier synthetic manuscript's numerical tables.

## 1. Experimental implementation and CLI

Repository HEAD observed: 80e7bbe0c01b58fa6615098c1bc56c6534a830eb. The working tree is dirty and that commit does not contain this new artifact. Each run captures a source_manifest.json of actual file SHA-256 values. No new commit, public archive, DOI or badge was created.

Implementation paths are under C:/Users/surji/ProjectSeven/benchmarks:

- harness/prepare_artifact.py materializes four actual fixtures, contracts, public suites, hidden suites and golden patches.
- harness/run_ablation.py implements the B1–B6 treatment gates and emits raw JSON evidence and a phase ledger.
- runners/candidate_worker.py executes the candidate's build_request interface.
- runners/evaluation.py maintains the controller/candidate boundary.
- adapters/model_backend.py contains explicit Google Cloud and llama.cpp adapters. No adapter falls back to another provider.
- harness/aggregate_metrics.py uses pandas and scipy.stats for metrics, Wilson intervals, paired case bootstrap and Cliff's delta.

The standalone harness does not import dashboard_api or frontend code. Live Google access reuses the production controller's credential/deadline client, not the UI. Fixture mode never imports or invokes the model adapter's generate method.

From the existing ProjectSeven checkout, these exact PowerShell commands reproduce the trusted offline fixtures in a fresh output directory:

```powershell
Set-Location C:/Users/surji/ProjectSeven
venv/Scripts/python.exe -B benchmarks/harness/prepare_artifact.py
venv/Scripts/python.exe -B benchmarks/harness/run_ablation.py --mode fixture --configuration all --task all --repetition 1 --boundary trusted-fixtures --output C:/Users/surji/ProjectSeven/benchmarks/runs/reproduction_01
benchmarks/.venv/Scripts/python.exe -B benchmarks/harness/aggregate_metrics.py --runs C:/Users/surji/ProjectSeven/benchmarks/runs/reproduction_01 --output C:/Users/surji/ProjectSeven/benchmarks/analysis/reproduction_01
```

For a clean installation, create the analysis environment with python -m venv benchmarks/.venv, then install benchmarks/requirements-analysis.txt. The live adapter additionally needs the project's backend dependencies and requirements-live.txt. Python used for qualification: 3.13.3. Existing output directories are refused to preserve evidence.

Configurations are exact JSON in configurations.json. Structural graph is on in B3–B6; semantic clustering in B4/B6; intent inference and generated checks in B5/B6; test feedback in B2–B6. Hidden-oracle evaluation is always enabled. It is an evaluator, not privileged generation context. B5/B6 have a separate enable_generated_checks flag so the independent evaluator is not confused with AI-generated acceptance checks.

Fixture mode exports real treatment-specific prompt contexts, but semantic groups and inferred rules are explicitly authored fixture metadata. The selected candidates intentionally exercise syntax failure, visible-but-incorrect output, abstention and success. This is instrumentation qualification, not a measurement of whether a graph improves model repair.

Live mode requires --mode live --execute-live --boundary docker and an existing image@sha256 digest. Google diagnostic runs additionally require --allow-unpinned-provider until an immutable release is verified. Docker was installed but its Linux daemon was unavailable during preparation. No Docker isolation execution is claimed and no live run was attempted. A supplied image is inspected before any model request.

## 2. Task manifest and physical oracle boundary

tasks_manifest.json and tasks_manifest.schema.json contain four complete records: TASK-BANK-014, TASK-BANK-015, TASK-SHIP-029 and TASK-PAY-008. Every referenced path exists. Public source/docs/tests are under tasks/TASK-ID/public; hidden oracle source, hidden inputs and golden patches are under evaluator_private/TASK-ID. Golden patches are checked with git apply and evaluated independently.

Prompt context is built from a positive allowlist: client.py, old/new documents, optionally public-test source, structural facts, semantic-stage response and inferred-intent-stage response. It is never built by recursively dumping a repository or task manifest. Private paths, oracle source, hidden results and golden patches are not copied into the candidate workspace or prompts.

The Docker candidate has only a read-only /work mount containing the candidate/generated checks and a read-only generic /runner.py mount. It has no host-project, private-oracle, model-credential or Docker-socket mount. Network access is disabled; filesystem is read-only except a bounded /tmp; capabilities are dropped; a non-root user, memory/CPU/PID limits and no-new-privileges are selected. Hidden inputs are sent only as concrete JSON test values. Assertions and expected results execute in the trusted controller outside the candidate container. Candidate outputs return through JSON. A model has no tool/filesystem interface.

The hidden evaluator is called only after the final candidate-selection loop. Its results are retained for the researcher and are never inserted into visible feedback or followed by another model call. The prompt-export tests confirm that private paths and reference-patch names do not appear in fixture prompts.

Trusted-fixtures mode uses native isolated Python processes only for the bundled authored candidates. It is not an OS security boundary and cannot be selected for live model-generated candidates. Docker-mode code has not been exercised on this host. The scaffold is not certified for adversarial repositories: additional output-volume, container lifecycle, source-exfiltration and hostile-runtime security testing is needed before such inputs are admitted. The four fixtures validate request construction and key preservation, not actual distributed banking state or duplicate-payment prevention under network races.

## 3. Original raw records

runs/qualification_verified contains 24 actual local qualification traces plus exported prompts, candidate records, patches, syntax diagnostics and public/hidden execution outputs. Six full representative traces are B1_TASK-BANK-014_rep1.json through B6_TASK-BANK-014_rep1.json. Each has the original 56-column record plus explicit aliases, phase records, boolean invariant maps and provenance.

The fixture traces have requested_model and resolved_model_version set to JSON null, token counts zero, and record_kind fixture_replay because no model was requested. Null here means not observed, not a slot populated with a fabricated identifier. Syntax errors and abstentions have null test exit codes when tests did not execute. Their invariant maps are empty, rather than falsely declaring unexecuted checks failed.

B1 is a genuine syntax-error execution record. B2 passes public tests but fails exact minor-unit preservation. B3 violates identity/destination. B4 is a scripted abstention. B5 violates key preservation. B6 passes the fixture's public and hidden checks. These candidates were authored in fixture_candidates, not produced by Gemini or Llama. Selection of these outcomes is intentional and supplies no performance ranking.

## 4. Model provenance

profiles/gemini.json records the current configured model ID gemini-3.8-flash, global endpoint and google-genai 2.22.0. It does not claim an immutable model snapshot: immutable_snapshot_verified is false and resolved_model_version is null until observed. Parameters are temperature 0.1, top_p 0.95, seed 42, max output 4096 and LOW reasoning. SDK content retries are disabled by the shared client; the research transport loop permits three retries at 1/2/4 seconds for 429/500/502/503/504. Three repair attempts are separate from transport retries. HTTP response metadata and usage are retained for any future live call.

The example gemini-1.5-pro-002 is a real historical release but was retired on 24 September 2025. It is not selected as a runnable current backend. Lifecycle source: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions .

The exact available quantized repository is bartowski/Meta-Llama-3.1-70B-Instruct-GGUF, revision 83fb6e83d0a8aada42d499259bc929d922e9a558. The published file is Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf, size 42,520,398,400 bytes, published LFS SHA-256 f775c87029be95fb41df9e2882e6e938b73121c30ffc235ac6b6b880add49aa5. Published metadata was fetched from https://huggingface.co/api/models/bartowski/Meta-Llama-3.1-70B-Instruct-GGUF?blobs=true . This is a published fingerprint, not a locally verified download. No weight file was downloaded, no engine build was measured and no GPU deployment was observed. The requested meta-llama/Meta-Llama-3.1-70B-Instruct-Q4_K_M name must not be substituted for this actual repository/file provenance.

profiles/llama_cpp.json supplies a concrete local weight path and llama-server command targeting two RTX A6000 48GB GPUs as a planning configuration. GGUF Q4_K_M is not AWQ. The local adapter refuses a missing or mismatched weight and an unrecorded engine version. Future operators must record actual hardware and engine builds; planned hardware cannot be reported as measured hardware. Command reference: https://github.com/ggml-org/llama.cpp/tree/master/tools/server .

## 5. Resource and billing accounting

runs/qualification_verified/resource_ledger.csv is measured local phase timing. Detection, graph, intent, inference, public evaluation, hidden evaluation and overhead reconcile to monotonic elapsed time. A zero inference duration and zero API charge reflect no inference calls, not free use of a proprietary service. CPU energy, GPU wattage and invoices were not measured and remain absent rather than invented.

profiles/rate_card.json records Google Cloud's published global introductory gemini-3.8-flash rates observed on 15 October 2026: USD 0.75 per million input tokens, 0.075 per million cached input tokens and 3.75 per million output/reasoning tokens, through 31 December 2026. Source: https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing . Cached input is a subset of input; reasoning is added to candidate output exactly once. Successful response usage is costed as ((input-cached)*0.75 + cached*0.075 + (candidate-output+reasoning)*3.75)/1,000,000. The official page lists no input/output charge for non-200 responses. Unknown transport outcomes require billing reconciliation; estimates are not invoices.

For a separately labelled planning scenario, energy_kWh = watts/1000 × GPU_active_seconds/3600 and electricity_USD = energy_kWh × tariff_USD_per_kWh. The profile's 600 W and USD 0.20/kWh are explicit assumptions for a proposed two-GPU target, not telemetry or official cloud billing. At 120 GPU-active seconds this scenario is 0.020000 kWh and USD 0.004000 electricity, excluding idle power, host power and capital costs. Actual GPU-active time is not available for these native fixture runs, so the scenario must not be inserted as measured ledger cost.

The aggregation pipeline joins ledger and traces on run_id and checks time/token reconciliation. Its output is analysis/qualification_verified/aggregate_metrics.csv and metrics.json. These are qualification summaries, not replacements for docs/academic-synthetic-reference tables and not a 3,600-run empirical dataset.

## 6. Statistical pipeline and classification rubric

aggregate_metrics.py reads and validates the 56 original columns, derives micro precision/recall from TP/FP/FN, reports public/hidden/delivered success separately, calculates Wilson intervals using scipy.stats.norm, calculates a case-preserving bootstrap and reports descriptive Cliff's delta plus a paired B6–B1 bootstrap contrast. Fixture and live records cannot be pooled. Repeated-task runs are retained together; a full study additionally needs the predeclared family-level hierarchy. Four deliberately selected fixtures do not support generalization or confirmatory significance claims.

Classification precedence:

- INFRASTRUCTURE_ERROR: provider, Docker or harness failure; never counted as appropriate model abstention.
- ABSTAIN/REFUSED: explicit abstention with no candidate; no hidden success is invented.
- SYNTAX_ERROR: candidate fails Python parsing before execution.
- PASS: public and hidden checks pass and enabled generated checks pass.
- PLAUSIBLE_BUT_INCORRECT: public checks and enabled generated checks pass, but hidden checks fail.
- TEST_FAILURE: remaining candidate/test failures, including failed public checks or rejected generated checks.

The two extra classes are necessary: the four requested labels alone cannot faithfully represent public-test failures and infrastructure outages.

## Validation and remaining archival gates

Qualification ran all six configurations over all four fixtures, generated 24 traces and exercised the statistical pipeline. Regression checks cover classification, common hidden evaluation, golden patch application, prompt/oracle separation and refusal of live native execution. These checks do not certify Docker isolation or live backend compatibility.

Before archival as an empirical-study artifact, obtain actual model/snapshot provenance, run and audit the Docker boundary, freeze an actual artifact revision/archive digest, qualify the complete benchmark, collect real model responses and patches, reconcile actual billing/telemetry and regenerate study results. Deposit in a durable repository and seek the venue's evaluation. Packaging alone cannot award Artifacts Evaluated, Artifacts Available or Results Validated badges. ACM policy: https://www.acm.org/publications/policies/artifact-review-and-badging-current .


## 1. Exact implementation and configuration


### C:/Users/surji/ProjectSeven/benchmarks/provenance/repository.json

SHA-256: fa834c9ae9482790b5a2ca4d1a30db0676257089162968b010815cf536ba50d3

```json
{
  "head": "80e7bbe0c01b58fa6615098c1bc56c6534a830eb",
  "working_tree_clean": false,
  "head_is_not_artifact_revision": true,
  "note": "Uncommitted artifact source is identified by source_manifest.json; no new commit was created."
}
```


### C:/Users/surji/ProjectSeven/benchmarks/configurations.json

SHA-256: 5ac2ec57a57072b398dff6e10f76edbd9fdc67a9f274bda24620cc25050258e6

```json
{
  "B1": {
    "enable_structural_graph": false,
    "enable_semantic_clustering": false,
    "enable_intent_inference": false,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": false,
    "enable_test_feedback": false
  },
  "B2": {
    "enable_structural_graph": false,
    "enable_semantic_clustering": false,
    "enable_intent_inference": false,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": false,
    "enable_test_feedback": true
  },
  "B3": {
    "enable_structural_graph": true,
    "enable_semantic_clustering": false,
    "enable_intent_inference": false,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": false,
    "enable_test_feedback": true
  },
  "B4": {
    "enable_structural_graph": true,
    "enable_semantic_clustering": true,
    "enable_intent_inference": false,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": false,
    "enable_test_feedback": true
  },
  "B5": {
    "enable_structural_graph": true,
    "enable_semantic_clustering": false,
    "enable_intent_inference": true,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": true,
    "enable_test_feedback": true
  },
  "B6": {
    "enable_structural_graph": true,
    "enable_semantic_clustering": true,
    "enable_intent_inference": true,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": true,
    "enable_test_feedback": true
  }
}
```


### C:/Users/surji/ProjectSeven/benchmarks/harness/run_ablation.py

SHA-256: 7f913d0c8e358cac718f42601a148fad5f6c30e5b773fe91c30acd5d4c58d6d6

```python
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
from benchmarks.runners.evaluation import execute,judge
from benchmarks.adapters.model_backend import Backend
BENCH=ROOT/'benchmarks'

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(value):return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=True)

def structural(source):
    tree=ast.parse(source)
    return {'functions':[n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)],
            'literal_paths':sorted({n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('/')}),
            'basis':'python_ast; unresolved dynamic paths excluded'}

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
    predicted=['client.py:build_request'] if changed and discovered['literal_paths'] else []
    truth=set(task['ground_truth_affected_locations'])
    tp=len(set(predicted)&truth);fp=len(set(predicted)-truth);fn=len(truth-set(predicted))
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
    profile=read(BENCH/'profiles'/('gemini.json' if args.provider=='google-cloud' else 'llama_cpp.json'))
    try:
        if args.mode=='live':
            model=Backend(args.provider,profile,artifacts/'model_calls.json')
            if flags['enable_semantic_clustering']:
                t=time.perf_counter_ns()
                context['semantic_groups']=model.generate('Return JSON semantic groups supported by this context. No tools.\n'+canonical(context),'semantic_clustering')
                phases['graph']+=(time.perf_counter_ns()-t)/1e9
            if flags['enable_intent_inference']:
                t=time.perf_counter_ns()
                context['inferred_intent']=model.generate('Return JSON with rules (array) and checks_source (Python defining check(inputs, outputs)->bool). Infer only from supplied inputs.\n'+canonical(context),'intent_inference')
                phases['intent']=(time.perf_counter_ns()-t)/1e9
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
                    t=time.perf_counter_ns();candidate=model.generate(prompt,'repair');phases['inference']+=(time.perf_counter_ns()-t)/1e9
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
                if flags['enable_generated_checks']:
                    checks=candidate.get('checks_source') if args.mode=='fixture' else context['inferred_intent'].get('checks_source')
                    if not isinstance(checks,str) or len(checks.encode())>65536:raise ValueError('Missing or oversized generated checks')
                    ast.parse(checks)
                    (work/'generated_checks.py').write_text(checks,encoding='utf-8')
                inputs=read(task['inputs_path'])
                t=time.perf_counter_ns();result,value=execute(work,inputs,args.boundary,args.image)
                public_checks=judge(task['public_test_suite'],inputs,value['outputs']) if value and isinstance(value.get('outputs'),list) and len(value['outputs'])==len(inputs) else {'candidate_execution':False}
                generated_ok=bool(value and value.get('generated_checks_pass'))
                visible=0 if result.returncode==0 and all(public_checks.values()) else 1
                phases['visible_tests']+=(time.perf_counter_ns()-t)/1e9
                (artifacts/f'public_tests_{attempt}.json').write_text(canonical({'exit_code':visible,'checks':public_checks,'worker_exit_code':result.returncode,'stdout':result.stdout[:65536],'stderr':result.stderr[:65536],'generated_checks_pass':generated_ok}),encoding='utf-8')
                if visible==0 and generated_ok:break
                context['visible_feedback']={'public_checks':public_checks,'generated_checks_pass':generated_ok}
            if syntax and not abstain and visible==0:
                # Final-only oracle. This block never precedes another model call.
                inputs=read(task['hidden_inputs_path'])
                t=time.perf_counter_ns();result,value=execute(work,inputs,args.boundary,args.image)
                invariants=judge(task['hidden_oracle_suite'],inputs,value['outputs']) if value and isinstance(value.get('outputs'),list) and len(value['outputs'])==len(inputs) else {'candidate_execution':False}
                hidden=0 if result.returncode==0 and all(invariants.values()) else 1
                phases['hidden_tests']=(time.perf_counter_ns()-t)/1e9
                (artifacts/'hidden_tests.json').write_text(canonical({'exit_code':hidden,'invariants_preserved':invariants,'worker_exit_code':result.returncode,'stdout':result.stdout[:65536],'stderr':result.stderr[:65536]}),encoding='utf-8')
    except Exception as exc:
        error=type(exc).__name__
    if model:calls=model.calls
    (artifacts/'candidate_record.json').write_text(canonical(candidate),encoding='utf-8')
    elapsed=(time.perf_counter_ns()-start_ns)/1e9;end=datetime.now(timezone.utc)
    label=outcome(syntax,abstain,visible,hidden,generated_ok,error is not None)
    columns=(ROOT/'docs/academic-run-record-template.csv').read_text(encoding='utf-8').strip().split(',')
    record={key:None for key in columns}
    prompt_path=artifacts/f'prompt_{attempts}.txt'
    prompt_hash=sha(prompt_path.read_bytes()) if prompt_path.is_file() else None
    prompts=sum(x.get('prompt_tokens',0) for x in calls);cached=sum(x.get('cached_tokens',0) for x in calls)
    output=sum(x.get('output_tokens',0) for x in calls);reasoning=sum(x.get('reasoning_tokens',0) for x in calls)
    rate=read(BENCH/'profiles/rate_card.json')
    price=((prompts-cached)*rate['input_per_million']+cached*rate['cached_input_per_million']+(output+reasoning)*rate['output_including_reasoning_per_million'])/1e6 if args.provider=='google-cloud' else None
    if args.mode=='fixture':price=0.0
    record.update(protocol_version='qualification-1',dataset_version='four-authored-fixtures-1',task_id=task['task_id'],family_id=task['family_id'],repository_id=task['repository_id'],
      task_origin='authored_fixture',task_class=task['task_class'],support_status='pure_request_builder_only',method=method,
      model_requested=profile.get('requested_model',profile.get('repository')) if args.mode=='live' else None,
      model_returned=next((x.get('resolved_model_version') for x in reversed(calls) if x.get('resolved_model_version')),None),provider=args.provider if args.mode=='live' else None,
      api_version='v1' if args.mode=='live' else None,sdk_version=importlib.metadata.version('google-genai') if args.mode=='live' and args.provider=='google-cloud' else None,
      timestamp_utc=start.isoformat(),repetition=args.repetition,randomization_block=0,tool_commit=read(BENCH/'provenance/repository.json')['head'],
      source_hash=sha(before),accepted_contract_hash=sha(Path(task['old_contract_path']).read_bytes()),observed_contract_hash=sha(Path(task['new_contract_path']).read_bytes()),
      prompt_hash=prompt_hash,graph_hash=sha(canonical(graph)) if graph else None,graph_nodes=len(graph['functions']) if graph else 0,graph_edges=0,
      context_bytes=len(prompt_path.read_bytes()) if prompt_path.is_file() else 0,context_truncated=False,temperature=.1,top_p=.95,seed=42,reasoning_setting='LOW' if args.provider=='google-cloud' else None,
      max_output_tokens=4096,call_count=len(calls),attempt_count=attempts,input_tokens=prompts,output_tokens=output,reasoning_tokens=reasoning,cached_tokens=cached,
      detection_seconds=phases['detection'],graph_seconds=phases['graph'],intent_seconds=phases['intent'],generation_seconds=phases['inference'],
      validation_seconds=phases['visible_tests']+phases['hidden_tests'],total_seconds=elapsed,engine_outcome=label,hidden_outcome='PASS' if hidden==0 else 'FAIL' if hidden==1 else 'NOT_EXECUTED',
      failure_category=error,independent_correct=hidden==0,unnecessary_edit=False,proper_abstention=False,patch_hash=sha(diff) if diff else None,
      environment_digest=sha(canonical({'python':sys.version,'boundary':args.boundary,'image':args.image})),reviewer_agreement=None,estimated_cost=price,currency='USD',pricing_date='2026-10-15')
    assert len(record)==56
    trace={'record_kind':'fixture_replay' if args.mode=='fixture' else 'live_model_execution',
      'run_id':ident,'task_id':task['task_id'],'configuration':method,'repetition_index':args.repetition,'timestamp_start':start.isoformat(),'timestamp_end':end.isoformat(),
      'requested_model':record['model_requested'],'resolved_model_version':record['model_returned'],'prompt_tokens':prompts,'cached_tokens':cached,'completion_tokens':output+reasoning,
      'raw_prompt_hash':prompt_hash,'generated_diff':diff,'visible_test_exit_code':visible,'hidden_oracle_exit_code':hidden,'invariants_preserved':invariants,
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
    p.add_argument('--output',type=Path,default=BENCH/'runs/qualification')
    args=p.parse_args()
    if args.mode=='live':
        if not args.execute_live or args.boundary!='docker':p.error('Live generation requires --execute-live and --boundary docker')
        if not args.image or not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}',args.image):p.error('Supply an actually resolved container image digest')
        if args.provider=='google-cloud' and not read(BENCH/'profiles/gemini.json')['immutable_snapshot_verified'] and not args.allow_unpinned_provider:
            p.error('No immutable provider snapshot verified; diagnostic runs require --allow-unpinned-provider')
        subprocess.run(['docker','info'],check=True,capture_output=True,timeout=15)
        subprocess.run(['docker','image','inspect',args.image],check=True,capture_output=True,timeout=15)
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
    sources={path.relative_to(ROOT).as_posix():sha(path.read_bytes()) for directory in [BENCH/'harness',BENCH/'runners',BENCH/'adapters',BENCH/'tasks',BENCH/'evaluator_private',BENCH/'fixture_candidates',BENCH/'profiles'] for path in directory.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
    for path in [BENCH/'tasks_manifest.json',BENCH/'tasks_manifest.schema.json',BENCH/'configurations.json',ROOT/'docs/academic-run-record-template.csv']:
        sources[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
    for path in BENCH.glob('*.txt'):
        sources[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
    (args.output/'source_manifest.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
    print(json.dumps({'record_kind':traces[0]['record_kind'],'traces':len(traces),'classifications':{t['run_id']:t['classification'] for t in traces}},indent=2))

if __name__=='__main__':main()
```


### C:/Users/surji/ProjectSeven/benchmarks/adapters/model_backend.py

SHA-256: 7c8d626c8333717649974423bca7c9c69af7d5bc9e0562e30d746ea681f7a858

```python
"""Explicit research backend. Fixture mode never calls this adapter."""
import hashlib
import json
import time
from pathlib import Path

class Backend:
    def __init__(self, provider, profile, output):
        self.provider,self.profile,self.output=provider,profile,output
        self.calls=[]
        if provider=='llama-cpp':
            path=Path(profile['local_weight_path'])
            if not path.is_file():raise ValueError('Configured GGUF file is absent; no local provenance can be asserted')
            digest=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
            if digest != profile['published_weight_sha256']:raise ValueError('Local GGUF hash does not match pinned published fingerprint')
            if not profile['inference_engine_version']:raise ValueError('Record the actual llama-server build version before live research')

    def generate(self, prompt, stage):
        import httpx
        last=None
        for retry in range(4):
            start=time.perf_counter()
            call={'stage':stage,'retry_index':retry,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'raw_prompt':prompt,
                  'generation_parameters':{'temperature':.1,'top_p':.95,'seed':42,'max_output_tokens':4096}}
            try:
                if self.provider=='google-cloud':
                    from apishield.model_access import environment_connection,model_client
                    from google.genai import types
                    with model_client(environment_connection(),time.monotonic()+120) as client:
                        result=client.models.generate_content(model=self.profile['requested_model'],contents=prompt,
                            config=types.GenerateContentConfig(temperature=.1,top_p=.95,seed=42,max_output_tokens=4096,
                                response_mime_type='application/json',thinking_config=types.ThinkingConfig(thinking_level='LOW'),
                                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)))
                    usage=result.usage_metadata
                    call.update(resolved_model_version=getattr(result,'model_version',None),
                                prompt_tokens=getattr(usage,'prompt_token_count',0) or 0,cached_tokens=getattr(usage,'cached_content_token_count',0) or 0,
                                output_tokens=getattr(usage,'candidates_token_count',0) or 0,reasoning_tokens=getattr(usage,'thoughts_token_count',0) or 0,
                                response=result.model_dump(mode='json'),response_text=result.text,http_status=200)
                else:
                    body={'model':self.profile['repository'],'messages':[{'role':'user','content':prompt}],
                          'temperature':.1,'top_p':.95,'seed':42,'max_tokens':4096,'stream':False}
                    response=httpx.post(self.profile['endpoint'],json=body,timeout=120);response.raise_for_status()
                    result=response.json();usage=result.get('usage',{})
                    call.update(resolved_model_version=result.get('model'),prompt_tokens=usage.get('prompt_tokens',0),cached_tokens=0,
                                output_tokens=usage.get('completion_tokens',0),reasoning_tokens=0,response=result,
                                response_text=result['choices'][0]['message']['content'],http_status=200)
                parsed=json.loads(call['response_text'])
                call['elapsed_seconds']=time.perf_counter()-start
                self.calls.append(call);self._save()
                return parsed
            except Exception as error:
                status=getattr(error,'code',None) or getattr(getattr(error,'response',None),'status_code',None)
                call.update(elapsed_seconds=time.perf_counter()-start,http_status=call.get('http_status',status),error_category=type(error).__name__)
                self.calls.append(call);self._save();last=error
                if status not in [429,500,502,503,504] or retry==3:break
                time.sleep([1,2,4][retry])
        raise RuntimeError(f'Model request failed; category={type(last).__name__}; no provider fallback') from None

    def _save(self):
        self.output.write_text(json.dumps(self.calls,indent=2),encoding='utf-8')
```


### C:/Users/surji/ProjectSeven/benchmarks/runners/candidate_worker.py

SHA-256: 9de37b776f8b26d4d4242325a69c0b45fef492a789dff4e0955f917facde49d6

```python
"""Candidate-side protocol. No hidden oracle or reference patch is mounted here."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import client

inputs = json.load(sys.stdin)
outputs = [client.build_request(item) for item in inputs]
checks_ok = True
if Path('generated_checks.py').exists():
    import generated_checks
    checks_ok = bool(generated_checks.check(inputs, outputs))
print(json.dumps({'outputs': outputs, 'generated_checks_pass': checks_ok}, ensure_ascii=True))
```


### C:/Users/surji/ProjectSeven/benchmarks/runners/evaluation.py

SHA-256: e9034d4e326de18bd290c255582d134ff13d3006d0976138c69256205e70c32e

```python
"""Controller-side test execution; oracle source never enters candidate mounts."""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

WORKER=Path(__file__).with_name('candidate_worker.py')

def execute(workspace, inputs, boundary, image=None):
    if boundary == 'docker':
        if not image or not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}',image):
            raise ValueError('Docker execution requires an actually resolved image@sha256 digest')
        cmd=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL',
             '--security-opt','no-new-privileges','--pids-limit','64','--memory','512m','--cpus','1',
             '--tmpfs','/tmp:rw,noexec,nosuid,size=64m','--user','65534:65534',
             '--mount',f'type=bind,source={workspace.resolve()},target=/work,readonly',
             '--mount',f'type=bind,source={WORKER.resolve()},target=/runner.py,readonly',
             '--workdir','/work','-i',image,'python','-B','/runner.py']
    elif boundary == 'trusted-fixtures':
        cmd=[sys.executable,'-I','-B',str(WORKER)]
    else:raise ValueError('Unknown execution boundary')
    result=subprocess.run(cmd,input=json.dumps(inputs),text=True,capture_output=True,cwd=workspace,timeout=30,
                          env={'SYSTEMROOT':__import__('os').environ.get('SYSTEMROOT','C:/Windows'), 'PYTHONIOENCODING':'utf-8'})
    value=None
    if result.returncode==0:
        try:value=json.loads(result.stdout)
        except ValueError:pass
    return result,value

def judge(suite, inputs, outputs):
    spec=importlib.util.spec_from_file_location('qualification_oracle',suite)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    try:
        checks=module.evaluate(inputs,outputs)
        if not isinstance(checks,dict) or not checks or any(type(v) is not bool for v in checks.values()):
            raise ValueError('Oracle must return nonempty named boolean assertions')
        return checks
    except (KeyError,TypeError,IndexError):return {'oracle_contract':False}
```


### C:/Users/surji/ProjectSeven/benchmarks/requirements-analysis.txt

SHA-256: 4f450afc46fa39e53a8b0c4c87f828986cab6696b6279046b1e05b20c9afaa63

```text
numpy==2.5.4
pandas==2.3.3
scipy==1.16.3
python-dateutil==2.9.0.post0
pytz==2026.5
six==1.17.0
tzdata==2026.5
```


### C:/Users/surji/ProjectSeven/benchmarks/requirements-live.txt

SHA-256: b9f5ff61c822308e163e892ff87f1e2d64e72e054e7673886620de2ffafb3058

```text
google-genai==2.22.0
httpx==0.28.1
```


## 2. Exact executable task schema and four manifest records


### C:/Users/surji/ProjectSeven/benchmarks/tasks_manifest.schema.json

SHA-256: 8b980c4f19594b7d5924997e44428bc5c1cde2e856e11760df0629bb5f62e332

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "record_kind",
    "tasks"
  ],
  "properties": {
    "schema_version": {
      "const": 1
    },
    "record_kind": {
      "const": "runnable_local_qualification_fixtures"
    },
    "tasks": {
      "type": "array",
      "minItems": 4,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "task_id",
          "domain",
          "task_class",
          "family_id",
          "repository_id",
          "source_directory",
          "old_contract_path",
          "new_contract_path",
          "public_test_suite",
          "hidden_oracle_suite",
          "golden_reference_patch",
          "inputs_path",
          "allowed_edit_paths",
          "ground_truth_affected_locations",
          "hidden_inputs_path"
        ],
        "properties": {
          "task_id": {
            "type": "string",
            "minLength": 1
          },
          "domain": {
            "type": "string",
            "minLength": 1
          },
          "task_class": {
            "type": "string",
            "minLength": 1
          },
          "family_id": {
            "type": "string",
            "minLength": 1
          },
          "repository_id": {
            "type": "string",
            "minLength": 1
          },
          "source_directory": {
            "type": "string",
            "minLength": 1
          },
          "old_contract_path": {
            "type": "string",
            "minLength": 1
          },
          "new_contract_path": {
            "type": "string",
            "minLength": 1
          },
          "public_test_suite": {
            "type": "string",
            "minLength": 1
          },
          "hidden_oracle_suite": {
            "type": "string",
            "minLength": 1
          },
          "golden_reference_patch": {
            "type": "string",
            "minLength": 1
          },
          "inputs_path": {
            "type": "string",
            "minLength": 1
          },
          "allowed_edit_paths": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "ground_truth_affected_locations": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "hidden_inputs_path": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    }
  }
}
```


### C:/Users/surji/ProjectSeven/benchmarks/tasks_manifest.json

SHA-256: afe8db6d42a50186d5fb80bc845e7584fdc4bfc008d11719fbd9a7c1e36fede5

```json
{
  "schema_version": 1,
  "record_kind": "runnable_local_qualification_fixtures",
  "tasks": [
    {
      "task_id": "TASK-BANK-014",
      "domain": "Banking",
      "task_class": "repairable",
      "family_id": "banking-qualification",
      "repository_id": "local-authored-fixture",
      "source_directory": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-014/public",
      "old_contract_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-014/public/old_contract.json",
      "new_contract_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-014/public/new_contract.json",
      "public_test_suite": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-014/public/test_public.py",
      "hidden_oracle_suite": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-BANK-014/oracle.py",
      "golden_reference_patch": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-BANK-014/golden.patch",
      "inputs_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-014/public/inputs.json",
      "allowed_edit_paths": [
        "client.py"
      ],
      "ground_truth_affected_locations": [
        "client.py:build_request"
      ],
      "hidden_inputs_path": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-BANK-014/inputs.json"
    },
    {
      "task_id": "TASK-BANK-015",
      "domain": "Banking",
      "task_class": "repairable",
      "family_id": "banking-qualification",
      "repository_id": "local-authored-fixture",
      "source_directory": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-015/public",
      "old_contract_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-015/public/old_contract.json",
      "new_contract_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-015/public/new_contract.json",
      "public_test_suite": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-015/public/test_public.py",
      "hidden_oracle_suite": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-BANK-015/oracle.py",
      "golden_reference_patch": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-BANK-015/golden.patch",
      "inputs_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-BANK-015/public/inputs.json",
      "allowed_edit_paths": [
        "client.py"
      ],
      "ground_truth_affected_locations": [
        "client.py:build_request"
      ],
      "hidden_inputs_path": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-BANK-015/inputs.json"
    },
    {
      "task_id": "TASK-SHIP-029",
      "domain": "Shipping",
      "task_class": "repairable",
      "family_id": "shipping-qualification",
      "repository_id": "local-authored-fixture",
      "source_directory": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-SHIP-029/public",
      "old_contract_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-SHIP-029/public/old_contract.json",
      "new_contract_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-SHIP-029/public/new_contract.json",
      "public_test_suite": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-SHIP-029/public/test_public.py",
      "hidden_oracle_suite": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-SHIP-029/oracle.py",
      "golden_reference_patch": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-SHIP-029/golden.patch",
      "inputs_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-SHIP-029/public/inputs.json",
      "allowed_edit_paths": [
        "client.py"
      ],
      "ground_truth_affected_locations": [
        "client.py:build_request"
      ],
      "hidden_inputs_path": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-SHIP-029/inputs.json"
    },
    {
      "task_id": "TASK-PAY-008",
      "domain": "Payment",
      "task_class": "repairable",
      "family_id": "payment-qualification",
      "repository_id": "local-authored-fixture",
      "source_directory": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-PAY-008/public",
      "old_contract_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-PAY-008/public/old_contract.json",
      "new_contract_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-PAY-008/public/new_contract.json",
      "public_test_suite": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-PAY-008/public/test_public.py",
      "hidden_oracle_suite": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-PAY-008/oracle.py",
      "golden_reference_patch": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-PAY-008/golden.patch",
      "inputs_path": "C:/Users/surji/ProjectSeven/benchmarks/tasks/TASK-PAY-008/public/inputs.json",
      "allowed_edit_paths": [
        "client.py"
      ],
      "ground_truth_affected_locations": [
        "client.py:build_request"
      ],
      "hidden_inputs_path": "C:/Users/surji/ProjectSeven/benchmarks/evaluator_private/TASK-PAY-008/inputs.json"
    }
  ]
}
```


## 3. Six complete original fixture execution traces


### C:/Users/surji/ProjectSeven/benchmarks/runs/qualification_verified/B1_TASK-BANK-014_rep1.json

SHA-256: 467511f57866add2d503e29813ff2b48ce2a51c7406fff5098fa7851c568b702

```json
{
  "record_kind": "fixture_replay",
  "run_id": "B1_TASK-BANK-014_rep1",
  "task_id": "TASK-BANK-014",
  "configuration": "B1",
  "repetition_index": 1,
  "timestamp_start": "2026-10-15T02:23:47.087247+00:00",
  "timestamp_end": "2026-10-15T02:23:47.121437+00:00",
  "requested_model": null,
  "resolved_model_version": null,
  "prompt_tokens": 0,
  "cached_tokens": 0,
  "completion_tokens": 0,
  "raw_prompt_hash": "2fc970a89b1c0c5b902085df9a0daa06f6e35b544cbac6fcbb2e0ebcc61d3fa2",
  "generated_diff": "--- a/client.py\n+++ b/client.py\n@@ -1,2 +1,2 @@\n-def build_request(data):\n-    return {'path': '/transfers', 'body': {'amount_cents': data['amount_cents']}, 'headers': {}}\n+def build_request(data)\n+    return {}\n",
  "visible_test_exit_code": null,
  "hidden_oracle_exit_code": null,
  "invariants_preserved": {},
  "classification": "SYNTAX_ERROR",
  "flags": {
    "enable_structural_graph": false,
    "enable_semantic_clustering": false,
    "enable_intent_inference": false,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": false,
    "enable_test_feedback": false
  },
  "detection": {
    "true_positive": 1,
    "false_positive": 0,
    "false_negative": 0
  },
  "phases_seconds": {
    "detection": 0.0005821,
    "graph": 1.3e-06,
    "intent": 0.0,
    "inference": 0.0,
    "visible_tests": 0.0,
    "hidden_tests": 0.0
  },
  "overhead_seconds": 0.0336064,
  "execution_boundary": "trusted-fixtures",
  "docker_isolation_verified": false,
  "hidden_results_never_used_for_retry": true,
  "fixture_candidate_origin": "trusted_fixture_not_model_output",
  "record": {
    "protocol_version": "qualification-1",
    "dataset_version": "four-authored-fixtures-1",
    "task_id": "TASK-BANK-014",
    "family_id": "banking-qualification",
    "repository_id": "local-authored-fixture",
    "task_origin": "authored_fixture",
    "task_class": "repairable",
    "support_status": "pure_request_builder_only",
    "method": "B1",
    "model_requested": null,
    "model_returned": null,
    "provider": null,
    "api_version": null,
    "sdk_version": null,
    "timestamp_utc": "2026-10-15T02:23:47.087247+00:00",
    "repetition": 1,
    "randomization_block": 0,
    "tool_commit": "80e7bbe0c01b58fa6615098c1bc56c6534a830eb",
    "source_hash": "27be638eaa929291b3eee703b160a8e87963461dc42c3275e4826568d8d6af21",
    "accepted_contract_hash": "bcdd6643664991578b65bcc097277334e92b3167de6b219dc882179f88b381cb",
    "observed_contract_hash": "a39ee7bde4fd2eb17b3f6eb866a1333fc9234a1edee0149bc63441ff9f6c9954",
    "prompt_hash": "2fc970a89b1c0c5b902085df9a0daa06f6e35b544cbac6fcbb2e0ebcc61d3fa2",
    "graph_hash": null,
    "graph_nodes": 0,
    "graph_edges": 0,
    "context_bytes": 1275,
    "context_truncated": false,
    "temperature": 0.1,
    "top_p": 0.95,
    "seed": 42,
    "reasoning_setting": "LOW",
    "max_output_tokens": 4096,
    "call_count": 0,
    "attempt_count": 1,
    "input_tokens": 0,
    "output_tokens": 0,
    "reasoning_tokens": 0,
    "cached_tokens": 0,
    "detection_seconds": 0.0005821,
    "graph_seconds": 1.3e-06,
    "intent_seconds": 0.0,
    "generation_seconds": 0.0,
    "validation_seconds": 0.0,
    "total_seconds": 0.0341898,
    "engine_outcome": "SYNTAX_ERROR",
    "hidden_outcome": "NOT_EXECUTED",
    "failure_category": null,
    "independent_correct": false,
    "unnecessary_edit": false,
    "proper_abstention": false,
    "patch_hash": "f018a8b0fced3bafb23a3fc26490abae5bbd2ba7e0884498f7e82a687822ffae",
    "environment_digest": "de41581c8c78222120edd0ff3d507bb593f8dad78803e284c3673f4b3eb5c0ac",
    "reviewer_agreement": null,
    "estimated_cost": 0.0,
    "currency": "USD",
    "pricing_date": "2026-10-15"
  }
}
```


### C:/Users/surji/ProjectSeven/benchmarks/runs/qualification_verified/B2_TASK-BANK-014_rep1.json

SHA-256: bac1f320a512c7859415ec865e1290582f4e322e2ccceffb48aaf214a6f0dd0b

```json
{
  "record_kind": "fixture_replay",
  "run_id": "B2_TASK-BANK-014_rep1",
  "task_id": "TASK-BANK-014",
  "configuration": "B2",
  "repetition_index": 1,
  "timestamp_start": "2026-10-15T02:23:47.135030+00:00",
  "timestamp_end": "2026-10-15T02:23:47.727132+00:00",
  "requested_model": null,
  "resolved_model_version": null,
  "prompt_tokens": 0,
  "cached_tokens": 0,
  "completion_tokens": 0,
  "raw_prompt_hash": "74f44f4365f1545dda34dffafec17967240967519c59be4e341d475e4ac742a6",
  "generated_diff": "--- a/client.py\n+++ b/client.py\n@@ -1,2 +1,2 @@\n def build_request(data):\n-    return {'path': '/transfers', 'body': {'amount_cents': data['amount_cents']}, 'headers': {}}\n+    return {'path': '/transfers', 'body': {'source': data['source'], 'destination': data['destination'], 'amount': {'value': data['amount_cents'] / 100, 'currency': data['currency']}}, 'headers': {'Idempotency-Key': data['idempotency_key']}}\n",
  "visible_test_exit_code": 0,
  "hidden_oracle_exit_code": 1,
  "invariants_preserved": {
    "exact_minor_units": false,
    "currency": true,
    "destination": true,
    "idempotency_key": true
  },
  "classification": "PLAUSIBLE_BUT_INCORRECT",
  "flags": {
    "enable_structural_graph": false,
    "enable_semantic_clustering": false,
    "enable_intent_inference": false,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": false,
    "enable_test_feedback": true
  },
  "detection": {
    "true_positive": 1,
    "false_positive": 0,
    "false_negative": 0
  },
  "phases_seconds": {
    "detection": 0.0005158,
    "graph": 3.7e-06,
    "intent": 0.0,
    "inference": 0.0,
    "visible_tests": 0.29178,
    "hidden_tests": 0.280133
  },
  "overhead_seconds": 0.019664299999999968,
  "execution_boundary": "trusted-fixtures",
  "docker_isolation_verified": false,
  "hidden_results_never_used_for_retry": true,
  "fixture_candidate_origin": "trusted_fixture_not_model_output",
  "record": {
    "protocol_version": "qualification-1",
    "dataset_version": "four-authored-fixtures-1",
    "task_id": "TASK-BANK-014",
    "family_id": "banking-qualification",
    "repository_id": "local-authored-fixture",
    "task_origin": "authored_fixture",
    "task_class": "repairable",
    "support_status": "pure_request_builder_only",
    "method": "B2",
    "model_requested": null,
    "model_returned": null,
    "provider": null,
    "api_version": null,
    "sdk_version": null,
    "timestamp_utc": "2026-10-15T02:23:47.135030+00:00",
    "repetition": 1,
    "randomization_block": 0,
    "tool_commit": "80e7bbe0c01b58fa6615098c1bc56c6534a830eb",
    "source_hash": "27be638eaa929291b3eee703b160a8e87963461dc42c3275e4826568d8d6af21",
    "accepted_contract_hash": "bcdd6643664991578b65bcc097277334e92b3167de6b219dc882179f88b381cb",
    "observed_contract_hash": "a39ee7bde4fd2eb17b3f6eb866a1333fc9234a1edee0149bc63441ff9f6c9954",
    "prompt_hash": "74f44f4365f1545dda34dffafec17967240967519c59be4e341d475e4ac742a6",
    "graph_hash": null,
    "graph_nodes": 0,
    "graph_edges": 0,
    "context_bytes": 1501,
    "context_truncated": false,
    "temperature": 0.1,
    "top_p": 0.95,
    "seed": 42,
    "reasoning_setting": "LOW",
    "max_output_tokens": 4096,
    "call_count": 0,
    "attempt_count": 1,
    "input_tokens": 0,
    "output_tokens": 0,
    "reasoning_tokens": 0,
    "cached_tokens": 0,
    "detection_seconds": 0.0005158,
    "graph_seconds": 3.7e-06,
    "intent_seconds": 0.0,
    "generation_seconds": 0.0,
    "validation_seconds": 0.571913,
    "total_seconds": 0.5920968,
    "engine_outcome": "PLAUSIBLE_BUT_INCORRECT",
    "hidden_outcome": "FAIL",
    "failure_category": null,
    "independent_correct": false,
    "unnecessary_edit": false,
    "proper_abstention": false,
    "patch_hash": "73a3f8b7042f4436c734f8875f5f86ffec70343e550cfc812d09c6b2393d29a6",
    "environment_digest": "de41581c8c78222120edd0ff3d507bb593f8dad78803e284c3673f4b3eb5c0ac",
    "reviewer_agreement": null,
    "estimated_cost": 0.0,
    "currency": "USD",
    "pricing_date": "2026-10-15"
  }
}
```


### C:/Users/surji/ProjectSeven/benchmarks/runs/qualification_verified/B3_TASK-BANK-014_rep1.json

SHA-256: cf4112b9d9233e57a9d1007a3711ef724f7cd604de21541db88c6566b9609092

```json
{
  "record_kind": "fixture_replay",
  "run_id": "B3_TASK-BANK-014_rep1",
  "task_id": "TASK-BANK-014",
  "configuration": "B3",
  "repetition_index": 1,
  "timestamp_start": "2026-10-15T02:23:47.741613+00:00",
  "timestamp_end": "2026-10-15T02:23:48.432589+00:00",
  "requested_model": null,
  "resolved_model_version": null,
  "prompt_tokens": 0,
  "cached_tokens": 0,
  "completion_tokens": 0,
  "raw_prompt_hash": "907cdbe3af2de38c82bf740dd1ef601db03404ea647fd40cf41e80ff8d47a0f8",
  "generated_diff": "--- a/client.py\n+++ b/client.py\n@@ -1,2 +1,2 @@\n def build_request(data):\n-    return {'path': '/transfers', 'body': {'amount_cents': data['amount_cents']}, 'headers': {}}\n+    return {'path': '/transfers', 'body': {'source': data['source'], 'destination': data['source'], 'amount': {'value': data['amount_cents'], 'currency': data['currency']}}, 'headers': {'Idempotency-Key': data['idempotency_key']}}\n",
  "visible_test_exit_code": 0,
  "hidden_oracle_exit_code": 1,
  "invariants_preserved": {
    "exact_minor_units": true,
    "currency": true,
    "destination": false,
    "idempotency_key": true
  },
  "classification": "PLAUSIBLE_BUT_INCORRECT",
  "flags": {
    "enable_structural_graph": true,
    "enable_semantic_clustering": false,
    "enable_intent_inference": false,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": false,
    "enable_test_feedback": true
  },
  "detection": {
    "true_positive": 1,
    "false_positive": 0,
    "false_negative": 0
  },
  "phases_seconds": {
    "detection": 0.0003357,
    "graph": 5.3e-06,
    "intent": 0.0,
    "inference": 0.0,
    "visible_tests": 0.3319776,
    "hidden_tests": 0.3388862
  },
  "overhead_seconds": 0.019767800000000002,
  "execution_boundary": "trusted-fixtures",
  "docker_isolation_verified": false,
  "hidden_results_never_used_for_retry": true,
  "fixture_candidate_origin": "trusted_fixture_not_model_output",
  "record": {
    "protocol_version": "qualification-1",
    "dataset_version": "four-authored-fixtures-1",
    "task_id": "TASK-BANK-014",
    "family_id": "banking-qualification",
    "repository_id": "local-authored-fixture",
    "task_origin": "authored_fixture",
    "task_class": "repairable",
    "support_status": "pure_request_builder_only",
    "method": "B3",
    "model_requested": null,
    "model_returned": null,
    "provider": null,
    "api_version": null,
    "sdk_version": null,
    "timestamp_utc": "2026-10-15T02:23:47.741613+00:00",
    "repetition": 1,
    "randomization_block": 0,
    "tool_commit": "80e7bbe0c01b58fa6615098c1bc56c6534a830eb",
    "source_hash": "27be638eaa929291b3eee703b160a8e87963461dc42c3275e4826568d8d6af21",
    "accepted_contract_hash": "bcdd6643664991578b65bcc097277334e92b3167de6b219dc882179f88b381cb",
    "observed_contract_hash": "a39ee7bde4fd2eb17b3f6eb866a1333fc9234a1edee0149bc63441ff9f6c9954",
    "prompt_hash": "907cdbe3af2de38c82bf740dd1ef601db03404ea647fd40cf41e80ff8d47a0f8",
    "graph_hash": "7b561eb30bd9739b0b54cf830cabcb9180b26ba68a3a296fc8775a11d97ff9dc",
    "graph_nodes": 1,
    "graph_edges": 0,
    "context_bytes": 1646,
    "context_truncated": false,
    "temperature": 0.1,
    "top_p": 0.95,
    "seed": 42,
    "reasoning_setting": "LOW",
    "max_output_tokens": 4096,
    "call_count": 0,
    "attempt_count": 1,
    "input_tokens": 0,
    "output_tokens": 0,
    "reasoning_tokens": 0,
    "cached_tokens": 0,
    "detection_seconds": 0.0003357,
    "graph_seconds": 5.3e-06,
    "intent_seconds": 0.0,
    "generation_seconds": 0.0,
    "validation_seconds": 0.6708638,
    "total_seconds": 0.6909726,
    "engine_outcome": "PLAUSIBLE_BUT_INCORRECT",
    "hidden_outcome": "FAIL",
    "failure_category": null,
    "independent_correct": false,
    "unnecessary_edit": false,
    "proper_abstention": false,
    "patch_hash": "28d6b7191ee8c15255c3d22bd137361db79ca0fcc23ef945825390f3b152d945",
    "environment_digest": "de41581c8c78222120edd0ff3d507bb593f8dad78803e284c3673f4b3eb5c0ac",
    "reviewer_agreement": null,
    "estimated_cost": 0.0,
    "currency": "USD",
    "pricing_date": "2026-10-15"
  }
}
```


### C:/Users/surji/ProjectSeven/benchmarks/runs/qualification_verified/B4_TASK-BANK-014_rep1.json

SHA-256: a444154bf1ce544676436209da0f9c3e368c7ed8a40cd5886aba34288bbd822f

```json
{
  "record_kind": "fixture_replay",
  "run_id": "B4_TASK-BANK-014_rep1",
  "task_id": "TASK-BANK-014",
  "configuration": "B4",
  "repetition_index": 1,
  "timestamp_start": "2026-10-15T02:23:48.442375+00:00",
  "timestamp_end": "2026-10-15T02:23:48.450652+00:00",
  "requested_model": null,
  "resolved_model_version": null,
  "prompt_tokens": 0,
  "cached_tokens": 0,
  "completion_tokens": 0,
  "raw_prompt_hash": "58bf542c86d6a6666384b6a69db1fa1b9b30c1e9d5ff0642e500971175f18e97",
  "generated_diff": "",
  "visible_test_exit_code": null,
  "hidden_oracle_exit_code": null,
  "invariants_preserved": {},
  "classification": "ABSTAIN/REFUSED",
  "flags": {
    "enable_structural_graph": true,
    "enable_semantic_clustering": true,
    "enable_intent_inference": false,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": false,
    "enable_test_feedback": true
  },
  "detection": {
    "true_positive": 1,
    "false_positive": 0,
    "false_negative": 0
  },
  "phases_seconds": {
    "detection": 0.000479,
    "graph": 3.1e-06,
    "intent": 0.0,
    "inference": 0.0,
    "visible_tests": 0.0,
    "hidden_tests": 0.0
  },
  "overhead_seconds": 0.0077916,
  "execution_boundary": "trusted-fixtures",
  "docker_isolation_verified": false,
  "hidden_results_never_used_for_retry": true,
  "fixture_candidate_origin": "trusted_fixture_not_model_output",
  "record": {
    "protocol_version": "qualification-1",
    "dataset_version": "four-authored-fixtures-1",
    "task_id": "TASK-BANK-014",
    "family_id": "banking-qualification",
    "repository_id": "local-authored-fixture",
    "task_origin": "authored_fixture",
    "task_class": "repairable",
    "support_status": "pure_request_builder_only",
    "method": "B4",
    "model_requested": null,
    "model_returned": null,
    "provider": null,
    "api_version": null,
    "sdk_version": null,
    "timestamp_utc": "2026-10-15T02:23:48.442375+00:00",
    "repetition": 1,
    "randomization_block": 0,
    "tool_commit": "80e7bbe0c01b58fa6615098c1bc56c6534a830eb",
    "source_hash": "27be638eaa929291b3eee703b160a8e87963461dc42c3275e4826568d8d6af21",
    "accepted_contract_hash": "bcdd6643664991578b65bcc097277334e92b3167de6b219dc882179f88b381cb",
    "observed_contract_hash": "a39ee7bde4fd2eb17b3f6eb866a1333fc9234a1edee0149bc63441ff9f6c9954",
    "prompt_hash": "58bf542c86d6a6666384b6a69db1fa1b9b30c1e9d5ff0642e500971175f18e97",
    "graph_hash": "7b561eb30bd9739b0b54cf830cabcb9180b26ba68a3a296fc8775a11d97ff9dc",
    "graph_nodes": 1,
    "graph_edges": 0,
    "context_bytes": 1746,
    "context_truncated": false,
    "temperature": 0.1,
    "top_p": 0.95,
    "seed": 42,
    "reasoning_setting": "LOW",
    "max_output_tokens": 4096,
    "call_count": 0,
    "attempt_count": 1,
    "input_tokens": 0,
    "output_tokens": 0,
    "reasoning_tokens": 0,
    "cached_tokens": 0,
    "detection_seconds": 0.000479,
    "graph_seconds": 3.1e-06,
    "intent_seconds": 0.0,
    "generation_seconds": 0.0,
    "validation_seconds": 0.0,
    "total_seconds": 0.0082737,
    "engine_outcome": "ABSTAIN/REFUSED",
    "hidden_outcome": "NOT_EXECUTED",
    "failure_category": null,
    "independent_correct": false,
    "unnecessary_edit": false,
    "proper_abstention": false,
    "patch_hash": null,
    "environment_digest": "de41581c8c78222120edd0ff3d507bb593f8dad78803e284c3673f4b3eb5c0ac",
    "reviewer_agreement": null,
    "estimated_cost": 0.0,
    "currency": "USD",
    "pricing_date": "2026-10-15"
  }
}
```


### C:/Users/surji/ProjectSeven/benchmarks/runs/qualification_verified/B5_TASK-BANK-014_rep1.json

SHA-256: dd30e02a5983dff0da6d8a64c0b191f5ad6c99e269ddeb41c854a33f04cfec7d

```json
{
  "record_kind": "fixture_replay",
  "run_id": "B5_TASK-BANK-014_rep1",
  "task_id": "TASK-BANK-014",
  "configuration": "B5",
  "repetition_index": 1,
  "timestamp_start": "2026-10-15T02:23:48.461778+00:00",
  "timestamp_end": "2026-10-15T02:23:49.232201+00:00",
  "requested_model": null,
  "resolved_model_version": null,
  "prompt_tokens": 0,
  "cached_tokens": 0,
  "completion_tokens": 0,
  "raw_prompt_hash": "69ff36d283005d956949abee245cce6dce07908cbe35aec54a5c525268c2cccf",
  "generated_diff": "--- a/client.py\n+++ b/client.py\n@@ -1,2 +1,2 @@\n def build_request(data):\n-    return {'path': '/transfers', 'body': {'amount_cents': data['amount_cents']}, 'headers': {}}\n+    return {'path': '/transfers', 'body': {'source': data['source'], 'destination': data['destination'], 'amount': {'value': data['amount_cents'], 'currency': data['currency']}}, 'headers': {'Idempotency-Key': 'replacement-key'}}\n",
  "visible_test_exit_code": 0,
  "hidden_oracle_exit_code": 1,
  "invariants_preserved": {
    "exact_minor_units": true,
    "currency": true,
    "destination": true,
    "idempotency_key": false
  },
  "classification": "PLAUSIBLE_BUT_INCORRECT",
  "flags": {
    "enable_structural_graph": true,
    "enable_semantic_clustering": false,
    "enable_intent_inference": true,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": true,
    "enable_test_feedback": true
  },
  "detection": {
    "true_positive": 1,
    "false_positive": 0,
    "false_negative": 0
  },
  "phases_seconds": {
    "detection": 0.0004436,
    "graph": 2.8e-06,
    "intent": 0.0,
    "inference": 0.0,
    "visible_tests": 0.448653,
    "hidden_tests": 0.3038453
  },
  "overhead_seconds": 0.01747719999999997,
  "execution_boundary": "trusted-fixtures",
  "docker_isolation_verified": false,
  "hidden_results_never_used_for_retry": true,
  "fixture_candidate_origin": "trusted_fixture_not_model_output",
  "record": {
    "protocol_version": "qualification-1",
    "dataset_version": "four-authored-fixtures-1",
    "task_id": "TASK-BANK-014",
    "family_id": "banking-qualification",
    "repository_id": "local-authored-fixture",
    "task_origin": "authored_fixture",
    "task_class": "repairable",
    "support_status": "pure_request_builder_only",
    "method": "B5",
    "model_requested": null,
    "model_returned": null,
    "provider": null,
    "api_version": null,
    "sdk_version": null,
    "timestamp_utc": "2026-10-15T02:23:48.461778+00:00",
    "repetition": 1,
    "randomization_block": 0,
    "tool_commit": "80e7bbe0c01b58fa6615098c1bc56c6534a830eb",
    "source_hash": "27be638eaa929291b3eee703b160a8e87963461dc42c3275e4826568d8d6af21",
    "accepted_contract_hash": "bcdd6643664991578b65bcc097277334e92b3167de6b219dc882179f88b381cb",
    "observed_contract_hash": "a39ee7bde4fd2eb17b3f6eb866a1333fc9234a1edee0149bc63441ff9f6c9954",
    "prompt_hash": "69ff36d283005d956949abee245cce6dce07908cbe35aec54a5c525268c2cccf",
    "graph_hash": "7b561eb30bd9739b0b54cf830cabcb9180b26ba68a3a296fc8775a11d97ff9dc",
    "graph_nodes": 1,
    "graph_edges": 0,
    "context_bytes": 1789,
    "context_truncated": false,
    "temperature": 0.1,
    "top_p": 0.95,
    "seed": 42,
    "reasoning_setting": "LOW",
    "max_output_tokens": 4096,
    "call_count": 0,
    "attempt_count": 1,
    "input_tokens": 0,
    "output_tokens": 0,
    "reasoning_tokens": 0,
    "cached_tokens": 0,
    "detection_seconds": 0.0004436,
    "graph_seconds": 2.8e-06,
    "intent_seconds": 0.0,
    "generation_seconds": 0.0,
    "validation_seconds": 0.7524983000000001,
    "total_seconds": 0.7704219,
    "engine_outcome": "PLAUSIBLE_BUT_INCORRECT",
    "hidden_outcome": "FAIL",
    "failure_category": null,
    "independent_correct": false,
    "unnecessary_edit": false,
    "proper_abstention": false,
    "patch_hash": "5f9367029596e85f766e69de58d678dc4ac39717d7b20b3ec4d14f6df5499d5c",
    "environment_digest": "de41581c8c78222120edd0ff3d507bb593f8dad78803e284c3673f4b3eb5c0ac",
    "reviewer_agreement": null,
    "estimated_cost": 0.0,
    "currency": "USD",
    "pricing_date": "2026-10-15"
  }
}
```


### C:/Users/surji/ProjectSeven/benchmarks/runs/qualification_verified/B6_TASK-BANK-014_rep1.json

SHA-256: 649940854336351d8d7e4b42d88e2ca2fca526ba813919806b600468439ba68e

```json
{
  "record_kind": "fixture_replay",
  "run_id": "B6_TASK-BANK-014_rep1",
  "task_id": "TASK-BANK-014",
  "configuration": "B6",
  "repetition_index": 1,
  "timestamp_start": "2026-10-15T02:23:49.238683+00:00",
  "timestamp_end": "2026-10-15T02:23:50.168359+00:00",
  "requested_model": null,
  "resolved_model_version": null,
  "prompt_tokens": 0,
  "cached_tokens": 0,
  "completion_tokens": 0,
  "raw_prompt_hash": "43f65051d0c36e290989caa932929aad397c7f33670e2274c4770cc49bd18f4e",
  "generated_diff": "--- a/client.py\n+++ b/client.py\n@@ -1,2 +1,2 @@\n def build_request(data):\n-    return {'path': '/transfers', 'body': {'amount_cents': data['amount_cents']}, 'headers': {}}\n+    return {'path': '/transfers', 'body': {'source': data['source'], 'destination': data['destination'], 'amount': {'value': data['amount_cents'], 'currency': data['currency']}}, 'headers': {'Idempotency-Key': data['idempotency_key']}}\n",
  "visible_test_exit_code": 0,
  "hidden_oracle_exit_code": 0,
  "invariants_preserved": {
    "exact_minor_units": true,
    "currency": true,
    "destination": true,
    "idempotency_key": true
  },
  "classification": "PASS",
  "flags": {
    "enable_structural_graph": true,
    "enable_semantic_clustering": true,
    "enable_intent_inference": true,
    "enable_hidden_invariant_checks": true,
    "enable_generated_checks": true,
    "enable_test_feedback": true
  },
  "detection": {
    "true_positive": 1,
    "false_positive": 0,
    "false_negative": 0
  },
  "phases_seconds": {
    "detection": 0.0003216,
    "graph": 2e-06,
    "intent": 0.0,
    "inference": 0.0,
    "visible_tests": 0.5290633,
    "hidden_tests": 0.3823238
  },
  "overhead_seconds": 0.017960599999999993,
  "execution_boundary": "trusted-fixtures",
  "docker_isolation_verified": false,
  "hidden_results_never_used_for_retry": true,
  "fixture_candidate_origin": "trusted_fixture_not_model_output",
  "record": {
    "protocol_version": "qualification-1",
    "dataset_version": "four-authored-fixtures-1",
    "task_id": "TASK-BANK-014",
    "family_id": "banking-qualification",
    "repository_id": "local-authored-fixture",
    "task_origin": "authored_fixture",
    "task_class": "repairable",
    "support_status": "pure_request_builder_only",
    "method": "B6",
    "model_requested": null,
    "model_returned": null,
    "provider": null,
    "api_version": null,
    "sdk_version": null,
    "timestamp_utc": "2026-10-15T02:23:49.238683+00:00",
    "repetition": 1,
    "randomization_block": 0,
    "tool_commit": "80e7bbe0c01b58fa6615098c1bc56c6534a830eb",
    "source_hash": "27be638eaa929291b3eee703b160a8e87963461dc42c3275e4826568d8d6af21",
    "accepted_contract_hash": "bcdd6643664991578b65bcc097277334e92b3167de6b219dc882179f88b381cb",
    "observed_contract_hash": "a39ee7bde4fd2eb17b3f6eb866a1333fc9234a1edee0149bc63441ff9f6c9954",
    "prompt_hash": "43f65051d0c36e290989caa932929aad397c7f33670e2274c4770cc49bd18f4e",
    "graph_hash": "7b561eb30bd9739b0b54cf830cabcb9180b26ba68a3a296fc8775a11d97ff9dc",
    "graph_nodes": 1,
    "graph_edges": 0,
    "context_bytes": 1889,
    "context_truncated": false,
    "temperature": 0.1,
    "top_p": 0.95,
    "seed": 42,
    "reasoning_setting": "LOW",
    "max_output_tokens": 4096,
    "call_count": 0,
    "attempt_count": 1,
    "input_tokens": 0,
    "output_tokens": 0,
    "reasoning_tokens": 0,
    "cached_tokens": 0,
    "detection_seconds": 0.0003216,
    "graph_seconds": 2e-06,
    "intent_seconds": 0.0,
    "generation_seconds": 0.0,
    "validation_seconds": 0.9113871,
    "total_seconds": 0.9296713,
    "engine_outcome": "PASS",
    "hidden_outcome": "PASS",
    "failure_category": null,
    "independent_correct": true,
    "unnecessary_edit": false,
    "proper_abstention": false,
    "patch_hash": "fd24700991b8f756c87a4d0096dce07bad8cf6e6c70920d4c6166d7ff7655f41",
    "environment_digest": "de41581c8c78222120edd0ff3d507bb593f8dad78803e284c3673f4b3eb5c0ac",
    "reviewer_agreement": null,
    "estimated_cost": 0.0,
    "currency": "USD",
    "pricing_date": "2026-10-15"
  }
}
```


## 4. Exact model configuration and observed provenance


### C:/Users/surji/ProjectSeven/benchmarks/profiles/gemini.json

SHA-256: b972ed73c348a5da9014838a0346793f812d5f31375770b837fadcc7db217ad0

```json
{
  "provider": "google_cloud",
  "requested_model": "gemini-3.8-flash",
  "immutable_snapshot_verified": false,
  "resolved_model_version": null,
  "endpoint": "https://aiplatform.googleapis.com/v1/projects/gen-lang-client-0604700095/locations/global/publishers/google/models/gemini-3.8-flash:generateContent",
  "sdk": "google-genai",
  "sdk_version": "2.22.0",
  "location": "global",
  "temperature": 0.1,
  "top_p": 0.95,
  "seed": 42,
  "max_output_tokens": 4096,
  "reasoning_setting": "LOW",
  "max_transport_retries": 3,
  "transport_backoff_seconds": [
    1,
    2,
    4
  ],
  "retryable_http_status": [
    429,
    500,
    502,
    503,
    504
  ],
  "retired_example_model": "gemini-1.5-pro-002",
  "retired_example_status": "not_selected; retired 2025-09-24",
  "lifecycle_source": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions"
}
```


### C:/Users/surji/ProjectSeven/benchmarks/profiles/llama_cpp.json

SHA-256: 34e563602a21f6b03422c9be4851810877c48ec1980ec2ee65281f3f85507a8b

```json
{
  "provider": "llama.cpp",
  "repository": "bartowski/Meta-Llama-3.1-70B-Instruct-GGUF",
  "revision": "83fb6e83d0a8aada42d499259bc929d922e9a558",
  "file": "Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf",
  "quantization": "GGUF Q4_K_M, not AWQ",
  "published_weight_sha256": "f775c87029be95fb41df9e2882e6e938b73121c30ffc235ac6b6b880add49aa5",
  "published_size_bytes": 42520398400,
  "metadata_source": "https://huggingface.co/api/models/bartowski/Meta-Llama-3.1-70B-Instruct-GGUF?blobs=true",
  "local_weight_path": "C:/Users/surji/ProjectSeven/benchmarks/models/Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf",
  "local_weight_verified": false,
  "inference_engine_version": null,
  "endpoint": "http://127.0.0.1:8080/v1/chat/completions",
  "temperature": 0.1,
  "top_p": 0.95,
  "seed": 42,
  "max_output_tokens": 4096,
  "deployment_target": "2 x NVIDIA RTX A6000 48GB; planning target, not observed hardware",
  "power_assumption_watts": 600,
  "energy_price_usd_kwh": 0.2,
  "server_command": [
    "llama-server",
    "--model",
    "C:/Users/surji/ProjectSeven/benchmarks/models/Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf",
    "--host",
    "127.0.0.1",
    "--port",
    "8080",
    "--ctx-size",
    "16384",
    "--n-gpu-layers",
    "99",
    "--split-mode",
    "layer",
    "--tensor-split",
    "1,1",
    "--seed",
    "42",
    "--temp",
    "0.1",
    "--top-p",
    "0.95"
  ]
}
```


## 5. Measured fixture phase ledger and official-rate estimate configuration


### C:/Users/surji/ProjectSeven/benchmarks/runs/qualification_verified/resource_ledger.csv

SHA-256: 2f551907c3dd632c6bb5cb97cb0db972d9dce3097d673978e577674e484e0c1c

```csv
run_id,record_kind,configuration,task_id,detection_seconds,graph_seconds,intent_seconds,inference_seconds,visible_tests_seconds,hidden_tests_seconds,overhead_seconds,total_seconds,prompt_tokens,cached_tokens,completion_tokens,estimated_api_usd,measured_gpu_watts,measured_gpu_seconds,measured_energy_kwh,actual_invoice_usd
B1_TASK-BANK-014_rep1,fixture_replay,B1,TASK-BANK-014,0.0005821,1.3e-06,0.0,0.0,0.0,0.0,0.0336064,0.0341898,0,0,0,0.0,,,,
B2_TASK-BANK-014_rep1,fixture_replay,B2,TASK-BANK-014,0.0005158,3.7e-06,0.0,0.0,0.29178,0.280133,0.019664299999999968,0.5920968,0,0,0,0.0,,,,
B3_TASK-BANK-014_rep1,fixture_replay,B3,TASK-BANK-014,0.0003357,5.3e-06,0.0,0.0,0.3319776,0.3388862,0.019767800000000002,0.6909726,0,0,0,0.0,,,,
B4_TASK-BANK-014_rep1,fixture_replay,B4,TASK-BANK-014,0.000479,3.1e-06,0.0,0.0,0.0,0.0,0.0077916,0.0082737,0,0,0,0.0,,,,
B5_TASK-BANK-014_rep1,fixture_replay,B5,TASK-BANK-014,0.0004436,2.8e-06,0.0,0.0,0.448653,0.3038453,0.01747719999999997,0.7704219,0,0,0,0.0,,,,
B6_TASK-BANK-014_rep1,fixture_replay,B6,TASK-BANK-014,0.0003216,2e-06,0.0,0.0,0.5290633,0.3823238,0.017960599999999993,0.9296713,0,0,0,0.0,,,,
B1_TASK-BANK-015_rep1,fixture_replay,B1,TASK-BANK-015,0.0005494,1.2e-06,0.0,0.0,0.0,0.0,0.0185168,0.0190674,0,0,0,0.0,,,,
B2_TASK-BANK-015_rep1,fixture_replay,B2,TASK-BANK-015,0.0004794,2.7e-06,0.0,0.0,0.5191682,0.2945734,0.019490499999999966,0.8337142,0,0,0,0.0,,,,
B3_TASK-BANK-015_rep1,fixture_replay,B3,TASK-BANK-015,0.0004893,4.05e-05,0.0,0.0,0.3256376,0.3310924,0.021398499999999987,0.6786583,0,0,0,0.0,,,,
B4_TASK-BANK-015_rep1,fixture_replay,B4,TASK-BANK-015,0.0004785,2.8e-06,0.0,0.0,0.0,0.0,0.009332499999999999,0.0098138,0,0,0,0.0,,,,
B5_TASK-BANK-015_rep1,fixture_replay,B5,TASK-BANK-015,0.0004861,2.9e-06,0.0,0.0,0.336977,0.4487092,0.024732199999999982,0.8109074,0,0,0,0.0,,,,
B6_TASK-BANK-015_rep1,fixture_replay,B6,TASK-BANK-015,0.0004857,3e-06,0.0,0.0,0.3484648,0.2874241,0.022403399999999962,0.658781,0,0,0,0.0,,,,
B1_TASK-SHIP-029_rep1,fixture_replay,B1,TASK-SHIP-029,0.0007355,1.1e-06,0.0,0.0,0.0,0.0,0.0195432,0.0202798,0,0,0,0.0,,,,
B2_TASK-SHIP-029_rep1,fixture_replay,B2,TASK-SHIP-029,0.0004816,2.3e-06,0.0,0.0,0.2550435,0.2616634,0.02265790000000001,0.5398487,0,0,0,0.0,,,,
B3_TASK-SHIP-029_rep1,fixture_replay,B3,TASK-SHIP-029,0.0005591,3.9e-06,0.0,0.0,0.3419947,0.2677107,0.017041399999999984,0.6273098,0,0,0,0.0,,,,
B4_TASK-SHIP-029_rep1,fixture_replay,B4,TASK-SHIP-029,0.0003264,2.4e-06,0.0,0.0,0.0,0.0,0.0072836,0.0076124,0,0,0,0.0,,,,
B5_TASK-SHIP-029_rep1,fixture_replay,B5,TASK-SHIP-029,0.0004862,3.1e-06,0.0,0.0,0.2951505,0.2734254,0.021426500000000015,0.5904917,0,0,0,0.0,,,,
B6_TASK-SHIP-029_rep1,fixture_replay,B6,TASK-SHIP-029,0.0011911,4.1e-06,0.0,0.0,0.3335181,0.4549798,0.021065700000000076,0.8107588,0,0,0,0.0,,,,
B1_TASK-PAY-008_rep1,fixture_replay,B1,TASK-PAY-008,0.0004958,9e-07,0.0,0.0,0.0,0.0,0.0182462,0.0187429,0,0,0,0.0,,,,
B2_TASK-PAY-008_rep1,fixture_replay,B2,TASK-PAY-008,0.0004736,2e-06,0.0,0.0,0.26723,0.2600006,0.01779059999999999,0.5454968,0,0,0,0.0,,,,
B3_TASK-PAY-008_rep1,fixture_replay,B3,TASK-PAY-008,0.0004995,3.3e-06,0.0,0.0,0.2988765,0.4066804,0.022130800000000006,0.7281905,0,0,0,0.0,,,,
B4_TASK-PAY-008_rep1,fixture_replay,B4,TASK-PAY-008,0.0005068,2.3e-06,0.0,0.0,0.0,0.0,0.0074640999999999996,0.0079732,0,0,0,0.0,,,,
B5_TASK-PAY-008_rep1,fixture_replay,B5,TASK-PAY-008,0.0005104,3.8e-06,0.0,0.0,0.2715433,0.2582881,0.020785300000000007,0.5511309,0,0,0,0.0,,,,
B6_TASK-PAY-008_rep1,fixture_replay,B6,TASK-PAY-008,0.0006566,3.8e-06,0.0,0.0,0.2724008,0.3465663,0.022056500000000034,0.641684,0,0,0,0.0,,,,
```


### C:/Users/surji/ProjectSeven/benchmarks/profiles/rate_card.json

SHA-256: 992d082553afd25ff128157d66066099c64698bcc101862ec6d7dba1e3b39de6

```json
{
  "model": "gemini-3.8-flash",
  "region": "global",
  "currency": "USD",
  "observed_date": "2026-10-15",
  "effective_until": "2026-12-31",
  "input_per_million": 0.75,
  "cached_input_per_million": 0.075,
  "output_including_reasoning_per_million": 3.75,
  "source": "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing",
  "status": "public introductory list rates; estimates only, not invoices",
  "non_200_policy": "Google lists no input/output charge for non-200 responses; unknown transport outcomes require billing reconciliation"
}
```


## 6. Complete statistical analysis pipeline and its actual output


### C:/Users/surji/ProjectSeven/benchmarks/harness/aggregate_metrics.py

SHA-256: 3f6c91f0f73a7099d3793975439aa084120d2f0686ff6fa5e4fac1661a094c23

```python
"""Aggregate actual trace files. Fixture and live evidence cannot be pooled."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT=Path(__file__).resolve().parents[2]

def wilson(successes,total,alpha=.05):
    if not total:return None,None
    z=norm.ppf(1-alpha/2);p=successes/total;den=1+z*z/total
    middle=(p+z*z/(2*total))/den
    half=z*np.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return float(middle-half),float(middle+half)

def bootstrap_cases(frame,column,seed=42,draws=2000):
    values=frame.groupby('task_id')[column].mean().to_numpy(dtype=float)
    if not len(values):return None,None
    samples=np.random.default_rng(seed).choice(values,(draws,len(values)),replace=True).mean(axis=1)
    return [float(x) for x in np.quantile(samples,[.025,.975])]

def cliffs_delta(left,right):
    if not len(left) or not len(right):return None
    differences=np.asarray(left)[:,None]-np.asarray(right)[None,:]
    return float((np.sum(differences>0)-np.sum(differences<0))/differences.size)

def load(directory):
    columns=(ROOT/'docs/academic-run-record-template.csv').read_text(encoding='utf-8').strip().split(',')
    rows=[];seen=set()
    for path in sorted(directory.glob('B*_TASK-*_rep*.json')):
        trace=json.loads(path.read_text(encoding='utf-8'))
        if trace['run_id'] in seen:raise ValueError('Duplicate run ID')
        seen.add(trace['run_id'])
        if set(trace['record'])!=set(columns):raise ValueError(f'56-column schema mismatch: {path.name}')
        if trace['configuration'] != trace['record']['method']:raise ValueError('Configuration alias mismatch')
        if abs(sum(trace['phases_seconds'].values())+trace['overhead_seconds']-trace['record']['total_seconds'])>1e-7:
            raise ValueError('Phase ledger does not reconcile')
        rows.append({**trace['record'],'run_id':trace['run_id'],'record_kind':trace['record_kind'],
                     'classification':trace['classification'],'requested_model':trace['requested_model'],
                     'public_success':int(trace['visible_test_exit_code']==0),'hidden_success':int(trace['hidden_oracle_exit_code']==0),
                     'delivered_success':int(trace['classification']=='PASS'),
                     'tp':trace['detection']['true_positive'],'fp':trace['detection']['false_positive'],'fn':trace['detection']['false_negative']})
    if not rows:raise ValueError('No raw traces found')
    frame=pd.DataFrame(rows)
    if frame['record_kind'].nunique()!=1:raise ValueError('Fixture replay and live model records must be analysed separately')
    return frame

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();frame=load(args.runs)
    ledger=pd.read_csv(args.runs/'resource_ledger.csv')
    if set(ledger.run_id)!=set(frame.run_id):raise ValueError('Ledger and trace run inventories differ')
    joined=frame.merge(ledger[['run_id','total_seconds','prompt_tokens','completion_tokens']],on='run_id',validate='one_to_one',suffixes=('','_ledger'))
    if not np.allclose(joined.total_seconds,joined.total_seconds_ledger,atol=1e-9):raise ValueError('Ledger time mismatch')
    if not np.array_equal(joined.input_tokens,joined.prompt_tokens):raise ValueError('Ledger input-token mismatch')
    if not np.array_equal(joined.output_tokens+joined.reasoning_tokens,joined.completion_tokens):raise ValueError('Ledger completion-token mismatch')
    args.output.mkdir(parents=True,exist_ok=False)
    frame.to_csv(args.output/'parsed_records.csv',index=False)
    summaries=[]
    for (kind,provider,model,method),group in frame.groupby(['record_kind','provider','requested_model','method'],dropna=False):
        row={'record_kind':kind,'provider':None if pd.isna(provider) else provider,'requested_model':None if pd.isna(model) else model,
             'configuration':method,'task_runs':len(group),'independent_tasks':group.task_id.nunique()}
        for metric,num,den in [('precision',int(group.tp.sum()),int((group.tp+group.fp).sum())),('recall',int(group.tp.sum()),int((group.tp+group.fn).sum()))]:
            lo,hi=wilson(num,den)
            row.update({metric:num/den if den else None,metric+'_numerator':num,metric+'_denominator':den,
                        metric+'_wilson_lo':lo,metric+'_wilson_hi':hi})
        for metric in ['public_success','hidden_success','delivered_success']:
            successes=int(group[metric].sum());lo,hi=wilson(successes,len(group));blo,bhi=bootstrap_cases(group,metric)
            row.update({metric:successes/len(group),metric+'_successes':successes,metric+'_wilson_lo':lo,metric+'_wilson_hi':hi,
                        metric+'_case_bootstrap_lo':blo,metric+'_case_bootstrap_hi':bhi})
        row.update(mean_wall_seconds=float(group.total_seconds.mean()),sd_wall_seconds=float(group.total_seconds.std(ddof=1)) if len(group)>1 else None,
                   total_estimated_api_usd=float(group.estimated_cost.sum()) if group.estimated_cost.notna().all() else None,
                   plausible_incorrect=int((group.classification=='PLAUSIBLE_BUT_INCORRECT').sum()))
        summaries.append(row)
    effects=[]
    for (provider,model),block in frame.groupby(['provider','requested_model'],dropna=False):
        a=block[block.method=='B1'].groupby('task_id').delivered_success.mean()
        b=block[block.method=='B6'].groupby('task_id').delivered_success.mean()
        common=a.index.intersection(b.index)
        if len(common):
            delta=(b[common]-a[common]).to_numpy()
            draws=np.random.default_rng(42).choice(delta,(2000,len(delta)),replace=True).mean(axis=1)
            effects.append({'provider':None if pd.isna(provider) else provider,'requested_model':None if pd.isna(model) else model,
                'contrast':'B6-B1','paired_tasks':len(common),'mean_paired_difference':float(delta.mean()),
                'paired_case_bootstrap_95':[float(x) for x in np.quantile(draws,[.025,.975])],
                'cliffs_delta_B6_vs_B1':cliffs_delta(b[common].to_numpy(),a[common].to_numpy()),
                'cliffs_delta_note':'Marginal descriptive ordinal effect; paired difference and case bootstrap are the matched-task analysis.'})
    report={'record_kind':str(frame.record_kind.iloc[0]),'schema_columns':56,'summaries':summaries,'effects':effects,
        'interpretation':'Qualification traces exercise instrumentation only; no model-quality inference.' if frame.record_kind.iloc[0]=='fixture_replay' else 'Descriptive output; finalize preregistered family-cluster analysis before confirmatory claims.',
        'ci_caveat':'Wilson intervals treat counted units as independent and are descriptive only with repeated/correlated calls. Case bootstrap preserves repetitions; multi-project studies also need family-level clustering.'}
    (args.output/'metrics.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
    pd.DataFrame(summaries).to_csv(args.output/'aggregate_metrics.csv',index=False)
    print(json.dumps({'raw_traces':len(frame),'output':str(args.output),'record_kind':report['record_kind']}))

if __name__=='__main__':main()
```


### C:/Users/surji/ProjectSeven/benchmarks/analysis/qualification_verified/aggregate_metrics.csv

SHA-256: 5324df2d2bb47aae0d80db1d1e4b75404196157b0fcc43b034fe3f76116ace15

```csv
record_kind,provider,requested_model,configuration,task_runs,independent_tasks,precision,precision_numerator,precision_denominator,precision_wilson_lo,precision_wilson_hi,recall,recall_numerator,recall_denominator,recall_wilson_lo,recall_wilson_hi,public_success,public_success_successes,public_success_wilson_lo,public_success_wilson_hi,public_success_case_bootstrap_lo,public_success_case_bootstrap_hi,hidden_success,hidden_success_successes,hidden_success_wilson_lo,hidden_success_wilson_hi,hidden_success_case_bootstrap_lo,hidden_success_case_bootstrap_hi,delivered_success,delivered_success_successes,delivered_success_wilson_lo,delivered_success_wilson_hi,delivered_success_case_bootstrap_lo,delivered_success_case_bootstrap_hi,mean_wall_seconds,sd_wall_seconds,total_estimated_api_usd,plausible_incorrect
fixture_replay,,,B1,4,4,1.0,4,4,0.5101091635454027,1.0,1.0,4,4,0.5101091635454027,1.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.023069975000000003,0.007442664604550801,0.0,0
fixture_replay,,,B2,4,4,1.0,4,4,0.5101091635454027,1.0,1.0,4,4,0.5101091635454027,1.0,1.0,4,0.5101091635454027,1.0,1.0,1.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.627789125,0.1392654822999912,0.0,4
fixture_replay,,,B3,4,4,1.0,4,4,0.5101091635454027,1.0,1.0,4,4,0.5101091635454027,1.0,1.0,4,0.5101091635454027,1.0,1.0,1.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.6812828,0.041690115825296824,0.0,4
fixture_replay,,,B4,4,4,1.0,4,4,0.5101091635454027,1.0,1.0,4,4,0.5101091635454027,1.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.008418275,0.0009688340462466553,0.0,0
fixture_replay,,,B5,4,4,1.0,4,4,0.5101091635454027,1.0,1.0,4,4,0.5101091635454027,1.0,1.0,4,0.5101091635454027,1.0,1.0,1.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.0,0,0.0,0.4898908364545973,0.0,0.0,0.6807379749999999,0.12900861683064366,0.0,4
fixture_replay,,,B6,4,4,1.0,4,4,0.5101091635454027,1.0,1.0,4,4,0.5101091635454027,1.0,1.0,4,0.5101091635454027,1.0,1.0,1.0,1.0,4,0.5101091635454027,1.0,1.0,1.0,1.0,4,0.5101091635454027,1.0,1.0,1.0,0.7602237749999999,0.1361476739146719,0.0,0
```


### C:/Users/surji/ProjectSeven/benchmarks/analysis/qualification_verified/metrics.json

SHA-256: a4aebdd7b20b558b8a3a98b3d7ce93cdecd21ef814deed34931c7d115acad1b2

```json
{
  "record_kind": "fixture_replay",
  "schema_columns": 56,
  "summaries": [
    {
      "record_kind": "fixture_replay",
      "provider": null,
      "requested_model": null,
      "configuration": "B1",
      "task_runs": 4,
      "independent_tasks": 4,
      "precision": 1.0,
      "precision_numerator": 4,
      "precision_denominator": 4,
      "precision_wilson_lo": 0.5101091635454027,
      "precision_wilson_hi": 1.0,
      "recall": 1.0,
      "recall_numerator": 4,
      "recall_denominator": 4,
      "recall_wilson_lo": 0.5101091635454027,
      "recall_wilson_hi": 1.0,
      "public_success": 0.0,
      "public_success_successes": 0,
      "public_success_wilson_lo": 0.0,
      "public_success_wilson_hi": 0.4898908364545973,
      "public_success_case_bootstrap_lo": 0.0,
      "public_success_case_bootstrap_hi": 0.0,
      "hidden_success": 0.0,
      "hidden_success_successes": 0,
      "hidden_success_wilson_lo": 0.0,
      "hidden_success_wilson_hi": 0.4898908364545973,
      "hidden_success_case_bootstrap_lo": 0.0,
      "hidden_success_case_bootstrap_hi": 0.0,
      "delivered_success": 0.0,
      "delivered_success_successes": 0,
      "delivered_success_wilson_lo": 0.0,
      "delivered_success_wilson_hi": 0.4898908364545973,
      "delivered_success_case_bootstrap_lo": 0.0,
      "delivered_success_case_bootstrap_hi": 0.0,
      "mean_wall_seconds": 0.023069975000000003,
      "sd_wall_seconds": 0.007442664604550801,
      "total_estimated_api_usd": 0.0,
      "plausible_incorrect": 0
    },
    {
      "record_kind": "fixture_replay",
      "provider": null,
      "requested_model": null,
      "configuration": "B2",
      "task_runs": 4,
      "independent_tasks": 4,
      "precision": 1.0,
      "precision_numerator": 4,
      "precision_denominator": 4,
      "precision_wilson_lo": 0.5101091635454027,
      "precision_wilson_hi": 1.0,
      "recall": 1.0,
      "recall_numerator": 4,
      "recall_denominator": 4,
      "recall_wilson_lo": 0.5101091635454027,
      "recall_wilson_hi": 1.0,
      "public_success": 1.0,
      "public_success_successes": 4,
      "public_success_wilson_lo": 0.5101091635454027,
      "public_success_wilson_hi": 1.0,
      "public_success_case_bootstrap_lo": 1.0,
      "public_success_case_bootstrap_hi": 1.0,
      "hidden_success": 0.0,
      "hidden_success_successes": 0,
      "hidden_success_wilson_lo": 0.0,
      "hidden_success_wilson_hi": 0.4898908364545973,
      "hidden_success_case_bootstrap_lo": 0.0,
      "hidden_success_case_bootstrap_hi": 0.0,
      "delivered_success": 0.0,
      "delivered_success_successes": 0,
      "delivered_success_wilson_lo": 0.0,
      "delivered_success_wilson_hi": 0.4898908364545973,
      "delivered_success_case_bootstrap_lo": 0.0,
      "delivered_success_case_bootstrap_hi": 0.0,
      "mean_wall_seconds": 0.627789125,
      "sd_wall_seconds": 0.1392654822999912,
      "total_estimated_api_usd": 0.0,
      "plausible_incorrect": 4
    },
    {
      "record_kind": "fixture_replay",
      "provider": null,
      "requested_model": null,
      "configuration": "B3",
      "task_runs": 4,
      "independent_tasks": 4,
      "precision": 1.0,
      "precision_numerator": 4,
      "precision_denominator": 4,
      "precision_wilson_lo": 0.5101091635454027,
      "precision_wilson_hi": 1.0,
      "recall": 1.0,
      "recall_numerator": 4,
      "recall_denominator": 4,
      "recall_wilson_lo": 0.5101091635454027,
      "recall_wilson_hi": 1.0,
      "public_success": 1.0,
      "public_success_successes": 4,
      "public_success_wilson_lo": 0.5101091635454027,
      "public_success_wilson_hi": 1.0,
      "public_success_case_bootstrap_lo": 1.0,
      "public_success_case_bootstrap_hi": 1.0,
      "hidden_success": 0.0,
      "hidden_success_successes": 0,
      "hidden_success_wilson_lo": 0.0,
      "hidden_success_wilson_hi": 0.4898908364545973,
      "hidden_success_case_bootstrap_lo": 0.0,
      "hidden_success_case_bootstrap_hi": 0.0,
      "delivered_success": 0.0,
      "delivered_success_successes": 0,
      "delivered_success_wilson_lo": 0.0,
      "delivered_success_wilson_hi": 0.4898908364545973,
      "delivered_success_case_bootstrap_lo": 0.0,
      "delivered_success_case_bootstrap_hi": 0.0,
      "mean_wall_seconds": 0.6812828,
      "sd_wall_seconds": 0.041690115825296824,
      "total_estimated_api_usd": 0.0,
      "plausible_incorrect": 4
    },
    {
      "record_kind": "fixture_replay",
      "provider": null,
      "requested_model": null,
      "configuration": "B4",
      "task_runs": 4,
      "independent_tasks": 4,
      "precision": 1.0,
      "precision_numerator": 4,
      "precision_denominator": 4,
      "precision_wilson_lo": 0.5101091635454027,
      "precision_wilson_hi": 1.0,
      "recall": 1.0,
      "recall_numerator": 4,
      "recall_denominator": 4,
      "recall_wilson_lo": 0.5101091635454027,
      "recall_wilson_hi": 1.0,
      "public_success": 0.0,
      "public_success_successes": 0,
      "public_success_wilson_lo": 0.0,
      "public_success_wilson_hi": 0.4898908364545973,
      "public_success_case_bootstrap_lo": 0.0,
      "public_success_case_bootstrap_hi": 0.0,
      "hidden_success": 0.0,
      "hidden_success_successes": 0,
      "hidden_success_wilson_lo": 0.0,
      "hidden_success_wilson_hi": 0.4898908364545973,
      "hidden_success_case_bootstrap_lo": 0.0,
      "hidden_success_case_bootstrap_hi": 0.0,
      "delivered_success": 0.0,
      "delivered_success_successes": 0,
      "delivered_success_wilson_lo": 0.0,
      "delivered_success_wilson_hi": 0.4898908364545973,
      "delivered_success_case_bootstrap_lo": 0.0,
      "delivered_success_case_bootstrap_hi": 0.0,
      "mean_wall_seconds": 0.008418275,
      "sd_wall_seconds": 0.0009688340462466553,
      "total_estimated_api_usd": 0.0,
      "plausible_incorrect": 0
    },
    {
      "record_kind": "fixture_replay",
      "provider": null,
      "requested_model": null,
      "configuration": "B5",
      "task_runs": 4,
      "independent_tasks": 4,
      "precision": 1.0,
      "precision_numerator": 4,
      "precision_denominator": 4,
      "precision_wilson_lo": 0.5101091635454027,
      "precision_wilson_hi": 1.0,
      "recall": 1.0,
      "recall_numerator": 4,
      "recall_denominator": 4,
      "recall_wilson_lo": 0.5101091635454027,
      "recall_wilson_hi": 1.0,
      "public_success": 1.0,
      "public_success_successes": 4,
      "public_success_wilson_lo": 0.5101091635454027,
      "public_success_wilson_hi": 1.0,
      "public_success_case_bootstrap_lo": 1.0,
      "public_success_case_bootstrap_hi": 1.0,
      "hidden_success": 0.0,
      "hidden_success_successes": 0,
      "hidden_success_wilson_lo": 0.0,
      "hidden_success_wilson_hi": 0.4898908364545973,
      "hidden_success_case_bootstrap_lo": 0.0,
      "hidden_success_case_bootstrap_hi": 0.0,
      "delivered_success": 0.0,
      "delivered_success_successes": 0,
      "delivered_success_wilson_lo": 0.0,
      "delivered_success_wilson_hi": 0.4898908364545973,
      "delivered_success_case_bootstrap_lo": 0.0,
      "delivered_success_case_bootstrap_hi": 0.0,
      "mean_wall_seconds": 0.6807379749999999,
      "sd_wall_seconds": 0.12900861683064366,
      "total_estimated_api_usd": 0.0,
      "plausible_incorrect": 4
    },
    {
      "record_kind": "fixture_replay",
      "provider": null,
      "requested_model": null,
      "configuration": "B6",
      "task_runs": 4,
      "independent_tasks": 4,
      "precision": 1.0,
      "precision_numerator": 4,
      "precision_denominator": 4,
      "precision_wilson_lo": 0.5101091635454027,
      "precision_wilson_hi": 1.0,
      "recall": 1.0,
      "recall_numerator": 4,
      "recall_denominator": 4,
      "recall_wilson_lo": 0.5101091635454027,
      "recall_wilson_hi": 1.0,
      "public_success": 1.0,
      "public_success_successes": 4,
      "public_success_wilson_lo": 0.5101091635454027,
      "public_success_wilson_hi": 1.0,
      "public_success_case_bootstrap_lo": 1.0,
      "public_success_case_bootstrap_hi": 1.0,
      "hidden_success": 1.0,
      "hidden_success_successes": 4,
      "hidden_success_wilson_lo": 0.5101091635454027,
      "hidden_success_wilson_hi": 1.0,
      "hidden_success_case_bootstrap_lo": 1.0,
      "hidden_success_case_bootstrap_hi": 1.0,
      "delivered_success": 1.0,
      "delivered_success_successes": 4,
      "delivered_success_wilson_lo": 0.5101091635454027,
      "delivered_success_wilson_hi": 1.0,
      "delivered_success_case_bootstrap_lo": 1.0,
      "delivered_success_case_bootstrap_hi": 1.0,
      "mean_wall_seconds": 0.7602237749999999,
      "sd_wall_seconds": 0.1361476739146719,
      "total_estimated_api_usd": 0.0,
      "plausible_incorrect": 0
    }
  ],
  "effects": [
    {
      "provider": null,
      "requested_model": null,
      "contrast": "B6-B1",
      "paired_tasks": 4,
      "mean_paired_difference": 1.0,
      "paired_case_bootstrap_95": [
        1.0,
        1.0
      ],
      "cliffs_delta_B6_vs_B1": 1.0,
      "cliffs_delta_note": "Marginal descriptive ordinal effect; paired difference and case bootstrap are the matched-task analysis."
    }
  ],
  "interpretation": "Qualification traces exercise instrumentation only; no model-quality inference.",
  "ci_caveat": "Wilson intervals treat counted units as independent and are descriptive only with repeated/correlated calls. Case bootstrap preserves repetitions; multi-project studies also need family-level clustering."
}
```
