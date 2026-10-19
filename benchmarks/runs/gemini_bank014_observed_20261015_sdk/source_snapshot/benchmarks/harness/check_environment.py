"""Retain bounded environment probes; failure is evidence, not an invented build."""
import json
import subprocess
import time
from datetime import datetime,timezone
from pathlib import Path

B=Path(__file__).resolve().parents[1]

def probe(command):
    start=time.monotonic()
    try:
        value=subprocess.run(command,capture_output=True,text=True,timeout=15)
        return {'command':command,'exit_code':value.returncode,'stdout':value.stdout[:8192],
                'stderr':value.stderr[:8192],'elapsed_seconds':time.monotonic()-start}
    except (OSError,subprocess.TimeoutExpired) as error:
        return {'command':command,'exit_code':None,'error_category':type(error).__name__,
                'elapsed_seconds':time.monotonic()-start}

def main():
    checks=[probe(['docker','version','--format','{{.Client.Version}}']),
            probe(['docker','info','--format','{{.ServerVersion}}']),
            probe(['docker','compose','version']),probe(['nvidia-smi']),probe(['llama-server','--version'])]
    record={'captured_at':datetime.now(timezone.utc).isoformat(),'probes':checks,
            'docker_engine_available':checks[1]['exit_code']==0,'docker_image_built':False,
            'container_evaluation_verified':False,'gpu_inference_observed':False}
    (B/'provenance/environment_check.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
