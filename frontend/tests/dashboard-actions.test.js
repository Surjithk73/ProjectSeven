import test from 'node:test';
import assert from 'node:assert/strict';
import { dashboardActions } from '../src/workspace_flow.js';

test('API check stays primary while relevant unapplied repair is secondary', () => {
  const repair = { job_id:'r', integration:'bank', operation:'repair', status:'validated', source_hash:'a', created_at:'2026-10-14' };
  assert.equal(dashboardActions('bank', [repair], 'a').primary, 'Check for API Changes');
  assert.equal(dashboardActions('bank', [repair], 'a').review.job_id, 'r');
  assert.equal(dashboardActions('bank', [repair], 'b').review, null);
  assert.equal(dashboardActions('other', [repair], 'a').review, null);
  assert.equal(dashboardActions('bank', [{...repair, application:{status:'applied'}}], 'a').review, null);
});

test('review is hidden when the observed contract changes', () => {
  const api_context = {accepted_hash:'v1', observed_hash:'v2', config_fingerprint:'config'};
  const repair = {job_id:'r', integration:'bank', operation:'repair', status:'validated', source_hash:'a', created_at:'2026-10-14', api_context};
  assert.equal(dashboardActions('bank', [repair], 'a', {...api_context, observed_hash:'v1'}).review, null);
});
