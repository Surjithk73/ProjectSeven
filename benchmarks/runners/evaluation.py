"""Controller-side test execution; oracle source never enters candidate mounts."""
import importlib.util
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

WORKER=Path(__file__).with_name('candidate_worker.py')

def valid_image(image):
    return bool(image and re.fullmatch(r'(?:[^\s]+@)?sha256:[0-9a-f]{64}',image))

def container_run(image, mounts, command, payload):
    if not valid_image(image):
        raise ValueError('Supply a resolved content-addressed Docker image')
    name='apishield-eval-'+uuid.uuid4().hex
    cmd=['docker','run','--name',name,'--rm','--network','none','--read-only',
         '--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64',
         '--memory','512m','--memory-swap','512m','--cpus','1','--log-driver','none',
         '--tmpfs','/tmp:rw,noexec,nosuid,size=64m','--user','65534:65534']
    for source,target in mounts:
        cmd += ['--mount',f'type=bind,source={Path(source).resolve()},target={target},readonly']
    cmd += ['--workdir','/work','-i',image,*command]
    # Bound collected output on disk; terminate noisy or timed-out workers.
    import tempfile
    import time
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr)
        try:
            proc.stdin.write(json.dumps(payload).encode());proc.stdin.close()
            deadline=time.monotonic()+30
            while proc.poll() is None:
                if time.monotonic()>deadline or stdout.tell()+stderr.tell()>1048576:
                    raise TimeoutError('Container exceeded runtime or output budget')
                time.sleep(.05)
            stdout.seek(0);stderr.seek(0)
            return subprocess.CompletedProcess(cmd,proc.returncode,stdout.read(1048576).decode('utf-8',errors='replace'),stderr.read(1048576).decode('utf-8',errors='replace'))
        finally:
            if proc.poll() is None:proc.kill();proc.wait()
            subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=10)

def execute(workspace, inputs, boundary, image=None):
    if boundary == 'docker':
        result=container_run(image,[(workspace,'/work'),(WORKER,'/runner.py')],['python','-I','-B','/runner.py'],inputs)
    elif boundary == 'trusted-fixtures':
        cmd=[sys.executable,'-I','-B',str(WORKER)]
    else:raise ValueError('Unknown execution boundary')
    if boundary != 'docker':
        result=subprocess.run(cmd,input=json.dumps(inputs),text=True,capture_output=True,cwd=workspace,timeout=30,
                              env={'SYSTEMROOT':__import__('os').environ.get('SYSTEMROOT','C:/Windows'), 'PYTHONIOENCODING':'utf-8'})
    value=None
    if result.returncode==0:
        try:value=json.loads(result.stdout)
        except ValueError:pass
    return result,value

def judge(suite, inputs, outputs, boundary='trusted-fixtures', image=None):
    if boundary == 'docker':
        result=container_run(image,[(suite,'/oracle.py'),(WORKER.with_name('oracle_worker.py'),'/oracle_worker.py')],
            ['python','-I','-B','/oracle_worker.py'],{'inputs':inputs,'outputs':outputs})
        if result.returncode:raise RuntimeError('Evaluator container failed')
        checks=json.loads(result.stdout)
        if not isinstance(checks,dict) or not checks or any(type(v) is not bool for v in checks.values()):
            raise ValueError('Invalid evaluator response')
        return checks
    spec=importlib.util.spec_from_file_location('qualification_oracle',suite)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    try:
        checks=module.evaluate(inputs,outputs)
        if not isinstance(checks,dict) or not checks or any(type(v) is not bool for v in checks.values()):
            raise ValueError('Oracle must return nonempty named boolean assertions')
        return checks
    except (KeyError,TypeError,IndexError):return {'oracle_contract':False}
