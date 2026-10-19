import test from 'node:test';
import assert from 'node:assert/strict';
import {validateCredentialFile,modelConnectionPresentation,modelConfigureRequest} from '../src/model-settings.js';
import {createSelectionGate} from '../src/workspace.js';

test('credential size is rejected before reading',async()=>{
  let read=false;
  const file={size:65537,text:async()=>{read=true;return '{}';}};
  await assert.rejects(()=>validateCredentialFile(file),/64 KiB/);
  assert.equal(read,false);
});
test('credential JSON must identify service account and never echo invalid body',async()=>{
  await assert.rejects(()=>validateCredentialFile({size:10,text:async()=> 'SECRET-JSON'}),/valid service-account/);
  assert.equal(await validateCredentialFile({size:25,text:async()=>'{"type":"service_account"}'}),'{"type":"service_account"}');
});
test('connection summary exposes safe fields and distinguishes configured from tested',()=>{
  const data={configured:true,connection:{provider:'google_cloud',project:'test-project',location:'global',private_key:'SECRET'},model:'gemini-3.8-flash'};
  assert.match(modelConnectionPresentation(data).detail,/test-project/);
  assert.equal(modelConnectionPresentation(data).label,'Configured · not tested');
  assert.ok(!JSON.stringify(modelConnectionPresentation(data)).includes('SECRET'));
  assert.equal(modelConnectionPresentation({...data,test:{success:true}}).label,'Connection tested');
  assert.equal(modelConnectionPresentation({...data,test:{success:false}}).label,'Connection test failed');
  assert.equal(modelConnectionPresentation({configured:false}).label,'No connection');
});
test('provider requests are explicit and stale responses are excluded',()=>{
  assert.deepEqual(modelConfigureRequest('google_cloud','PRIVATE-JSON'),{path:'/api/settings/model/cloud',options:{method:'POST',headers:{'Content-Type':'application/json'},body:'PRIVATE-JSON'}});
  assert.throws(()=>modelConfigureRequest('developer','KEY'),/service accounts/);
  const gate=createSelectionGate();gate.select('first');const current=gate.capture('first');gate.select('second');assert.equal(current(),false);
});
