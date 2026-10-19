import test from 'node:test';
import assert from 'node:assert/strict';
import { workflowPresentation, providerHealth, endpointIdentity, filterProviderGraph } from '../src/project-workflow.js';

test('merge does not imply deployed health, and rollback is a failure',()=>{
  assert.equal(workflowPresentation({state:'merged'}).tone,'pending');
  assert.equal(workflowPresentation({state:'verified'}).tone,'success');
  assert.equal(workflowPresentation({state:'failed',error:'Rollback'}).tone,'danger');
  assert.equal(workflowPresentation({state:'pr_open'}).label,'Awaiting human review');
});
test('provider graph filter retains shared orchestration and removes another provider',()=>{
  const graph={nodes:[{id:'p',provider_id:'payment'},{id:'t',provider_id:'theatre'},{id:'shared'}],edges:[{from:'shared',to:'p'},{from:'shared',to:'t'}]};
  assert.deepEqual(filterProviderGraph(graph,'payment').nodes.map(n=>n.id),['p','shared']);
  assert.equal(filterProviderGraph(graph,'payment').edges.length,1);
});
test('provider health follows real monitoring evidence',()=>{
  assert.equal(providerHealth({configured:false}).label,'Not configured');
  assert.equal(providerHealth({configured:true,last_success:'now',baseline_hash:'a',last_observation_hash:'b'}).label,'API change detected');
  assert.equal(providerHealth({configured:true,error:'unreachable'}).label,'Connection needs attention');
});
test('qualified endpoint display keeps providers distinct without leaking internal prefixes',()=>{
  assert.deepEqual(endpointIdentity('/__provider__/payment/payments'),{provider:'payment',path:'/payments'});
  assert.deepEqual(endpointIdentity('/payments'),{provider:'',path:'/payments'});
});
