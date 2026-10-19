const definitions = [
  ['prepare', 'Prepare workspace', 'Capture current code and API documents.'],
  ['analyze', 'Analyze API impact', 'Compare contracts and trace affected functions.'],
  ['intent', 'Infer behavior', 'Generate checks and verify they expose the break.'],
  ['repair', 'Generate update', 'Create and stage a candidate in the temporary copy.'],
  ['validate', 'Run validation', 'Execute repository tests and behavioral checks.'],
  ['review', 'Review changes', 'The tested proposal waits for your review.'],
  ['apply', 'Apply changes', 'Update working files only after you choose Apply.'],
];

export function nearLogEnd(element) {
  return element.scrollHeight - element.scrollTop - element.clientHeight < 48;
}

export function activityState(report, events = [], now = Date.now()) {
  const stages = definitions.map(([id, label, description]) => ({id,label,description,state:'pending',detail:description}));
  let current = null, attempt = 0;
  for (const event of events) {
    if (event.kind !== 'activity') continue;
    const stage = stages.find(s => s.id === event.stage);
    if (!stage) continue;
    if (current && current !== stage && current.state === 'running') current.state = 'completed';
    if (stage.id === 'repair' && current?.id === 'validate') stages.find(s => s.id === 'validate').state = 'pending';
    stage.state = event.status || 'running';
    stage.detail = event.message || stage.description;
    stage.startedAt = event.time;
    current = stage;
    attempt = Math.max(attempt, event.attempt || 0);
  }
  const terminal = !['queued','running'].includes(report.status);
  if (report.status === 'validated') {
    if (current?.state === 'running') current.state = 'completed';
    current = stages.find(s => s.id === 'review'); current.state = 'waiting';
  } else if (terminal && current) {
    current.state = report.status === 'cancelled' ? 'cancelled' : report.status === 'needs_input' ? 'blocked' : report.status === 'failed' ? 'failed' : 'completed';
    if (report.error) current.detail = report.failure_explanation?.summary || report.error;
  }
  if (report.application?.status === 'applied') {
    stages.find(s => s.id === 'review').state = 'completed';
    current = stages.find(s => s.id === 'apply'); current.state = 'completed';
    current.detail = 'The reviewed repair has been applied to working files.';
  }
  const end = terminal ? Date.parse(report.finished_at || events.findLast(e => e.kind === 'job_finished')?.time) : now;
  const start = Date.parse(report.created_at);
  return {stages,current,attempt,terminal,elapsed:Number.isFinite(start) && Number.isFinite(end) ? Math.max(0,(end-start)/1000) : null};
}

export function eventDescription(event) {
  if (event.message) return event.message;
  if (event.kind === 'command_started') return `Running ${event.label}`;
  if (event.kind === 'command_finished') return `${event.label}: ${event.timed_out ? 'timed out' : event.cancelled ? 'cancelled' : `exit ${event.exit_code}`}`;
  if (event.kind === 'attempt_finished') return `Attempt ${event.number}: ${event.status}${event.error ? ` · ${event.error}` : ''}`;
  if (event.kind === 'model_usage') return `Model response received · ${event.elapsed_seconds}s`;
  if (event.kind === 'scan_finished') return `Found ${event.sites} API call sites`;
  if (event.kind === 'comparison_finished') return `${event.changed_operations?.length || 0} API operations changed`;
  if (event.kind === 'job_finished') return `Run finished: ${event.status}`;
  return event.kind?.replaceAll('_',' ') || 'Execution event';
}
