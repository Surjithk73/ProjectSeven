import test from 'node:test';
import assert from 'node:assert/strict';
import { activityState, nearLogEnd } from '../src/agent-activity.js';

test('progress follows real events and retries return from validation to repair', () => {
  const events = [
    {kind:'activity',stage:'prepare',time:'2026-10-15T00:00:00Z'},
    {kind:'activity',stage:'analyze',time:'2026-10-15T00:00:02Z'},
    {kind:'activity',stage:'repair',message:'Generating patch',attempt:1,time:'2026-10-15T00:00:04Z'},
    {kind:'activity',stage:'validate',time:'2026-10-15T00:00:08Z'},
    {kind:'activity',stage:'repair',message:'Retrying with test feedback',attempt:2,time:'2026-10-15T00:00:12Z'},
  ];
  const state = activityState({status:'running',created_at:'2026-10-15T00:00:00Z'},events,Date.parse('2026-10-15T00:00:15Z'));
  assert.equal(state.current.id,'repair');
  assert.equal(state.current.detail,'Retrying with test feedback');
  assert.equal(state.attempt,2);
  assert.equal(state.elapsed,15);
  assert.equal(state.stages.find(s=>s.id==='validate').state,'pending');
  assert.equal(state.stages.find(s=>s.id==='intent').state,'pending');
});
test('validation waits for user apply and failures never mark later steps completed', () => {
  const events=[{kind:'activity',stage:'validate',time:'2026-10-15T00:00:00Z'}];
  const failed=activityState({status:'failed',error:'Tests failed'},events);
  assert.equal(failed.current.state,'failed');
  assert.equal(failed.stages.find(s=>s.id==='apply').state,'pending');
  const validated=activityState({status:'validated'},events);
  assert.equal(validated.current.id,'review');
  assert.equal(validated.current.state,'waiting');
  const applied=activityState({status:'validated',application:{status:'applied'}},events);
  assert.equal(applied.current.id,'apply');
  assert.equal(applied.current.state,'completed');
});
test('old runs without phase evidence do not invent completed stages', () => {
  const value=activityState({status:'running'},[]);
  assert.equal(value.current,null);
  assert.ok(value.stages.every(s=>s.state==='pending'));
});

test('log follows appended entries only while the reader stays near the bottom', () => {
  assert.equal(nearLogEnd({scrollHeight:1000,scrollTop:490,clientHeight:500}),true);
  assert.equal(nearLogEnd({scrollHeight:1000,scrollTop:100,clientHeight:500}),false);
});

test('provider failure shows its explanation instead of raw SDK JSON in the current stage', () => {
  const state = activityState({status:'failed',error:"ServerError: 504 {'error': 'private diagnostic'}",
    failure_explanation:{summary:'Google could not finish behavior inference.'}},
    [{kind:'activity',stage:'intent'}]);
  assert.equal(state.current.detail,'Google could not finish behavior inference.');
});
