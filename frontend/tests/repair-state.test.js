import test from 'node:test';
import assert from 'node:assert/strict';
import { repairPresentation } from '../src/repair-state.js';

test('low judge scores stay low after validation', () => {
  assert.equal(repairPresentation({ agent_status: 'validated', ips_score: 24 }).score, 24);
});
test('missing or invalid evidence remains unavailable', () => {
  for (const score of [null, undefined, '95', 101, -1, NaN]) {
    assert.equal(repairPresentation({ agent_status: 'validated', ips_score: score }).score, null);
  }
});
test('failure never displays successful validation', () => {
  assert.equal(repairPresentation({ agent_status: 'failed', ips_score: 98 }).validated, false);
  assert.equal(repairPresentation({ agent_status: 'pr_opened' }).validated, true);
});
