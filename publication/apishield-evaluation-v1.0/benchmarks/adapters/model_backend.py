"""Explicit research backend. Fixture mode never calls this adapter."""
import hashlib
import json
import time
from pathlib import Path

class Backend:
    def __init__(self, provider, profile, output):
        self.provider,self.profile,self.output=provider,profile,output
        self.calls=[]
        if provider=='llama-cpp':
            path=Path(profile['local_weight_path'])
            if not path.is_file():raise ValueError('Configured GGUF file is absent; no local provenance can be asserted')
            digest=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
            if digest != profile['published_weight_sha256']:raise ValueError('Local GGUF hash does not match pinned published fingerprint')
            if not profile['inference_engine_version']:raise ValueError('Record the actual llama-server build version before live research')

    def generate(self, prompt, stage):
        import httpx
        last=None
        for retry in range(4):
            minimum=self.profile.get('rate_limits',{}).get('client_min_interval_seconds',0)
            if self.calls:time.sleep(minimum)
            start=time.perf_counter()
            call={'stage':stage,'retry_index':retry,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'raw_prompt':prompt,
                  'generation_parameters':{'temperature':.1,'top_p':.95,'seed':42,'max_output_tokens':4096}}
            try:
                if self.provider=='google-cloud':
                    from apishield.model_access import environment_connection,model_client
                    from google.genai import types
                    connection=environment_connection()
                    if self.profile.get('transport')=='sdk_standard':
                        from google import genai
                        from google.oauth2 import service_account
                        from google.auth.transport.requests import Request
                        if not connection.ready:raise ValueError('Managed service account unavailable')
                        credentials=service_account.Credentials.from_service_account_info(json.loads(connection.credential_json),
                            scopes=['https://www.googleapis.com/auth/cloud-platform'])
                        request=Request()
                        credentials.refresh(lambda **kwargs:request(**{**kwargs,'timeout':30}))
                        client_context=genai.Client(enterprise=True,vertexai=True,credentials=credentials,
                            project=connection.project,location='global',http_options=types.HttpOptions(
                                api_version='v1',base_url='https://aiplatform.googleapis.com/',timeout=120000,
                                retry_options=types.HttpRetryOptions(attempts=1),client_args={'trust_env':False}))
                    else:client_context=model_client(connection,time.monotonic()+120)
                    call['transport']=self.profile.get('transport','application_deadline_transport')
                    with client_context as client:
                        result=client.models.generate_content(model=self.profile['requested_model'],contents=prompt,
                            config=types.GenerateContentConfig(temperature=.1,top_p=.95,seed=42,max_output_tokens=4096,
                                response_mime_type='application/json',thinking_config=types.ThinkingConfig(thinking_level='LOW'),
                                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)))
                    usage=result.usage_metadata
                    if usage is None or usage.prompt_token_count is None or usage.candidates_token_count is None:
                        raise ValueError('Provider omitted measured token usage')
                    call.update(resolved_model_version=getattr(result,'model_version',None),
                                prompt_tokens=getattr(usage,'prompt_token_count',0) or 0,cached_tokens=getattr(usage,'cached_content_token_count',0) or 0,
                                output_tokens=getattr(usage,'candidates_token_count',0) or 0,reasoning_tokens=getattr(usage,'thoughts_token_count',0) or 0,
                                response=result.model_dump(mode='json'),response_text=result.text,http_status=200)
                    call['request_envelope']={'contents':[{'role':'user','parts':[{'text':prompt}]}],
                        'generationConfig':{'temperature':.1,'topP':.95,'seed':42,'maxOutputTokens':4096,
                            'responseMimeType':'application/json','thinkingConfig':{'thinkingLevel':'LOW'}}}
                    call['response_envelope']=result.model_dump(mode='json',by_alias=True,exclude_none=True)
                else:
                    body={'model':self.profile['repository'],'messages':[{'role':'user','content':prompt}],
                          'temperature':.1,'top_p':.95,'seed':42,'max_tokens':4096,'stream':False}
                    response=httpx.post(self.profile['endpoint'],json=body,timeout=120);response.raise_for_status()
                    result=response.json();usage=result.get('usage',{})
                    call.update(resolved_model_version=result.get('model'),prompt_tokens=usage.get('prompt_tokens',0),cached_tokens=0,
                                output_tokens=usage.get('completion_tokens',0),reasoning_tokens=0,response=result,
                                response_text=result['choices'][0]['message']['content'],http_status=200)
                    call['decoder_tokens_per_second']=result.get('timings',{}).get('predicted_per_second')
                parsed=json.loads(call['response_text'])
                call['elapsed_seconds']=time.perf_counter()-start
                self.calls.append(call);self._save()
                return parsed
            except Exception as error:
                status=getattr(error,'code',None) or getattr(getattr(error,'response',None),'status_code',None)
                call.update(elapsed_seconds=time.perf_counter()-start,http_status=call.get('http_status',status),error_category=type(error).__name__)
                self.calls.append(call);self._save();last=error
                if status not in [429,500,502,503,504] or retry==3:break
                time.sleep([1,2,4][retry])
        raise RuntimeError(f'Model request failed; category={type(last).__name__}; no provider fallback') from None

    def _save(self):
        self.output.write_text(json.dumps(self.calls,indent=2),encoding='utf-8')
