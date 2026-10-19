import { GitCompareArrows, Sparkles, Check } from 'lucide-react';
import { changeNotice } from '../overview-view';
import './change-notice.css';

export default function ChangeNotice({ report, modelAvailable, onAskAI }) {
  const notice = changeNotice(report);
  if (!notice) return null;
  const changed = notice.changes.length > 0;
  const Icon = changed ? GitCompareArrows : Check;
  return <section className={`change-notice ${changed ? 'has-changes' : 'no-changes'}`} aria-label="API change summary">
    <div className="change-notice-main"><span className="change-notice-icon"><Icon size={23} /></span><div><h3>{notice.title}</h3><p>{changed ? `${notice.changes.length} endpoint changes · ${notice.affected} affected source calls` : 'The observed API matches the accepted contract.'}</p></div>
      {notice.canAskAI && onAskAI && <button className="primary-button" disabled={!modelAvailable} onClick={onAskAI}><Sparkles size={19} />Ask AI to update</button>}
    </div>
    {changed && <div className="change-notice-details"><div className="change-counts">{Object.entries(notice.counts).filter(([,count])=>count).map(([kind,count])=><span className={`change-count-${kind}`} key={kind}>{count} {kind}</span>)}</div><ul>{notice.changes.slice(0,6).map(change=><li key={`${change.method}:${change.endpoint}`}><code>{change.method} {change.endpoint}</code><span className={`change-count-${change.status}`}>{change.status}</span></li>)}</ul>{notice.changes.length > 6 && <p>{notice.changes.length - 6} more changes in the endpoint comparison below.</p>}{notice.affected === 0 && <p>No affected supported source calls were localized. Review the endpoints and coverage notes.</p>}{notice.canAskAI && !modelAvailable && <p>Connect Google Cloud under Settings → AI connection to request an update.</p>}</div>}
  </section>;
}
