import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from benchmarks.harness.run_ablation import outcome
from benchmarks.runners.evaluation import execute,judge

def test_rubric_never_calls_infrastructure_failure_an_abstention():
    assert outcome(True,False,0,0)=='PASS'
    assert outcome(True,False,0,1)=='PLAUSIBLE_BUT_INCORRECT'
    assert outcome(False,False,None,None)=='SYNTAX_ERROR'
    assert outcome(True,True,None,None)=='ABSTAIN/REFUSED'
    assert outcome(True,False,1,None)=='TEST_FAILURE'
    assert outcome(True,False,None,None,infrastructure=True)=='INFRASTRUCTURE_ERROR'

def test_all_treatments_share_hidden_evaluation_and_only_b5_b6_add_checks():
    config=json.loads((ROOT/'benchmarks/configurations.json').read_text())
    assert all(v['enable_hidden_invariant_checks'] for v in config.values())
    assert {k for k,v in config.items() if v['enable_generated_checks']}=={'B5','B6'}
    assert {k for k,v in config.items() if v['enable_semantic_clustering']}=={'B4','B6'}

def test_golden_patches_apply_and_pass_independent_oracles():
    tasks=json.loads((ROOT/'benchmarks/tasks_manifest.json').read_text())['tasks']
    for task in tasks:
        with tempfile.TemporaryDirectory(prefix='apishield-golden-') as path:
            work=Path(path)
            (work/'client.py').write_bytes(Path(task['source_directory'],'client.py').read_bytes())
            result=subprocess.run(['git','apply','--check',task['golden_reference_patch']],cwd=work,capture_output=True,text=True)
            assert result.returncode==0,result.stderr
            subprocess.run(['git','apply',task['golden_reference_patch']],cwd=work,check=True,capture_output=True)
            inputs=json.loads(Path(task['hidden_inputs_path']).read_text())
            result,value=execute(work,inputs,'trusted-fixtures')
            assert result.returncode==0,result.stderr
            assert all(judge(task['hidden_oracle_suite'],inputs,value['outputs']).values())

def test_record_schema_hashes_and_oracle_context_separation():
    runs=ROOT/'benchmarks/runs/qualification_verified'
    traces=list(runs.glob('B*_TASK-*_rep*.json'))
    assert len(traces)==24
    for path in traces:
        trace=json.loads(path.read_text())
        assert len(trace['record'])==56
        assert trace['record_kind']=='fixture_replay'
        assert trace['requested_model'] is None and trace['prompt_tokens']==0
        folder=runs/'evidence'/trace['run_id']
        for prompt in folder.glob('prompt_*.txt'):
            content=prompt.read_text(encoding='utf-8')
            assert 'evaluator_private' not in content
            assert 'golden.patch' not in content
            assert 'hidden_oracle_suite' not in content
        assert abs(sum(trace['phases_seconds'].values())+trace['overhead_seconds']-trace['record']['total_seconds'])<1e-8
    b2=json.loads((runs/'B2_TASK-BANK-014_rep1.json').read_text())
    b6=json.loads((runs/'B6_TASK-BANK-014_rep1.json').read_text())
    assert b2['visible_test_exit_code']==0 and b2['hidden_oracle_exit_code']==1
    assert b2['invariants_preserved']['exact_minor_units'] is False
    assert b6['hidden_oracle_exit_code']==0 and all(b6['invariants_preserved'].values())

def test_live_generation_fails_closed_without_docker_boundary(tmp_path):
    result=subprocess.run([sys.executable,str(ROOT/'benchmarks/harness/run_ablation.py'),'--mode','live','--execute-live','--output',str(tmp_path/'not-created')],capture_output=True,text=True)
    assert result.returncode!=0
    assert not (tmp_path/'not-created').exists()


def test_malformed_model_json_records_one_billable_response_once(tmp_path, monkeypatch):
    import httpx
    import pytest
    from benchmarks.adapters.model_backend import Backend
    class Response:
        def raise_for_status(self): pass
        def json(self):
            return {'model':'server-reported-version', 'usage':{'prompt_tokens':10,'completion_tokens':2},
                    'choices':[{'message':{'content':'invalid JSON response'}}]}
    monkeypatch.setattr(httpx,'post',lambda *args,**kwargs:Response())
    backend=Backend.__new__(Backend)
    backend.provider='llama-cpp'
    backend.profile={'repository':'bartowski/Meta-Llama-3.1-70B-Instruct-GGUF','endpoint':'http://127.0.0.1:8080/v1/chat/completions'}
    backend.output=tmp_path/'calls.json'
    backend.calls=[]
    with pytest.raises(RuntimeError):backend.generate('public context only','repair')
    assert len(backend.calls)==1
    assert backend.calls[0]['http_status']==200
    assert backend.calls[0]['prompt_tokens']==10


def test_docker_worker_and_judge_have_disjoint_mounts(tmp_path, monkeypatch):
    from benchmarks.runners import evaluation
    calls=[]
    def run(image,mounts,command,payload):
        calls.append((mounts,payload))
        return subprocess.CompletedProcess(command,0,json.dumps({'exact_minor_units':True}),'')
    monkeypatch.setattr(evaluation,'container_run',run)
    suite=tmp_path/'oracle.py'
    checks=evaluation.judge(suite,[{'amount':1}],[{'amount':1}],'docker','sha256:'+'a'*64)
    assert checks=={'exact_minor_units':True}
    assert [target for _,target in calls[0][0]]==['/oracle.py','/oracle_worker.py']
    assert all(target!='/work' for _,target in calls[0][0])
    assert evaluation.valid_image('sha256:'+'a'*64)
    assert not evaluation.valid_image('python:latest')


def test_profile_records_unknown_measurements_honestly():
    profile=json.loads((ROOT/'benchmarks/profiles/gemini.json').read_text())
    assert profile['temperature']==.1 and profile['seed']==42
    assert profile['immutable_snapshot_verified'] is False
    assert profile['rate_limits']['project_quota_observed'] is False
    local=json.loads((ROOT/'benchmarks/profiles/llama_cpp.json').read_text())
    assert local['context_window']==8192
    assert local['local_weight_verified'] is False


def test_energy_integration_uses_run_window_and_preserves_missing_sensor():
    from benchmarks.harness.collect_telemetry import measured_energy
    samples=[{'seconds':0,'gpus':[{'uuid':'device','power_watts':100}]},
             {'seconds':10,'gpus':[{'uuid':'device','power_watts':200}]}]
    assert abs(measured_energy(samples,2,8)-150*6/3600000)<1e-12
    assert measured_energy(samples,-1,8) is None
    assert measured_energy([{'seconds':0,'gpus':[]},{'seconds':10,'gpus':[]}],2,8) is None
