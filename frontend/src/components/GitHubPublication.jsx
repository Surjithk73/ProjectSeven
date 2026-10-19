import {useEffect,useRef,useState} from 'react';
import {GitPullRequest,ExternalLink,Download} from 'lucide-react';
import {requestJSON} from '../workspace';
import RepairDiff from './RepairDiff';
import {proposalPresentation,proposalRequest,targetDraft,targetRequest,publicationDetails,localDraftPreview} from '../publication';
import './github-preview.css';

export function GitHubTarget({integration}) {
  const [state,setState]=useState(null),[draft,setDraft]=useState(null),[pending,setPending]=useState(false),[error,setError]=useState('');
  const url=`/api/integrations/${encodeURIComponent(integration)}/github`;
  useEffect(()=>{
    let current=true;
    requestJSON(url).then(value=>{if(current){setState(value);setDraft(targetDraft(value));}}).catch(e=>{if(current)setError(e.message);});
    return ()=>{current=false;};
  },[url]);
  async function save(event) {
    event.preventDefault();if(pending)return;setPending(true);setError('');
    try {const value=await requestJSON(url,targetRequest(draft));setState(value);setDraft(targetDraft(value));}
    catch(e){setError(e.message);}finally{setPending(false);}
  }
  return <section className="github-target">
    <div className="section-heading"><h2>GitHub drafts</h2><GitPullRequest size={20}/></div>
    <p className="muted">Use this computer’s GitHub CLI sign-in. Connect the repository and branch that match your repair’s source commit.</p>
    {state?.configured && <p>Connected as <strong>{state.account.login}</strong> · {state.repository} / {state.base}</p>}
    {draft && <form onSubmit={save} className="github-target-form"><label>Repository<input required placeholder="owner/repository" value={draft.repository} disabled={pending} onChange={e=>setDraft({...draft,repository:e.target.value})}/></label><label>Base branch<input required value={draft.base} disabled={pending} onChange={e=>setDraft({...draft,base:e.target.value})}/></label><button className="secondary-button" disabled={pending}>{pending?'Checking access…':'Check and save target'}</button></form>}
    {error && <p className="form-error" role="alert">{error}</p>}
  </section>;
}

export default function GitHubPublication({integration,jobId,report,onConnect}) {
  const [proposal,setProposal]=useState(null),[pending,setPending]=useState(false),[error,setError]=useState('');
  const [preview,setPreview]=useState(null),[connected,setConnected]=useState(false);
  const submitting=useRef(false);
  const storageKey=`apishield-proposal:${integration}:${jobId}`;
  useEffect(()=>{
    let current=true;
    let id;
    try { id=localStorage.getItem(storageKey); } catch { /* Storage is optional. */ }
    if(id)requestJSON(`/api/proposals/${id}`).then(value=>{if(current)setProposal(value);}).catch(e=>{if(current)setError(e.message);});
    return ()=>{current=false;};
  },[storageKey]);
  const view=proposalPresentation(proposal);
  const published=publicationDetails(proposal);
  useEffect(()=>{
    if(!view.busy || !proposal?.id)return;
    let current=true;
    const timer=setInterval(()=>requestJSON(`/api/proposals/${proposal.id}`).then(value=>{if(current)setProposal(value);}).catch(e=>{if(current)setError(e.message);}),1500);
    return ()=>{current=false;clearInterval(timer);};
  },[proposal?.id,view.busy]);
  async function act(action) {
    if(submitting.current)return;submitting.current=true;setPending(true);setError('');
    try {
      let url,options;
      if(action==='prepare') {
        const evidence=report || await requestJSON(`/api/jobs/${jobId}`);
        const response=await fetch(`/api/jobs/${jobId}/patch`);
        if(!response.ok)throw new Error('The retained patch is unavailable. Reload the patch and try again.');
        setPreview(localDraftPreview(evidence,await response.text()));
        const target=await requestJSON(`/api/integrations/${encodeURIComponent(integration)}/github`);
        setConnected(Boolean(target.configured));
        if(!target.configured)return;
        url=`/api/integrations/${encodeURIComponent(integration)}/proposals`;
        options=proposalRequest(action,{jobId,revision:target.revision});
      } else {url=`/api/proposals/${proposal.id}/${action}`;options=proposalRequest(action,{revision:proposal.revision});}
      const value=await requestJSON(url,options);setProposal(value);
      try { localStorage.setItem(storageKey,value.id); } catch { /* The result remains available without browser storage. */ }
    }catch(e){setError(e.message);}finally{submitting.current=false;setPending(false);}
  }
  function downloadPreview() {
    const contents=`# ${preview.title}\n\n${preview.body}\n\n## Patch\n\n\`\`\`diff\n${preview.patch}\n\`\`\`\n`;
    const url=URL.createObjectURL(new Blob([contents],{type:'text/markdown;charset=utf-8'}));
    const link=document.createElement('a');link.href=url;link.download=`apishield-${jobId}-draft.md`;link.click();URL.revokeObjectURL(url);
  }
  return <section className="github-publication">
    <div className="section-heading"><h3>Review a GitHub draft</h3><span className="muted">{preview && !proposal?.prepared && !view.busy ? 'Local draft ready' : view.label}</span></div>
    <p className="muted">Preview the proposed pull request without connecting GitHub. Connected preparation rechecks the complete patch and reruns validation before you can create a draft PR.</p>
    {preview && !proposal?.prepared && <div className="github-local-preview">
      <div className="github-preview-heading"><GitPullRequest size={22}/><div><h4>{preview.title}</h4><p>Local preview · Not published to GitHub</p></div></div>
      <h4>Draft description</h4><pre className="github-draft-description">{preview.body}</pre>
      <details><summary>Review patch · {preview.files.length} changed {preview.files.length===1?'file':'files'}</summary><ul>{preview.files.map(file=><li key={file}><code>{file}</code></li>)}</ul><RepairDiff patch={preview.patch}/></details>
    </div>}
    {proposal?.prepared && <>
      <p>{proposal.target.repository} · {proposal.target.base} · <code>{proposal.source_commit.slice(0,12)}</code></p>
      <p><strong>{proposal.prepared.files.length} source files</strong> · Local validation passed · GitHub CI: not verified</p>
      <details><summary>Complete patch and changed files</summary><ul>{proposal.prepared.files.map(file=><li key={file.path}><code>{file.path}</code></li>)}</ul><RepairDiff patch={proposal.prepared.patch} /></details>
      <h4>Proposed title</h4><p>{proposal.title}</p><details><summary>Exact draft description</summary><pre className="patch-preview">{proposal.body}</pre></details>
    </>}
    {(error || proposal?.error) && <p className="form-error" role="alert">{error || proposal.error}</p>}
    {published && <dl className="source-facts"><dt>Head branch</dt><dd>{published.head}</dd><dt>Published commit</dt><dd>{published.commit}</dd><dt>GitHub state at publication</dt><dd>{published.state} · {published.draft?'draft':'not a draft'}</dd></dl>}
    <div className="report-actions">
      {!view.busy && proposal?.status!=='published' && !view.reconcilable && <button className="secondary-button" disabled={pending} onClick={()=>act('prepare')}>{pending?'Preparing…':'Prepare draft preview'}</button>}
      {preview && <button className="secondary-button" onClick={downloadPreview}><Download size={17}/>Download draft</button>}
      {preview && !connected && !proposal?.prepared && onConnect && <button className="primary-button" disabled={pending} onClick={onConnect}><GitPullRequest size={17}/>Connect GitHub to continue</button>}
      {view.publishable && <button className="primary-button" disabled={pending} onClick={()=>act('publish')}><GitPullRequest size={17}/>Create draft PR</button>}
      {proposal?.status==='preparing' && <button className="secondary-button" disabled={pending} onClick={()=>act('cancel')}>Cancel preparation</button>}
      {view.reconcilable && <button className="secondary-button" disabled={pending} onClick={()=>act('reconcile')}>Check GitHub outcome</button>}
      {proposal?.publication && <a className="secondary-button" href={proposal.publication.url} target="_blank" rel="noreferrer"><ExternalLink size={17}/>Open draft PR</a>}
    </div>
  </section>;
}
