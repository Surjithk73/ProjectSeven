"""Package actual diagnostic evidence and protocol with verifiable byte lineage."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
B=ROOT/'benchmarks'

def hashes(raw):
    return {'md5':hashlib.md5(raw,usedforsecurity=False).hexdigest(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs',type=Path,nargs='+',required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    args.runs=[path.resolve() for path in args.runs]
    args.output=args.output.resolve()
    if args.output.exists():raise ValueError('Preserve previous archives: choose a new output filename')
    traces=[]
    for directory in args.runs:
        for path in sorted(directory.glob('B*_TASK-*_rep*.json')):
            trace=json.loads(path.read_text());traces.append(trace)
    if not traces:raise ValueError('No observed trace records')
    successful_calls=[]
    for directory in args.runs:
        for path in directory.glob('evidence/*/model_calls.json'):
            successful_calls += [c for c in json.loads(path.read_text()) if c.get('http_status')==200]
    metrics={'evidence_type':'live_inference_diagnostic_not_evaluated_repairs',
        'run_directories':[str(p.resolve()) for p in args.runs],'traces':len(traces),
        'successful_provider_responses':len(successful_calls),
        'recorded_prompt_tokens':sum(c.get('prompt_tokens',0) for c in successful_calls),
        'recorded_cached_tokens':sum(c.get('cached_tokens',0) for c in successful_calls),
        'recorded_completion_and_reasoning_tokens':sum(c.get('output_tokens',0)+c.get('reasoning_tokens',0) for c in successful_calls),
        'models_returned':sorted({c['resolved_model_version'] for c in successful_calls if c.get('resolved_model_version')}),
        'evaluated_hidden_runs':sum(t['hidden_oracle_exit_code'] is not None for t in traces),
        'independent_repair_success_rate':None,'synthetic_manuscript_results_validated':False,
        'snapshot_immutable_verified':False,'per_configuration':{}}
    for name in ['B1','B2','B3','B4','B5','B6']:
        group=[t for t in traces if t['configuration']==name]
        metrics['per_configuration'][name]={'attempted_runs':len(group),'candidate_diffs_recorded':sum(bool(t['generated_diff']) for t in group),
            'infrastructure_failures':sum(t['classification']=='INFRASTRUCTURE_ERROR' for t in group),
            'recorded_input_tokens':sum(t['prompt_tokens'] for t in group),
            'recorded_completion_tokens':sum(t['completion_tokens'] for t in group),
            'public_success_rate':None,'hidden_success_rate':None}
    analysis=B/'analysis/live_diagnostic_review'
    analysis.mkdir(parents=True,exist_ok=True)
    metric_path=analysis/'metrics.json'
    metric_path.write_text(json.dumps(metrics,indent=2)+'\n')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
    anchor={'head':head,'working_tree_clean':not bool(status),'head_is_not_artifact_revision':bool(status),
        'captured_at':datetime.now(timezone.utc).isoformat(),
        'artifact_commit_created':False,'content_identity':'See review_payload_manifest.json; existing HEAD alone does not identify these working files'}
    (B/'provenance/review_repository.json').write_text(json.dumps(anchor,indent=2)+'\n')
    roots=[B/'harness',B/'runners',B/'adapters',B/'docker',B/'profiles',B/'tests',B/'tasks',B/'evaluator_private',B/'fixture_candidates',B/'provenance',analysis,*args.runs]
    roots += [B/'runs/tooling_qualification_20261015',B/'analysis/tooling_qualification_20261015',B/'analysis/gemini_bank014_observed_20261015_sdk']
    files={path for root in roots for path in root.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
    files.update(B.glob('requirements-*.txt'))
    files.update([B/'README.md',B/'REVIEW_STATUS.md',B/'configurations.json',B/'tasks_manifest.json',B/'tasks_manifest.schema.json',
        ROOT/'docs/academic-evaluation-report.md',ROOT/'docs/academic-run-record-template.csv',ROOT/'config.py',ROOT/'requirements.txt'])
    files.update((ROOT/'apishield').glob('*.py'))
    previous_archive=ROOT/'reports/artifacts/APIShield-qualification-artifact-2026-10-15.zip'
    if previous_archive.is_file():files.add(previous_archive)
    payload={path.relative_to(ROOT).as_posix():hashes(path.read_bytes()) for path in sorted(files)}
    internal=B/'review_payload_manifest.json'
    internal.write_text(json.dumps({'files':payload,'excludes_self':True,'metrics_are_diagnostic_not_manuscript_effect_estimates':True},indent=2)+'\n')
    files.add(internal)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):archive.write(path,path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(args.output) as archive:
        assert archive.testzip() is None
        for path,expected in payload.items():assert hashes(archive.read(path))==expected,path
    manifest={'archive':{**hashes(args.output.read_bytes()),'path':args.output.resolve().as_posix()},
        'files':{name:payload[name] for name in ['docs/academic-evaluation-report.md',metric_path.relative_to(ROOT).as_posix()]},
        'payload_manifest':hashes(internal.read_bytes()),'git':anchor,
        'meaning':'Byte consistency verified; no artifact badge, clean commit, immutable model snapshot or hidden correctness claimed'}
    target=args.output.with_suffix('.manifest.json')
    target.write_text(json.dumps(manifest,indent=2)+'\n')
    for algorithm in ['md5','sha256']:
        args.output.with_suffix(args.output.suffix+'.'+algorithm).write_text(manifest['archive'][algorithm]+'  '+args.output.name+'\n')
    print(json.dumps({'archive':str(args.output),'manifest':str(target),'files':len(files),'metrics':metrics},indent=2))

if __name__=='__main__':main()
