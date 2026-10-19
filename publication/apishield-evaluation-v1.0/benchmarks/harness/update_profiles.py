"""Refresh researched configuration without inventing observed provenance."""
import json
import os
from pathlib import Path

B=Path(__file__).resolve().parents[1]

def main():
    path=B/'profiles/gemini.json'
    profile=json.loads(path.read_text())
    profile.update(release_stage='GA',release_date='2026-09-02',retirement_not_before='2027-09-02',
        model_documentation='https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash',
        snapshot_status='Exact published GA ID selected; no separately addressable immutable snapshot documented',
        rate_limits={'provider_policy':'Standard PayGo with usage tiers; fixed quota not supported',
                     'project_rpm':None,'project_tpm':None,'project_quota_observed':False,
                     'client_max_concurrent_requests':1,'client_min_interval_seconds':1,
                     'source':'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/deploy/consumption-options'},
        request_envelope_schema='C:/Users/surji/ProjectSeven/benchmarks/profiles/gemini_request.schema.json',
        response_envelope_schema='C:/Users/surji/ProjectSeven/benchmarks/profiles/gemini_response.schema.json',
        envelope_scope='Schemas constrain the text-only benchmark REST payload; full raw SDK response retained separately')
    path.write_text(json.dumps(profile,indent=2)+'\n')
    path=B/'profiles/llama_cpp.json'
    profile=json.loads(path.read_text())
    profile.update(context_window=8192,threads=min(8,os.cpu_count() or 1),threads_batch=min(8,os.cpu_count() or 1),
        ngl=99,ngl_status='Requested GPU offload target, not observed executed layers',
        quantization_flags={'weight_format':'GGUF','weight_quantization':'Q4_K_M','cache_type_k':'f16','cache_type_v':'f16'},
        local_runtime_status='Not executed: llama-server and GGUF weights absent; observed RAM below weight size',
        power_assumption_watts=None,deployment_target='External capable GPU host required; local GPU not validated')
    profile['server_command']=['llama-server','--model',profile['local_weight_path'],'--host','127.0.0.1','--port','8080',
        '--ctx-size','8192','--threads',str(profile['threads']),'--threads-batch',str(profile['threads_batch']),
        '--n-gpu-layers','99','--cache-type-k','f16','--cache-type-v','f16','--seed','42','--temp','0.1','--top-p','0.95']
    path.write_text(json.dumps(profile,indent=2)+'\n')

if __name__=='__main__':main()
