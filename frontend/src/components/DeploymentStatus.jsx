import { useEffect, useRef, useState } from 'react';
import { GitPullRequest, CheckCircle2, AlertCircle, Clock3, ArrowUpRight } from 'lucide-react';
import { requestJSON } from '../workspace';
import { workflowPresentation } from '../project-workflow';
import './project-workflow.css';

export default function DeploymentStatus({workflow: supplied, integration, jobId, onOpenJob, onRefresh}) {
  const [record,setRecord]=useState(null),[error,setError]=useState(''),[busy,setBusy]=useState(false),[preview,setPreview]=useState(null);
  const log=useRef(null), follow=useRef(true);
  useEffect(()=>{
    if(supplied || !integration)return;
    let live=true,timer;
    async function load(){try{const value=await requestJSON(`/api/projects/${encodeURIComponent(integration)}/workflows`);if(live)setRecord(value.workflows.find(w=>w.job_id===jobId)||null);}catch{/* Existing single-provider runs have no project workflow. */}if(live)timer=setTimeout(load,4000);}
    load();return()=>{live=false;clearTimeout(timer);};
  },[supplied,integration,jobId]);
  const workflow=supplied || record;
  useEffect(()=>{if(log.current && follow.current)log.current.scrollTop=log.current.scrollHeight;},[workflow?.events?.length]);
  if(!workflow)return null;
  const view=workflowPresentation(workflow), Icon=view.tone==='success'?CheckCircle2:view.tone==='danger'?AlertCircle:Clock3;
  async function action(name){setBusy(true);setError('');try{await requestJSON(`/api/projects/${workflow.project_id}/workflows/${workflow.workflow_id}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:name})});onRefresh?.();}catch(e){setError(e.message);}finally{setBusy(false);}}
  async function showPreview(){setError('');try{const value=await requestJSON(`/api/proposals/${workflow.publication_id}`);setPreview(value);}catch(e){setError(e.message);}}
  return <section className={`deployment-status deployment-${view.tone}`} aria-label="Update and deployment status">
    <header><Icon size={24}/><div><h3>{view.label}</h3><p>{workflow.state==='verified'?'The merged client is running and its booking smoke test passed.':workflow.state==='pr_open'?'A person must review and merge the GitHub PR before deployment.':'Follow this update from the provider change to the running client.'}</p></div></header>
    <dl className="deployment-revisions"><div><dt>Client source</dt><dd><code>{workflow.source_sha?.slice(0,12)}</code></dd></div><div><dt>Providers</dt><dd>{Object.keys(workflow.providers).join(' + ')}</dd></div>{workflow.merge_sha&&<div><dt>Merged revision</dt><dd><code>{workflow.merge_sha.slice(0,12)}</code></dd></div>}{workflow.deployed_sha&&<div><dt>Running revision</dt><dd><code>{workflow.deployed_sha.slice(0,12)}</code></dd></div>}</dl>
    {(error||workflow.error)&&<p className="project-error" role="alert">{error||workflow.error}</p>}
    <div className="project-actions">
      {workflow.state==='awaiting_request'&&<button className="primary-button" disabled={busy} onClick={()=>action('generate')}>Ask AI to Update</button>}
      {workflow.state==='failed'&&<button className="secondary-button" disabled={busy} onClick={()=>action('retry')}>Retry with current evidence</button>}
      {workflow.job_id&&onOpenJob&&<button className="secondary-button" onClick={()=>onOpenJob(workflow.job_id)}>View agent activity</button>}
      {workflow.state==='awaiting_publication'&&<button className="primary-button" disabled={busy} onClick={()=>action('prepare')}>Prepare draft preview</button>}
      {workflow.state==='ready'&&<><button className="secondary-button" onClick={showPreview}>View draft preview</button><button className="primary-button" disabled={busy} onClick={()=>action('publish')}>Publish GitHub PR<GitPullRequest size={16}/></button></>}
      {workflow.pr_url&&<a className="secondary-button" href={workflow.pr_url} target="_blank" rel="noreferrer">Review on GitHub<ArrowUpRight size={16}/></a>}
    </div>
    {preview&&<details open className="project-preview"><summary>Proposed GitHub draft</summary><h4>{preview.title}</h4><pre>{preview.body}</pre></details>}
    {!!workflow.events?.length&&<details className="workflow-event-details"><summary>Publication and deployment events</summary><ol ref={log} onScroll={e=>{follow.current=e.currentTarget.scrollHeight-e.currentTarget.scrollTop-e.currentTarget.clientHeight<35;}}>{workflow.events.map((event,index)=><li key={index}><time>{new Date(event.time).toLocaleTimeString()}</time><span>{event.message}</span></li>)}</ol></details>}
  </section>;
}
