import test from 'node:test';
import assert from 'node:assert/strict';
import { proposalPresentation, proposalRequest, targetDraft, targetRequest, publicationDetails } from '../src/publication.js';
import { createSelectionGate } from '../src/workspace.js';
import { localDraftPreview } from '../src/publication.js';

test('publication states describe preparation, remote uncertainty and published truth', () => {
  for (const state of ['preparing','ready','publishing','reconciling','reconciliation_needed','published','stale','failed','cancelled']) {
    assert.ok(proposalPresentation({status:state}).label);
  }
  assert.equal(proposalPresentation({status:'ready'}).publishable,true);
  assert.equal(proposalPresentation({status:'reconciliation_needed'}).publishable,false);
  assert.equal(proposalPresentation({status:'published'}).label,'Draft published');
});
test('separate preparation and publication carry captured revisions only', () => {
  assert.deepEqual(JSON.parse(proposalRequest('prepare',{jobId:'job',revision:7}).body),{job_id:'job',expected_revision:7});
  assert.deepEqual(JSON.parse(proposalRequest('publish',{revision:9}).body),{expected_revision:9});
  assert.equal(proposalRequest('reconcile').method,'POST');
});
test('target edit retains revision even after a new server value arrives', () => {
  const draft=targetDraft({repository:'owner/repo',base:'main',revision:3});
  const refreshed={repository:'other/repo',base:'dev',revision:4};
  assert.deepEqual(JSON.parse(targetRequest(draft).body),{repository:'owner/repo',base:'main',expected_revision:3});
  assert.notDeepEqual(targetDraft(refreshed),draft);
});
test('selection gate rejects late proposal replies after switching jobs', () => {
  const gate=createSelectionGate();gate.select('first');const first=gate.capture('first');
  gate.select('second');assert.equal(first(),false);
});
test('published review retains the remote head and commit and exposes partial recovery',()=>{
  assert.deepEqual(publicationDetails({branch:'codex/repair',publication:{commit:'a'.repeat(40),state:'closed',draft:false}}),{head:'codex/repair',commit:'a'.repeat(40),state:'closed',draft:false});
  assert.equal(proposalPresentation({status:'stale',effects:[{}]}).reconcilable,true);
});

test('a local draft contains the actual validated patch and evidence without a GitHub target',()=>{
  const patch='--- a/src/bankclient.py\n+++ b/src/bankclient.py\n@@ -1 +1 @@\n-old\n+new\n';
  const preview=localDraftPreview({job_id:'repair-7',integration:'banking-example',operation:'repair',status:'validated',
    source_commit:'a'.repeat(40),applied_files:{'src/bankclient.py':'digest'},
    impacted_sites:[{method:'POST',endpoint:'/transfers',function:'transfer'}]},patch);
  assert.match(preview.title,/NexusBank Integration/);
  assert.match(preview.body,/Recorded local validation: passed/);
  assert.match(preview.body,/GitHub.*not.*run/i);
  assert.match(preview.body,/POST \/transfers/);
  assert.equal(preview.patch,patch);
  assert.deepEqual(preview.files,['src/bankclient.py']);
  assert.equal(preview.sourceCommit,'a'.repeat(40));
});

test('local preview rejects unvalidated evidence and missing patch instead of inventing a draft',()=>{
  assert.throws(()=>localDraftPreview({operation:'repair',status:'failed'},'patch'),/validated/i);
  assert.throws(()=>localDraftPreview({operation:'repair',status:'validated'},''),/patch/i);
});
