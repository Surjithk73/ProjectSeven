"""Observe host/GPU data around a command; absent sensors stay unmeasured."""
import argparse
import csv
import io
import json
import os
import platform
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

B=Path(__file__).resolve().parents[1]

def measured_energy(samples, start, end):
    """Trapezoidal total GPU board energy, clipped to one recorded run window."""
    if len(samples)<2 or start<samples[0]['seconds'] or end>samples[-1]['seconds']:
        return None
    energy=0.
    for a,b in zip(samples,samples[1:]):
        lo=max(start,a['seconds']);hi=min(end,b['seconds'])
        if hi<=lo:continue
        if not a['gpus'] or {g['uuid'] for g in a['gpus']}!={g['uuid'] for g in b['gpus']}:return None
        if any(g['power_watts'] is None for g in a['gpus']+b['gpus']):return None
        pa=sum(g['power_watts'] for g in a['gpus']);pb=sum(g['power_watts'] for g in b['gpus'])
        span=b['seconds']-a['seconds']
        if span<=0:return None
        plo=pa+(pb-pa)*(lo-a['seconds'])/span;phi=pa+(pb-pa)*(hi-a['seconds'])/span
        energy+=(plo+phi)/2*(hi-lo)/3600000
    return energy

def powershell_json(script):
    if os.name!='nt':return None
    result=subprocess.run(['powershell','-NoProfile','-Command',script+' | ConvertTo-Json -Compress'],capture_output=True,text=True,timeout=15)
    return json.loads(result.stdout) if result.returncode==0 and result.stdout.strip() else None

def sample_gpu():
    if not shutil.which('nvidia-smi'):return []
    query='uuid,name,driver_version,memory.total,memory.used,power.draw'
    result=subprocess.run(['nvidia-smi','--query-gpu='+query,'--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
    if result.returncode:return []
    rows=[]
    for row in csv.reader(io.StringIO(result.stdout)):
        uuid,name,driver,total,used,power=[v.strip() for v in row]
        number=lambda v:float(v) if v not in {'[N/A]','N/A','[Not Supported]'} else None
        rows.append(dict(uuid=uuid,name=name,driver_version=driver,total_vram_mib=number(total),used_vram_mib=number(used),power_watts=number(power)))
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=B/'profiles/hardware_telemetry.json')
    p.add_argument('--run-dir',type=Path)
    p.add_argument('--electricity-usd-kwh',type=float)
    p.add_argument('--amortized-usd-hour',type=float)
    p.add_argument('command',nargs=argparse.REMAINDER)
    args=p.parse_args()
    start_epoch=time.time();start=time.monotonic();baseline=sample_gpu();samples=[{'seconds':0,'gpus':baseline}]
    command=args.command[1:] if args.command[:1]==['--'] else args.command
    returncode=None
    if command:
        proc=subprocess.Popen(command)
        while proc.poll() is None:
            time.sleep(.25);samples.append({'seconds':time.monotonic()-start,'gpus':sample_gpu()})
        returncode=proc.returncode
        samples.append({'seconds':time.monotonic()-start,'gpus':sample_gpu()})
    gpus=[]
    for item in baseline:
        records=[(s['seconds'],g) for s in samples for g in s['gpus'] if g['uuid']==item['uuid']]
        power=[g['power_watts'] for _,g in records if g['power_watts'] is not None]
        energy=sum((b[0]-a[0])*(a[1]['power_watts']+b[1]['power_watts'])/2/3600000
                   for a,b in zip(records,records[1:]) if a[1]['power_watts'] is not None and b[1]['power_watts'] is not None) if len(power)==len(records) and len(records)>1 else None
        gpus.append({**item,'baseline_vram_mib':item['used_vram_mib'],
            'peak_vram_mib':max(g['used_vram_mib'] for _,g in records if g['used_vram_mib'] is not None),
            'average_watts':sum(power)/len(power) if power else None,'sampled_energy_kwh':energy})
    throughputs=[]
    if args.run_dir:
        for path in args.run_dir.glob('evidence/*/model_calls.json'):
            for call in json.loads(path.read_text()):
                timing=call.get('response',{}).get('timings',{})
                if timing.get('predicted_per_second') is not None:
                    throughputs.append(timing['predicted_per_second'])
    profile={'captured_at':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),
        'processor':platform.processor(),'logical_cpus':os.cpu_count(),
        'physical_memory':powershell_json('Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory'),
        'display_adapters':powershell_json('Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,AdapterRAM'),
        'cuda_compiler':shutil.which('nvcc'),'nvidia_smi':shutil.which('nvidia-smi'),'llama_server':shutil.which('llama-server'),
        'cuda_version':None,'cuda_version_status':'No CUDA runtime version measurement collected',
        'gpus':gpus,'samples':samples,'command':command,'command_exit_code':returncode,'duration_seconds':time.monotonic()-start,
        'decoder_tokens_per_second':sum(throughputs)/len(throughputs) if throughputs else None,
        'throughput_source':'llama.cpp response.timings.predicted_per_second; not tokens divided by total API latency',
        'measurement_status':'sampled_gpu' if gpus and command else 'gpu_baseline_only' if gpus else 'no_supported_gpu_sensor',
        'missing_measurements_are_zero':False,'electricity_usd_kwh':args.electricity_usd_kwh,'amortized_usd_hour':args.amortized_usd_hour}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(profile,indent=2)+'\n')
    # Integrate each run's timestamp window; never allocate a whole-session average.
    if args.run_dir:
        ledger=args.run_dir/'resource_ledger.csv'
        rows=list(csv.DictReader(ledger.open(newline='',encoding='utf-8')))
        for row in rows:
            trace=json.loads((args.run_dir/(row['run_id']+'.json')).read_text())
            begin=datetime.fromisoformat(trace['timestamp_start']).timestamp()-start_epoch
            end=datetime.fromisoformat(trace['timestamp_end']).timestamp()-start_epoch
            energy=measured_energy(samples,begin,end)
            energy_cost=energy*args.electricity_usd_kwh if energy is not None and args.electricity_usd_kwh is not None else None
            amortized=float(row['total_seconds'])/3600*args.amortized_usd_hour if args.amortized_usd_hour is not None else None
            api=float(row['estimated_api_usd']) if row['estimated_api_usd'] else None
            total=api+energy_cost+amortized if all(v is not None for v in (api,energy_cost,amortized)) else None
            row.update(telemetry_profile=args.output.as_posix(),gpu_measurement_status=profile['measurement_status'],
                measured_energy_kwh=energy,electricity_usd_kwh=args.electricity_usd_kwh,
                amortized_usd_hour=args.amortized_usd_hour,energy_cost_usd=energy_cost,amortized_compute_cost_usd=amortized,
                total_cost_usd=total,cost_completeness='GPU board energy plus runtime allocation and API estimate' if total is not None else 'Incomplete; unmeasured components remain empty')
        with ledger.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps({'telemetry':str(args.output),'measurement_status':profile['measurement_status'],'gpus':len(gpus)}))
    if returncode:raise SystemExit(returncode)

if __name__=='__main__':main()
