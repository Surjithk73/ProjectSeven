import { orderedJobs } from './workspace.js';

const endpointCount = sites => new Set(sites.map(site => `${site.method}:${site.endpoint}`)).size;
const countText = (count, noun) => `${count} ${noun}${count === 1 ? '' : 's'}`;

export function activityOutcome(job) {
  if (job.application?.status === 'applied') return `Update applied${job.application.files ? ` · ${countText(job.application.files.length,'file')}` : ''}`;
  if (['queued','running'].includes(job.status)) return job.operation === 'repair' ? 'AI update in progress' : 'Check in progress';
  if (job.status === 'failed') return job.operation === 'repair' ? 'Update could not complete' : 'Check could not complete';
  if (job.status === 'cancelled') return 'Run cancelled';
  if (job.status === 'needs_input') return 'Your input is needed';
  if (job.operation === 'repair' && job.status === 'validated') return 'Validation passed · Ready to review';
  if (job.status === 'no_change') return 'No relevant API changes';
  if (job.operation === 'scan' && job.status === 'completed') return job.scan?.sites ? `${countText(endpointCount(job.scan.sites),'endpoint')} discovered` : 'Scan completed';
  if (job.operation === 'compare' && job.status === 'completed') {
    const changes = job.comparison?.changed_operations || job.contract_overview?.changes;
    return changes ? changes.length ? `${countText(changes.length,'endpoint change')} detected` : 'No API changes detected' : 'Comparison completed';
  }
  return 'Recorded execution';
}

export function integrationSnapshot(integration, current, jobs) {
  const recent = orderedJobs(jobs.filter(job => job.integration === integration));
  const evidence = current?.integration === integration ? current : recent.find(job => job.scan && ['completed','validated','no_change'].includes(job.status));
  const check = recent.find(job => job.operation === 'compare');
  const monitoring = !check ? 'Not checked' : ['queued','running'].includes(check.status) ? 'Checking…' : ['completed','no_change'].includes(check.status) ? 'Successful' : check.status === 'cancelled' ? 'Cancelled' : 'Needs attention';
  return {
    version:evidence?.contract_overview?.before?.info?.version || null,
    endpoints:evidence?.scan?.sites ? endpointCount(evidence.scan.sites) : null,
    files:evidence?.scan?.sites ? new Set(evidence.scan.sites.map(site=>site.file).filter(Boolean)).size : null,
    lastChecked:check?.finished_at || check?.created_at || null,
    monitoring, checkOutcome:check ? activityOutcome(check) : 'Run an API check to record its outcome.',
  };
}

const intervals = [15,60,360,1440];
const previewKey = integration => `apishield-check-preview:${integration}`;
export function loadCheckPreview(integration, storage = globalThis.localStorage) {
  try {
    const value = JSON.parse(storage.getItem(previewKey(integration)) || '{}');
    return {enabled:value.enabled === true,interval:intervals.includes(value.interval) ? value.interval : 60};
  } catch { return {enabled:false,interval:60}; }
}
export function saveCheckPreview(integration, value, storage = globalThis.localStorage) {
  try { storage.setItem(previewKey(integration),JSON.stringify({enabled:value.enabled === true,interval:intervals.includes(value.interval) ? value.interval : 60})); }
  catch { /* The preview remains usable when browser storage is unavailable. */ }
}
