import test from 'node:test';
import assert from 'node:assert/strict';
import { changeNotice } from '../src/overview-view.js';
test('comparison notice distinguishes actual changes, consumed impact and no change',()=>{
  const report={operation:'compare',status:'completed',impacted_sites:[{file:'src/client.py'}],contract_overview:{changes:[{method:'GET',endpoint:'/balance',status:'changed'},{method:'POST',endpoint:'/refunds',status:'removed'},{method:'POST',endpoint:'/refunds/create',status:'added'}]}};
  const value=changeNotice(report);
  assert.equal(value.title,'API changes detected');assert.equal(value.affected,1);
  assert.deepEqual(value.counts,{added:1,removed:1,changed:1});assert.equal(value.canAskAI,true);
  assert.equal(changeNotice({...report,impacted_sites:[]}).canAskAI,false);
  assert.equal(changeNotice({...report,contract_overview:{changes:[]}}).title,'No API changes detected');
  assert.equal(changeNotice({...report,operation:'scan'}),null);
});
