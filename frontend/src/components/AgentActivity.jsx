import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { Activity, Check, Circle, CircleAlert, Clock3, Pause, RefreshCw, ArrowRight } from 'lucide-react';
import { requestJSON } from '../workspace';
import { activityState, eventDescription, nearLogEnd } from '../agent-activity';
import './agent-activity.css';
import DeploymentStatus from './DeploymentStatus';

const elapsed = seconds => seconds == null ? 'Not recorded' : seconds < 60 ? `${Math.floor(seconds)}s` : `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
const icons = {completed:Check,running:RefreshCw,waiting:Pause,failed:CircleAlert,blocked:CircleAlert,cancelled:Pause,pending:Circle};
const labels = {completed:'Completed',running:'In progress',waiting:'Awaiting review',failed:'Failed',blocked:'Needs input',cancelled:'Cancelled',pending:'Pending'};

export default function AgentActivity({ report, active, onCancel, onReview }) {
  const [record, setRecord] = useState(null);
  const [failure, setFailure] = useState(null);
  const [retry, setRetry] = useState(0);
  const [now, setNow] = useState(Date.now);
  const log = useRef(null);
  const follow = useRef(true);
  const [following, setFollowing] = useState(true);
  const busy = ['queued','running'].includes(report.status);
  useEffect(() => {
    if (!active) return;
    let live = true, timer;
    async function load() {
      let running = busy;
      try {
        const value = await requestJSON(`/api/jobs/${report.job_id}/activity`);
        if (!live) return;
        setRecord(value); setFailure(null);
        running = ['queued','running'].includes(value.status);
      } catch (error) {
        if (live) setFailure({job_id:report.job_id,message:error.message});
      }
      if (live && running) timer = setTimeout(load,2000);
    }
    load();
    return () => { live = false; clearTimeout(timer); };
  }, [report.job_id, report.status, report.application?.status, active, busy, retry]);
  useEffect(() => {
    if (!active || !busy) return;
    const timer = setInterval(() => setNow(Date.now()),1000);
    return () => clearInterval(timer);
  }, [active,busy]);
  const snapshot = record?.job_id === report.job_id ? record : null;
  const events = snapshot?.events || [];
  const effective = {...report,...snapshot,status:busy ? snapshot?.status || report.status : report.status,application:report.application || snapshot?.application};
  const state = activityState(effective,events,now);
  const current = state.current;
  const Icon = current ? icons[current.state] || Circle : Clock3;
  const error = failure?.job_id === report.job_id ? failure.message : '';
  const explanation = snapshot?.failure_explanation || report.failure_explanation;
  useLayoutEffect(() => {
    if (active && log.current && follow.current) log.current.scrollTop = log.current.scrollHeight;
  }, [active,record]);
  return <div className="agent-activity">
    <header className="evidence-title"><Activity size={25} /><div><h3>Agent activity</h3><p>Live execution steps, test output and repair attempts.</p></div></header>
    {report.project_workflow && <DeploymentStatus integration={report.integration} jobId={report.job_id} />}
    <div className="agent-current">
      <span className={`agent-current-icon agent-state-${current?.state || 'pending'}`}><Icon size={25} className={current?.state === 'running' ? 'agent-spinning' : ''} /></span>
      <div className="agent-current-copy" role="status"><strong>{current?.label || (busy ? 'Waiting for execution details' : 'Recorded execution')}</strong><p>{current?.detail || (events.length ? 'This older run has execution logs, but no recorded stage transitions.' : busy ? 'The worker will report its next step here.' : 'No detailed activity was recorded for this run.')}</p></div>
      <div className="agent-timing"><span><Clock3 size={14} />Execution time</span><strong>{elapsed(state.elapsed)}</strong>{state.attempt > 0 && <span>Attempt {state.attempt}</span>}</div>
    </div>
    {error && <div className="agent-error" role="alert">Couldn’t refresh activity: {error} <button className="text-button" onClick={() => setRetry(value => value + 1)}>Retry</button></div>}
    {explanation ? <section className="agent-failure-details" role="alert"><h4>{explanation.title}</h4><p>{explanation.summary}</p><code>{explanation.detail}</code>{explanation.test && <p><strong>Test:</strong> {explanation.test}</p>}{explanation.location && <p><strong>Location:</strong> {explanation.location}</p>}<p>{explanation.consequence}</p><p><strong>Next:</strong> {explanation.next_action}</p></section> : effective.error && <p className="agent-error" role="alert">{effective.error}</p>}
    <div className="agent-workspace">
      <section className="agent-stages" aria-label="Repair stages"><ol>{state.stages.map(stage => {
        const StageIcon = icons[stage.state] || Circle;
        const label = stage.state === 'pending' && stage.id === 'apply' ? 'Not applied' : stage.state === 'pending' && state.terminal ? 'Not recorded' : labels[stage.state];
        return <li key={stage.id} className={`agent-state-${stage.state}`} aria-current={stage === current ? 'step' : undefined}><span className="agent-stage-icon"><StageIcon size={17} className={stage.state === 'running' ? 'agent-spinning' : ''} /></span><div><div className="agent-stage-label"><strong>{stage.label}</strong><span>{label}</span></div><p>{stage === current ? stage.detail : stage.description}</p></div></li>;
      })}</ol></section>
      <section className="agent-events" aria-label="Execution log">
        <div className="agent-log-heading"><h4>Execution log</h4><span>{events.length} events{snapshot?.truncated ? ' · latest retained window' : ''}</span>{!following && <button className="text-button" onClick={() => { follow.current = true; setFollowing(true); if (log.current) log.current.scrollTop = log.current.scrollHeight; }}>Jump to latest</button>}</div>
        {events.length ? <div className="agent-log-list" ref={log} onScroll={event => { follow.current = nearLogEnd(event.currentTarget); setFollowing(follow.current); }}>{events.map((event,index) => <details key={`${event.time}:${index}`} className="agent-log-entry"><summary><time>{event.time ? new Date(event.time).toLocaleTimeString() : '—'}</time><span>{eventDescription(event)}</span></summary><div>{event.stdout || event.stderr ? <pre>{[event.stdout,event.stderr].filter(Boolean).join('\n').slice(0,12000)}</pre> : <p>{event.kind === 'activity' ? 'Reported by the execution worker.' : 'No command output for this event.'}</p>}{event.duration_seconds != null && <p>Duration: {event.duration_seconds.toFixed(2)}s</p>}</div></details>)}</div> : <div className="agent-log-empty"><Clock3 size={22} /><p>{busy ? 'Execution events will appear as the agent works.' : 'This run has no retained execution events.'}</p></div>}
      </section>
    </div>
    <footer className="agent-activity-footer"><p>{effective.application?.status === 'applied' ? 'The reviewed repair is applied to working files.' : 'Candidate edits and tests run in a temporary copy. Working files change only when you apply the repair.'}</p>{busy && <button className="secondary-button" onClick={onCancel}>Cancel run</button>}{report.status === 'validated' && <button className="primary-button" onClick={onReview}>Review code change<ArrowRight size={16} /></button>}</footer>
  </div>;
}
