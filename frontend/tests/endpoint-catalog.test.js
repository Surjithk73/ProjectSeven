import test from 'node:test';
import assert from 'node:assert/strict';
import { endpointPresentation } from '../src/overview-view.js';

test('catalog shows only consumed current endpoints, without comparison state', () => {
  const before = {operations:[{method:'GET',endpoint:'/balance',definition:{}},{method:'POST',endpoint:'/unused',definition:{}}]};
  const after = {operations:[{method:'GET',endpoint:'/balance/v2',definition:{}}]};
  const report = {operation:'compare',scan:{sites:[{method:'GET',endpoint:'/balance'}]},contract_overview:{before,after,changes:[{method:'GET',endpoint:'/balance',status:'removed'}]}};
  const value = endpointPresentation(report, true);
  assert.equal(value.comparing, false);
  assert.deepEqual(value.rows.map(row => row.endpoint), ['/balance']);
  assert.equal(value.contract, before);
  assert.ok(value.rows.every(row => !row.status));
  assert.equal(endpointPresentation(report, false).comparing, true);
  assert.equal(endpointPresentation({...report,operation:'scan'}).comparing, false);
});
