"""Portable single-case qualification; generated candidates require Docker."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main():
    from benchmarks.harness.run_ablation import run_one,valid_image
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--task',default='TASK-BANK-014')
    p.add_argument('--config',choices=[f'B{i}' for i in range(1,7)],default='B6')
    p.add_argument('--mode',choices=['fixture','live'],default='fixture')
    p.add_argument('--image')
    p.add_argument('--execute-live',action='store_true')
    p.add_argument('--allow-unpinned-provider',action='store_true')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.mode=='live':
        if not args.execute_live or not valid_image(args.image):p.error('Live mode requires explicit execution and a resolved Docker image digest')
        if not args.allow_unpinned_provider:p.error('Current provider is not verified immutable; diagnostic live mode requires explicit override')
        subprocess.run(['docker','info'],capture_output=True,check=True,timeout=15)
        subprocess.run(['docker','image','inspect',args.image],capture_output=True,check=True,timeout=15)
    tasks=json.loads((ROOT/'benchmarks/tasks_manifest.json').read_text())['tasks']
    task=next((t for t in tasks if t['task_id']==args.task),None)
    if task is None:p.error('Only the four retained executable qualification tasks are available')
    for key,value in task.items():
        if isinstance(value,str) and value.startswith('C:/Users/surji/ProjectSeven/'):
            task[key]=str(ROOT/value.removeprefix('C:/Users/surji/ProjectSeven/'))
    flags=json.loads((ROOT/'benchmarks/configurations.json').read_text())[args.config]
    args.output=args.output.resolve();args.output.mkdir(parents=True,exist_ok=False)
    runtime=SimpleNamespace(repetition=1,mode=args.mode,provider='google-cloud',
        boundary='docker' if args.mode=='live' else 'trusted-fixtures',image=args.image,generation_only=False)
    trace=run_one(task,args.config,flags,runtime,args.output)
    print(json.dumps({'run_id':trace['run_id'],'evidence_kind':trace['record_kind'],
        'classification':trace['classification'],'independent_correct':trace['record']['independent_correct']},indent=2))
    if trace['classification']=='INFRASTRUCTURE_ERROR':raise SystemExit(1)

if __name__=='__main__':main()
