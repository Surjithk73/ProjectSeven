"""Materialize trusted, runnable fixtures. No inference and no invented model records."""
import difflib
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / 'benchmarks'

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n' if isinstance(value, (dict, list)) else value, encoding='utf-8')

def prepare():
    configs = {}
    for number in range(1, 7):
        configs[f'B{number}'] = dict(enable_structural_graph=number >= 3,
            enable_semantic_clustering=number in (4, 6), enable_intent_inference=number in (5, 6),
            enable_hidden_invariant_checks=True, enable_generated_checks=number in (5, 6),
            enable_test_feedback=number >= 2)
    write(BENCH/'configurations.json', configs)
    rows = []
    specifications = [
        ('TASK-BANK-014', 'Banking', '/transfers', '/transfers', 'amount_cents', 'amount', {'source':'checking','destination':'savings','amount_cents':9007199254740993,'currency':'USD','idempotency_key':'transfer-014'}),
        ('TASK-BANK-015', 'Banking', '/transfers', '/transfers', 'amount_cents', 'amount', {'source':'reserve','destination':'merchant','amount_cents':1,'currency':'JPY','idempotency_key':'transfer-015'}),
        ('TASK-SHIP-029', 'Shipping', '/labels', '/labels/create', 'weight_grams', 'parcel', {'parcel_id':'parcel-029','weight_grams':1250,'idempotency_key':'label-029'}),
        ('TASK-PAY-008', 'Payment', '/refunds', '/refunds/create', 'transaction_id', 'refund', {'transaction_id':'paid-008','amount_cents':1999,'currency':'USD','idempotency_key':'refund-008'})]
    for task, domain, oldpath, newpath, oldfield, newfield, data in specifications:
        public = BENCH/'tasks'/task/'public'
        private = BENCH/'evaluator_private'/task
        if domain == 'Banking':
            body = "{'source': data['source'], 'destination': data['destination'], 'amount': {'value': data['amount_cents'], 'currency': data['currency']}}"
        elif domain == 'Shipping':
            body = "{'parcel': {'id': data['parcel_id'], 'weight_grams': data['weight_grams']}}"
        else:
            body = "{'refund': {'transaction_id': data['transaction_id'], 'amount_cents': data['amount_cents'], 'currency': data['currency']}}"
        reference = f"def build_request(data):\n    return {{'path': {newpath!r}, 'body': {body}, 'headers': {{'Idempotency-Key': data['idempotency_key']}}}}\n"
        old = f"def build_request(data):\n    return {{'path': {oldpath!r}, 'body': {{{oldfield!r}: data[{oldfield!r}]}}, 'headers': {{}}}}\n"
        def contract(path, field, version):
            return {'openapi':'3.0.3','info':{'title':task,'version':version},'paths':{path:{'post':{'description':'Preserve exact amounts, input identity, destination and idempotency key. No defaults may be invented.',
                'requestBody':{'required':True,'content':{'application/json':{'schema':{'type':'object','required':[field],'properties':{field:{'type':'integer' if field in ['amount_cents','weight_grams'] else 'string' if field=='transaction_id' else 'object'}}}}}},'responses':{'200':{'description':'Accepted'}}}}}}
        write(public/'client.py',old)
        write(public/'old_contract.json',contract(oldpath,oldfield,'1.0.0'))
        write(public/'new_contract.json',contract(newpath,newfield,'2.0.0'))
        write(public/'inputs.json',[data])
        hidden_inputs=[data.copy(), data.copy(), data.copy()]
        for index, item in enumerate(hidden_inputs):
            if 'amount_cents' in item:item['amount_cents']=[1,1999,9007199254740993][index]
            if 'weight_grams' in item:item['weight_grams']=[1,1250,9007199254740993][index]
            if 'transaction_id' in item:item['transaction_id']=f'paid-λ-{index}'
            if 'destination' in item:item['destination']=f'destination-λ-{index}'
            item['idempotency_key']=f'key-λ-{index}'
        write(private/'inputs.json',hidden_inputs)
        write(public/'test_public.py',f"def evaluate(inputs, outputs):\n    return {{'endpoint': all(o.get('path') == {newpath!r} for o in outputs), 'payload_shape': all(isinstance(o.get('body', {{}}).get({newfield!r}), dict) for o in outputs)}}\n")
        if domain == 'Banking':
            assertions = "{'exact_minor_units': all(type(o['body']['amount']['value']) is int and o['body']['amount']['value'] == d['amount_cents'] for d,o in zip(inputs,outputs)), 'currency': all(o['body']['amount']['currency'] == d['currency'] for d,o in zip(inputs,outputs)), 'destination': all(o['body']['destination'] == d['destination'] and o['body']['source'] == d['source'] for d,o in zip(inputs,outputs)), 'idempotency_key': all(o['headers']['Idempotency-Key'] == d['idempotency_key'] for d,o in zip(inputs,outputs))}"
        elif domain == 'Shipping':
            assertions = "{'parcel_identity': all(o['body']['parcel']['id'] == d['parcel_id'] for d,o in zip(inputs,outputs)), 'exact_weight': all(type(o['body']['parcel']['weight_grams']) is int and o['body']['parcel']['weight_grams'] == d['weight_grams'] for d,o in zip(inputs,outputs)), 'idempotency_key': all(o['headers']['Idempotency-Key'] == d['idempotency_key'] for d,o in zip(inputs,outputs))}"
        else:
            assertions = "{'original_transaction': all(o['body']['refund']['transaction_id'] == d['transaction_id'] for d,o in zip(inputs,outputs)), 'exact_minor_units': all(o['body']['refund']['amount_cents'] == d['amount_cents'] for d,o in zip(inputs,outputs)), 'currency': all(o['body']['refund']['currency'] == d['currency'] for d,o in zip(inputs,outputs)), 'idempotency_key': all(o['headers']['Idempotency-Key'] == d['idempotency_key'] for d,o in zip(inputs,outputs))}"
        write(private/'oracle.py',f'def evaluate(inputs, outputs):\n    return {assertions}\n')
        write(private/'golden.patch',''.join(difflib.unified_diff(old.splitlines(True),reference.splitlines(True),fromfile='a/client.py',tofile='b/client.py')))
        wrong_units = reference.replace("data['amount_cents']", "data['amount_cents'] / 100").replace("data['weight_grams']", "data['weight_grams'] / 1000")
        wrong_identity = reference.replace("data['destination']", "data['source']").replace("data['parcel_id']", "'another-parcel'").replace("data['transaction_id']", "'another-payment'")
        for method, source in [('B1', 'def build_request(data)\n    return {}\n'),('B2',wrong_units),('B3',wrong_identity),('B4',None),('B5',reference.replace("data['idempotency_key']", "'replacement-key'")),('B6',reference)]:
            candidate={'origin':'trusted_fixture_not_model_output','source':source,'abstain_reason':'Scripted abstention for harness qualification' if source is None else None,
                       'checks_source':"def check(inputs, outputs):\n    return all(isinstance(o['body'], dict) for o in outputs)\n"}
            write(BENCH/'fixture_candidates'/task/f'{method}.json',candidate)
        rows.append(dict(task_id=task,domain=domain,task_class='repairable',family_id=domain.lower()+'-qualification',repository_id='local-authored-fixture',
                         source_directory=public.as_posix(),old_contract_path=(public/'old_contract.json').as_posix(),new_contract_path=(public/'new_contract.json').as_posix(),
                         public_test_suite=(public/'test_public.py').as_posix(),hidden_oracle_suite=(private/'oracle.py').as_posix(),golden_reference_patch=(private/'golden.patch').as_posix(),
                         inputs_path=(public/'inputs.json').as_posix(),allowed_edit_paths=['client.py'],ground_truth_affected_locations=['client.py:build_request']))
        rows[-1]['hidden_inputs_path']=(private/'inputs.json').as_posix()
    write(BENCH/'tasks_manifest.json',{'schema_version':1,'record_kind':'runnable_local_qualification_fixtures','tasks':rows})
    properties={k:{'type':'array','items':{'type':'string'}} if isinstance(v,list) else {'type':'string','minLength':1} for k,v in rows[0].items()}
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','additionalProperties':False,'required':['schema_version','record_kind','tasks'],
            'properties':{'schema_version':{'const':1},'record_kind':{'const':'runnable_local_qualification_fixtures'},'tasks':{'type':'array','minItems':4,'items':{'type':'object','additionalProperties':False,'required':list(rows[0]),'properties':properties}}}}
    write(BENCH/'tasks_manifest.schema.json',schema)
    try:head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        head=json.loads((BENCH/'provenance/repository.json').read_text(encoding='utf-8'))['head']
    write(BENCH/'provenance/repository.json',{'head':head,'working_tree_clean':False,'head_is_not_artifact_revision':True,
         'note':'Uncommitted artifact source is identified by source_manifest.json; no new commit was created.'})
    write(BENCH/'profiles/gemini.json',{'provider':'google_cloud','requested_model':'gemini-3.8-flash','immutable_snapshot_verified':False,'resolved_model_version':None,
         'endpoint':'https://aiplatform.googleapis.com/v1/projects/gen-lang-client-0604700095/locations/global/publishers/google/models/gemini-3.8-flash:generateContent',
         'sdk':'google-genai','sdk_version':'2.22.0','location':'global','temperature':0.1,'top_p':0.95,'seed':42,'max_output_tokens':4096,'reasoning_setting':'LOW',
         'max_transport_retries':3,'transport_backoff_seconds':[1,2,4],'retryable_http_status':[429,500,502,503,504],
         'retired_example_model':'gemini-1.5-pro-002','retired_example_status':'not_selected; retired 2025-09-24',
         'lifecycle_source':'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions'})
    write(BENCH/'profiles/llama_cpp.json',{'provider':'llama.cpp','repository':'bartowski/Meta-Llama-3.1-70B-Instruct-GGUF',
         'revision':'83fb6e83d0a8aada42d499259bc929d922e9a558','file':'Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf','quantization':'GGUF Q4_K_M, not AWQ',
         'published_weight_sha256':'f775c87029be95fb41df9e2882e6e938b73121c30ffc235ac6b6b880add49aa5','published_size_bytes':42520398400,
         'metadata_source':'https://huggingface.co/api/models/bartowski/Meta-Llama-3.1-70B-Instruct-GGUF?blobs=true',
         'local_weight_path':(BENCH/'models/Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf').as_posix(),'local_weight_verified':False,'inference_engine_version':None,
         'endpoint':'http://127.0.0.1:8080/v1/chat/completions','temperature':0.1,'top_p':0.95,'seed':42,'max_output_tokens':4096,
         'deployment_target':'2 x NVIDIA RTX A6000 48GB; planning target, not observed hardware','power_assumption_watts':600,'energy_price_usd_kwh':0.20,
         'server_command':['llama-server','--model',(BENCH/'models/Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf').as_posix(),'--host','127.0.0.1','--port','8080','--ctx-size','16384','--n-gpu-layers','99','--split-mode','layer','--tensor-split','1,1','--seed','42','--temp','0.1','--top-p','0.95']})
    write(BENCH/'profiles/rate_card.json',{'model':'gemini-3.8-flash','region':'global','currency':'USD','observed_date':'2026-10-15','effective_until':'2026-12-31',
         'input_per_million':0.75,'cached_input_per_million':0.075,'output_including_reasoning_per_million':3.75,
         'source':'https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing','status':'public introductory list rates; estimates only, not invoices',
         'non_200_policy':'Google lists no input/output charge for non-200 responses; unknown transport outcomes require billing reconciliation'})
    from update_profiles import main as update_profiles
    update_profiles()
    print('Created four runnable qualification tasks and exact configuration/provenance files.')

if __name__=='__main__':prepare()
