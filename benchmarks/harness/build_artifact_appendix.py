"""Assemble exact artifact contents and an allowlisted local archive, not a badge."""
import hashlib
import json
import platform
import subprocess
import sys
import zipfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
B=ROOT/'benchmarks'
RUNS=B/'runs/qualification_verified'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    chunks=['# APIShield artifact appendix: exact contents\n\nPrepared 15 October 2026. These are authored fixture qualification records, not model-generated experimental results. Unknown model/engine/invoice fields are explicitly unobserved, not fabricated. No artifact badge or empirical-study validation is asserted.\n',
            (B/'README.md').read_text(encoding='utf-8')]
    sections=[
        ('1. Exact implementation and configuration',[
            B/'provenance/repository.json', B/'configurations.json', B/'harness/run_ablation.py',B/'adapters/model_backend.py',
            B/'runners/candidate_worker.py',B/'runners/evaluation.py',B/'requirements-analysis.txt',B/'requirements-live.txt']),
        ('2. Exact executable task schema and four manifest records',[B/'tasks_manifest.schema.json',B/'tasks_manifest.json']),
        ('3. Six complete original fixture execution traces',[RUNS/f'B{i}_TASK-BANK-014_rep1.json' for i in range(1,7)]),
        ('4. Exact model configuration and observed provenance',[B/'profiles/gemini.json',B/'profiles/llama_cpp.json']),
        ('5. Measured fixture phase ledger and official-rate estimate configuration',[RUNS/'resource_ledger.csv',B/'profiles/rate_card.json']),
        ('6. Complete statistical analysis pipeline and its actual output',[B/'harness/aggregate_metrics.py',B/'analysis/qualification_verified/aggregate_metrics.csv',B/'analysis/qualification_verified/metrics.json'])]
    for heading,files in sections:
        chunks.append('\n## '+heading+'\n')
        for path in files:
            language={'.py':'python','.json':'json','.csv':'csv'}.get(path.suffix,'text')
            chunks.append('\n### '+path.as_posix()+'\n\nSHA-256: '+digest(path)+'\n\n'+chr(96)*3+language+'\n'+path.read_text(encoding='utf-8').rstrip()+'\n'+chr(96)*3+'\n')
    (B/'ARTIFACT_APPENDIX.md').write_text('\n'.join(chunks),encoding='utf-8')
    runtime={'captured_at':datetime.now(timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),
             'fixture_boundary':'trusted-fixtures; not an OS sandbox','docker_engine_available_during_preparation':False,
             'paid_model_requests_in_qualification':0,'local_gpu_execution_observed':False,
             'qualification_tests':'benchmarks/tests/test_artifact.py; see retained test output',
             'package_status':'local qualification scaffold; not a publicly archived or badged empirical-study artifact'}
    (B/'provenance/runtime.json').write_text(json.dumps(runtime,indent=2),encoding='utf-8')
    files=[]
    for path in B.rglob('*'):
        if not path.is_file():continue
        rel=path.relative_to(B)
        if any(part in {'.venv','_work','models','__pycache__','.pytest_cache'} for part in rel.parts):continue
        if rel.parts[0]=='runs' and rel.parts[1]!='qualification_verified':continue
        if rel.parts[0]=='analysis' and rel.parts[1]!='qualification_verified':continue
        if path.name=='archive_manifest.json':continue
        files.append(path)
    # The live controller adapter uses these backend modules, never frontend/UI.
    files += [p for p in (ROOT/'apishield').glob('*.py')]
    files += [ROOT/'config.py',ROOT/'requirements.txt',ROOT/'docs/academic-run-record-template.csv']
    files=sorted(set(files))
    manifest={p.relative_to(ROOT).as_posix():digest(p) for p in files}
    (B/'archive_manifest.json').write_text(json.dumps({'hash_algorithm':'sha256','files':manifest,'manifest_excludes_itself':True},indent=2),encoding='utf-8')
    files.append(B/'archive_manifest.json')
    target=ROOT/'reports/artifacts/APIShield-qualification-artifact-2026-10-15.zip'
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:archive.write(path,path.relative_to(ROOT).as_posix())
    target.with_suffix('.zip.sha256').write_text(digest(target)+'  '+target.name+'\n',encoding='utf-8')
    with zipfile.ZipFile(target) as archive:
        for name,expected in manifest.items():
            assert hashlib.sha256(archive.read(name)).hexdigest()==expected,name
        assert not any(name.endswith('.env') or '/.venv/' in name or '/models/' in name for name in archive.namelist())
    print(json.dumps({'appendix':str(B/'ARTIFACT_APPENDIX.md'),'archive':str(target),'sha256':digest(target),'files':len(files),'bytes':target.stat().st_size},indent=2))

if __name__=='__main__':main()
