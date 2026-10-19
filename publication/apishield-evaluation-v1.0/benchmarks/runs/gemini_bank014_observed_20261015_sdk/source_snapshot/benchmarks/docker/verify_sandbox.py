"""Execute OS isolation probes against the same container runner as evaluation."""
import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from benchmarks.runners.evaluation import container_run

PROBE='''import json,os,socket
from pathlib import Path
checks={"non_root":os.getuid()==65534}
try:
    Path("/root-write-probe").write_text("probe")
    checks["root_read_only"]=False
except OSError:checks["root_read_only"]=True
try:
    connection=socket.create_connection(("1.1.1.1",443),timeout=2)
    connection.close()
    checks["egress_blocked"]=False
except OSError:checks["egress_blocked"]=True
status=Path("/proc/self/status").read_text()
checks["capabilities_dropped"]="CapEff:\\t0000000000000000" in status
checks["no_new_privileges"]="NoNewPrivs:\\t1" in status
checks["memory_limit"]=Path("/sys/fs/cgroup/memory.max").read_text().strip()=="536870912"
checks["pids_limit"]=Path("/sys/fs/cgroup/pids.max").read_text().strip()=="64"
checks["cpu_limit"]=Path("/sys/fs/cgroup/cpu.max").read_text().strip()=="100000 100000"
print(json.dumps(checks))
'''

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image',required=True)
    args=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='apishield-os-probe-') as directory:
        script=Path(directory)/'probe.py';script.write_text(PROBE)
        result=container_run(args.image,[(script,'/probe.py')],['python','-I','-B','/probe.py'],{})
    if result.returncode:raise RuntimeError('OS isolation probe failed: '+result.stderr[:1024])
    checks=json.loads(result.stdout)
    evidence={'image':args.image,'checks':checks,'all_passed':all(checks.values()),
              'scope':'Observed Linux cgroup-v2 configuration probes; not a sandbox escape audit'}
    (ROOT/'benchmarks/provenance/sandbox_verification.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))
    if not evidence['all_passed']:raise SystemExit(1)

if __name__=='__main__':main()
