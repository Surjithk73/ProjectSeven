import { projectDisplayName } from './workspace.js';

export function localDraftPreview(report, patch) {
  if (report.operation !== 'repair' || report.status !== 'validated') throw new Error('A validated update is required to prepare a draft.');
  if (typeof patch !== 'string' || !patch.trim()) throw new Error('The retained patch is unavailable. Reload the patch and try again.');
  const files = Object.keys(report.applied_files || {});
  if (!files.length) {
    for (const line of patch.split('\n')) if (line.startsWith('+++ b/')) files.push(line.slice(6));
  }
  const title = `[APIShield] Update ${projectDisplayName(report.integration) || 'API integration'} for API changes`;
  const operations = [...new Set((report.impacted_sites || []).map(site=>`${site.method} ${site.endpoint}`))];
  const body = [
    '## Summary',
    'Apply the validated API migration update and retain its recorded validation evidence.',
    '', '## Changed files', ...files.map(file=>`- \`${file}\``),
    ...(operations.length ? ['', '## Affected API operations', ...operations.map(operation=>`- \`${operation}\``)] : []),
    '', '## Validation', 'Recorded local validation: passed.',
    'GitHub publication checks have not run for this local preview. They run separately when preparing a connected GitHub draft.',
    '', '## Provenance', `APIShield result: \`${report.job_id}\``,
    ...(report.source_commit ? [`Analyzed commit: \`${report.source_commit}\``] : []),
    ...(report.patch_sha256 ? [`Patch SHA-256: \`${report.patch_sha256}\``] : []),
    '', 'Prepared locally. No branch, commit, or pull request has been created by this preview.',
  ].join('\n');
  return {title,body,files:[...new Set(files)],patch,sourceCommit:report.source_commit || null};
}

const post = (body) => ({method:'POST',headers:{'Content-Type':'application/json'},...(body ? {body:JSON.stringify(body)} : {})});

export function proposalRequest(action, {jobId,revision} = {}) {
  return post(action === 'prepare' ? {job_id:jobId,expected_revision:revision} : action === 'publish' ? {expected_revision:revision} : null);
}
export function targetDraft(state) {
  return {repository:state.repository || '',base:state.base || 'main',expected_revision:state.revision};
}
export function targetRequest(draft) {
  return {...post(draft),method:'PUT'};
}
export function proposalPresentation(state) {
  const labels={preparing:'Revalidating repair',ready:'Ready for review',publishing:'Creating draft',reconciling:'Checking GitHub',reconciliation_needed:'GitHub outcome needs checking',published:'Draft published',stale:'Preview is outdated',failed:'Preparation failed',cancelled:'Preparation cancelled'};
  return {label:labels[state?.status] || 'Not prepared',publishable:state?.status === 'ready',busy:['preparing','publishing','reconciling'].includes(state?.status),reconcilable:state?.status==='reconciliation_needed' || (['stale','failed','cancelled'].includes(state?.status) && Boolean(state?.effects?.length))};
}
export function publicationDetails(state) {
  return state?.publication ? {head:state.branch,commit:state.publication.commit,state:state.publication.state,draft:state.publication.draft} : null;
}
