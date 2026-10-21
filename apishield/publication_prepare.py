"""Reconstruct retained diffs and independently revalidate them without inference."""
import hashlib
import json
from pathlib import Path
import re
import tempfile

from .configuration import load_config,relative_path
from .jobs import atomic_json,JobCancelled,JobTimedOut
from .workspace import prepare_workspace,_git,_secret
from .commands import run_command
from .engine import _hash_files


def evidence_hash(store,job_id):
    root=store._path(job_id)
    contracts=root/'contracts'
    if contracts.is_symlink() or not contracts.is_dir():raise ValueError('Unsafe verification contract evidence')
    result=store.get(job_id)
    digest=hashlib.sha256()
    for name in ('config.json','source.json','result.json','candidate.patch','contracts/base.json','contracts/target.json'):
        path=root/name
        if path.is_symlink() or not path.is_file():raise ValueError('Unsafe verification evidence')
        content=path.read_bytes()
        if name.startswith('contracts/'):
            label=path.stem
            if hashlib.sha256(content).hexdigest()!=result.get(f'{label}_spec_hash'):
                raise ValueError('Verification contract evidence changed')
        digest.update(name.encode()+b'\0'+content)
    return digest.hexdigest()


def retained_patch(store,job_id):
    result=store.get(job_id)
    if result.get('status')!='validated' or result.get('operation')!='repair' or result.get('patch')!='candidate.patch':
        raise ValueError('Only validated repair jobs can prepare a draft PR')
    path=store._path(job_id)/'candidate.patch'
    if path.is_symlink() or not path.is_file() or path.stat().st_size>2*1024*1024:
        raise ValueError('Unsafe or oversized repair patch')
    patch=path.read_bytes()
    digest=hashlib.sha256(patch).hexdigest()
    if not patch or digest!=result.get('patch_sha256'):
        raise ValueError('Repair patch changed or has no validation-time digest; regenerate the repair')
    if not re.fullmatch('[0-9a-f]{40}',result.get('source_commit','')):
        raise ValueError('Repair has no supported pinned source commit')
    if _secret('candidate.patch',patch):raise ValueError('Known secret marker in proposed source')
    return result,patch


def prepare_repair(store,job_id,check=None,*,verification_job_id=None):
    from .engine import run_job
    result,patch=retained_patch(store,job_id)
    source_root=store._path(job_id)
    for name in ('config.json','contracts/base.json','contracts/target.json'):
        if (source_root/name).is_symlink():raise ValueError('Unsafe retained configuration')
    raw=json.loads((source_root/'config.json').read_text(encoding='utf-8'))
    for label in ('base','target'):
        path=source_root/f'contracts/{label}.json'
        if hashlib.sha256(path.read_bytes()).hexdigest()!=result[f'{label}_spec_hash']:
            raise ValueError('Retained contract changed')
        raw[f'{label}_spec']=str(path)
    raw['ref']=result['source_commit']
    job=None
    with tempfile.TemporaryDirectory(prefix='publication-',dir=store.root) as scratch:
        config_path=Path(scratch)/'config.json';atomic_json(config_path,raw)
        config=load_config(config_path)
        job=store.create(config,'repair',job_id=verification_job_id)
        job._initial['publication_source_job']=job_id
        if result.get('integration'):job._initial['integration']=result['integration']
        atomic_json(job.path/'result.json',job._initial)
        original_cancelled=job.cancelled
        def cancelled():
            if check:check()
            return original_cancelled()
        job.cancelled=cancelled
        def checked():
            job.check()
        try:
            checked();prepare_workspace(job)
            before=_hash_files(job.workspace,include_caches=True)
            originals={name:(job.workspace/name).read_bytes() for name in before}
            allowed={site['file'] for site in result['impacted_sites']}
            patch_path=Path(scratch)/'candidate.patch';patch_path.write_bytes(patch)
            def command(argv,label):
                checked()
                outcome=run_command(argv,job,label)
                checked()
                if outcome['exit_code']!=0 or outcome['timed_out'] or outcome['output_limited']:
                    raise ValueError('Retained patch cannot be safely reconstructed')
                return outcome['stdout']
            git_apply=['git','-c','core.autocrlf=false','-c','core.eol=lf','apply']
            summary=command([*git_apply,'--summary',str(patch_path)],'publication_inspect')
            if summary.strip():raise ValueError('Added/deleted/renamed/mode changes cannot publish')
            command([*git_apply,'--check',str(patch_path)],'publication_check')
            command([*git_apply,str(patch_path)],'publication_apply')
            after=_hash_files(job.workspace,include_caches=True)
            if set(before)!=set(after):raise ValueError('Publication cannot add or delete files')
            changed=sorted(name for name in before if before[name]!=after[name])
            if not changed:raise ValueError('Publication patch has no source changes')
            modes={}
            for entry in _git(job,'ls-tree','-rz',result['source_commit'],binary=True).split(b'\0'):
                if entry:
                    meta,name=entry.split(b'\t',1);modes[name.decode()]=meta.split()[0].decode()
            files=[];candidate={'patches':[]}
            for name in changed:
                name=relative_path(name)
                content=(job.workspace/name).read_bytes()
                if name not in allowed or Path(name).suffix!='.py' or before[name][1]!=after[name][1]:
                    raise ValueError('Publication changed an unapproved source file')
                if _secret(name,content):raise ValueError('Known secret marker in proposed source')
                candidate['patches'].append({'file':name,'old_code_snippet':originals[name].decode('utf-8'),'new_code_snippet':content.decode('utf-8')})
                blob=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
                files.append({'path':name,'content':content.decode('utf-8'),'mode':modes[name],'blob_sha':blob})
            candidate_path=Path(scratch)/'candidate.json';atomic_json(candidate_path,candidate)
            checked()
            verified=run_job(config,'repair',store,candidate_path=candidate_path,job=job)
            checked()
            if verified['status']!='validated' or verified.get('patch_sha256')!=result['patch_sha256']:
                raise ValueError('Offline revalidation did not validate the identical complete patch')
            return {'source_job_id':job_id,'verification_job_id':job.id,'source_commit':result['source_commit'],
                'patch_sha256':result['patch_sha256'],'patch':patch.decode('utf-8'),'files':files,
                'evidence_sha256':evidence_hash(store,job.id),'validation':{
                    'status':'validated','test_commands':len(config.test_commands),
                    'requirements':[{key:item.get(key) for key in ('id','description','status','checks')} for item in verified['requirement_outcomes']],
                    'proposal_source':result.get('proposal_source','unavailable'),
                    'generation_guidance':result.get('generation_guidance'),
                    'model_connection':result.get('model_connection')}}
        except (JobCancelled,JobTimedOut) as error:
            job.cancelled=original_cancelled
            job.finish({'status':'cancelled' if isinstance(error,JobCancelled) else 'failed','error':str(error)})
            raise
        except Exception:
            job.cancelled=original_cancelled
            job.finish({'status':'failed','error':'Publication preparation failed; inspect linked validation evidence'})
            raise
        finally:
            job.cancelled=original_cancelled
            job.cleanup()
