import test from 'node:test';
import assert from 'node:assert/strict';
import { applyReviewedUpdate, appliedUpdateSummary } from '../src/workspace_flow.js';
import { refreshedJobReport } from '../src/workspace.js';

const report = {job_id:'repair-7',operation:'repair',status:'validated',integration:'banking-example'};
const application = {status:'applied',files:['src/bankclient.py','tests/apishield_generated/test_balance.py']};

test('apply keeps the original result selected and confirms the committed outcome before refreshing it', async () => {
  const calls = [], updates = [];
  await applyReviewedUpdate(report, {
    request:async (url, options) => {
      calls.push([url, options?.method]);
      if (options?.method === 'POST') return application;
      assert.equal(updates[0].application.status,'applied');
      return {...report,application,current_graph_report:{job_id:'current-8'}};
    },
    isCurrent:()=>true,
    onApplied:value=>updates.push(value),
  });
  assert.deepEqual(calls,[['/api/jobs/repair-7/apply','POST'],['/api/jobs/repair-7',undefined]]);
  assert.ok(updates.every(value=>value.job_id==='repair-7'));
  assert.equal(updates[1].current_graph_report.job_id,'current-8');
  assert.equal(appliedUpdateSummary(updates[1]).fileCount,2);
});

test('failed or unfinished Apply never displays a success confirmation', async () => {
  const updates = [];
  assert.equal(appliedUpdateSummary(report),null);
  assert.equal(appliedUpdateSummary({...report,application:{status:'prepared'}}),null);
  await assert.rejects(applyReviewedUpdate(report, {
    request:async()=>{throw new Error('Working files changed');},
    isCurrent:()=>true,onApplied:value=>updates.push(value),
  }),/Working files changed/);
  assert.equal(updates.length,0);
});

test('successful Apply remains confirmed if fetching the refreshed result fails', async () => {
  const updates = [];
  await assert.rejects(applyReviewedUpdate(report, {
    request:async(url,options)=>{if(options?.method==='POST')return application;throw new Error('Disconnected');},
    isCurrent:()=>true,onApplied:value=>updates.push(value),
  }),/applied successfully.*refresh/i);
  assert.equal(appliedUpdateSummary(updates[0]).title,'Changes applied successfully');
});

test('changing selection during Apply does not replace another result', async () => {
  const updates = [];
  await applyReviewedUpdate(report, {request:async()=>application,isCurrent:()=>false,onApplied:value=>updates.push(value)});
  assert.equal(updates.length,0);
});

test('a poll started before Apply cannot erase its persisted success confirmation', () => {
  const applied = {...report, application};
  assert.equal(refreshedJobReport(applied,report),applied);
  const fresh = {...applied,current_graph_report:{job_id:'current-9'}};
  assert.equal(refreshedJobReport(applied,fresh),fresh);
  const other = {...report,job_id:'different'};
  assert.equal(refreshedJobReport(applied,other),other);
});
