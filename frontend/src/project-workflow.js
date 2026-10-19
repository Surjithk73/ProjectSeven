export function workflowPresentation(workflow) {
  const labels={awaiting_request:'API changes detected',generating:'AI update in progress',validating:'Running validation',awaiting_publication:'Update validated',preparing:'Preparing draft preview',ready:'Draft ready to publish',pr_open:'Awaiting human review',awaiting_ci:'Waiting for merged-revision CI',merged:'Merged · awaiting deployment',deploying:'Deploying client',verified:'Deployed and verified',failed:'Update needs attention',ci_failed:'Merged client CI failed',superseded:'Replaced by a newer analysis',closed:'PR closed without merging'};
  return {label:workflow?.state==='reconciling'?'Recovering GitHub publication':labels[workflow?.state] || 'No migration in progress',tone:workflow?.state==='verified'?'success':['failed','ci_failed'].includes(workflow?.state)?'danger':'pending'};
}
export function providerHealth(state) {
  if(state.error)return {label:'Connection needs attention',tone:'danger'};
  if(!state.configured)return {label:'Not configured',tone:'pending'};
  if(state.active_check)return {label:'Checking contract',tone:'pending'};
  if(state.last_observation_hash && state.baseline_hash!==state.last_observation_hash)return {label:'API change detected',tone:'attention'};
  if(state.last_success)return {label:'Up to date',tone:'success'};
  return {label:'Waiting for first check',tone:'pending'};
}
export function endpointIdentity(endpoint='') {
  const match=endpoint.match(/^\/__provider__\/([^/]+)(\/.*)$/);
  return match?{provider:match[1],path:match[2]}:{provider:'',path:endpoint};
}
export function filterProviderGraph(graph, provider) {
  if(provider==='all')return graph;
  const nodes=graph.nodes.filter(n=>!n.provider_id||n.provider_id===provider), ids=new Set(nodes.map(n=>n.id));
  return {...graph,nodes,edges:graph.edges.filter(e=>ids.has(e.from)&&ids.has(e.to))};
}
