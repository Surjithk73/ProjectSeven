import { useState } from 'react';
import { CircleCheck, Clock3, Radio, CircleAlert, ArrowUpRight } from 'lucide-react';
import { integrationSnapshot, loadCheckPreview, saveCheckPreview } from '../dashboard-details';
import './integration-snapshot.css';

const checkedTime = value => value && Number.isFinite(Date.parse(value))
  ? new Date(value).toLocaleString(undefined,{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}) : 'Not checked yet';

export default function IntegrationSnapshot({integration,report,jobs,onEndpoints,onGraph}) {
  const snapshot = integrationSnapshot(integration,report,jobs);
  const [preview,setPreview] = useState(()=>loadCheckPreview(integration));
  function updatePreview(change) {
    const next = {...preview,...change};
    setPreview(next);
    saveCheckPreview(integration,next);
  }
  const success = snapshot.monitoring === 'Successful';
  const attention = snapshot.monitoring === 'Needs attention';
  const Icon = success ? CircleCheck : attention ? CircleAlert : Clock3;
  return <section className="integration-snapshot" aria-labelledby="integration-snapshot-title">
    <h3 id="integration-snapshot-title">Integration snapshot</h3>
    <dl className="integration-snapshot-values">
      <div><dt>Accepted API version</dt><dd>{snapshot.version || 'Not recorded'}</dd></div>
      <div><dt>API endpoints in use</dt><dd><button onClick={onEndpoints}>{snapshot.endpoints ?? 'Not scanned'}<ArrowUpRight size={16} aria-hidden="true" /></button></dd></div>
      <div><dt>Consumer source files</dt><dd><button onClick={onGraph}>{snapshot.files ?? 'Not scanned'}<ArrowUpRight size={16} aria-hidden="true" /></button></dd></div>
      <div><dt>Last API check</dt><dd className="snapshot-time">{checkedTime(snapshot.lastChecked)}</dd></div>
    </dl>
    <div className="snapshot-monitoring">
      <div className={`snapshot-monitor-status ${success ? 'is-successful' : attention ? 'needs-attention' : ''}`}>
        <Icon size={28} aria-hidden="true" />
        <div><span>Monitoring status</span><strong>{snapshot.monitoring}</strong><p>{snapshot.checkOutcome}</p></div>
      </div>
      <div className="snapshot-automatic">
        <div className="snapshot-automatic-controls">
          <Radio size={20} aria-hidden="true" />
          <label className="snapshot-toggle"><span>Automatic checks</span><input type="checkbox" role="switch" checked={preview.enabled} onChange={event=>updatePreview({enabled:event.target.checked})} /><span className="snapshot-switch-track" aria-hidden="true" /></label>
          <select aria-label="Automatic check interval preview" disabled={!preview.enabled} value={preview.interval} onChange={event=>updatePreview({interval:Number(event.target.value)})}>
            <option value={15}>Every 15 minutes</option><option value={60}>Every hour</option><option value={360}>Every 6 hours</option><option value={1440}>Every day</option>
          </select>
        </div>
      </div>
    </div>
  </section>;
}
