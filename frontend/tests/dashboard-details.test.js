import test from 'node:test';
import assert from 'node:assert/strict';
import { integrationSnapshot, activityOutcome, loadCheckPreview, saveCheckPreview } from '../src/dashboard-details.js';

test('snapshot uses recorded consumers, accepted API version and the latest actual check', () => {
  const jobs = [{integration:'bank',operation:'compare',status:'completed',created_at:'2026-10-16T09:00:00Z',comparison:{changed_operations:[{},{}]}},
    {integration:'other',operation:'compare',status:'failed',created_at:'2026-10-16T10:00:00Z'}];
  const snapshot = integrationSnapshot('bank', {integration:'bank',contract_overview:{before:{info:{version:'2.0.0'}}},scan:{sites:[
    {method:'GET',endpoint:'/accounts',file:'src/client.py'},
    {method:'GET',endpoint:'/accounts',file:'src/routes.py'},
    {method:'POST',endpoint:'/transfers',file:'src/client.py'}]}}, jobs);
  assert.equal(snapshot.version,'2.0.0');
  assert.equal(snapshot.endpoints,2);
  assert.equal(snapshot.files,2);
  assert.equal(snapshot.monitoring,'Successful');
  assert.equal(snapshot.checkOutcome,'2 endpoint changes detected');
});

test('failed checks and missing evidence never become successful monitoring or invented counts', () => {
  assert.equal(integrationSnapshot('bank',null,[]).monitoring,'Not checked');
  assert.equal(integrationSnapshot('bank',null,[]).endpoints,null);
  assert.equal(integrationSnapshot('bank',{integration:'other',scan:{sites:[]}},[]).files,null);
  assert.equal(integrationSnapshot('bank',null,[{integration:'bank',operation:'compare',status:'failed'}]).monitoring,'Needs attention');
});

test('recent activity distinguishes scans, API changes, applied updates and failures', () => {
  assert.equal(activityOutcome({operation:'scan',status:'completed',scan:{sites:[{method:'GET',endpoint:'/a'},{method:'GET',endpoint:'/a'}]}}),'1 endpoint discovered');
  assert.equal(activityOutcome({operation:'compare',status:'completed',comparison:{changed_operations:[]}}),'No API changes detected');
  assert.equal(activityOutcome({operation:'repair',status:'validated',application:{status:'applied',files:['src/a.py','src/b.py']}}),'Update applied · 2 files');
  assert.equal(activityOutcome({operation:'repair',status:'validated'}),'Validation passed · Ready to review');
  assert.equal(activityOutcome({operation:'repair',status:'failed'}),'Update could not complete');
  assert.equal(activityOutcome({operation:'scan',status:'completed'}),'Scan completed');
});

test('automatic-check settings are local preview data, isolated per project and bounded', () => {
  const data = new Map();
  const storage = {getItem:key=>data.get(key),setItem:(key,value)=>data.set(key,value)};
  saveCheckPreview('bank',{enabled:true,interval:60},storage);
  assert.deepEqual(loadCheckPreview('bank',storage),{enabled:true,interval:60});
  assert.deepEqual(loadCheckPreview('other',storage),{enabled:false,interval:60});
  saveCheckPreview('bank',{enabled:true,interval:1},storage);
  assert.equal(loadCheckPreview('bank',storage).interval,60);
  assert.deepEqual(loadCheckPreview('bank',{getItem(){throw new Error('blocked');}}),{enabled:false,interval:60});
});
