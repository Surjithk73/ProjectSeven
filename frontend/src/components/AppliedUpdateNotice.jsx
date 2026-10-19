import { CircleCheck, ArrowRight, Network, ExternalLink } from 'lucide-react';
import './applied-update.css';

export default function AppliedUpdateNotice({ notice, noticeRef, onGraph }) {
  if (!notice) return null;
  return <section className="applied-update-notice" ref={noticeRef} tabIndex={-1} role="status" aria-live="polite" aria-atomic="true">
    <CircleCheck className="applied-update-icon" size={30} aria-hidden="true" />
    <div className="applied-update-copy">
      <h3>{notice.title}</h3>
      <p>{notice.description}</p>
      <p className="applied-update-evidence">{notice.fileCount > 0 && <span>{notice.fileCount} {notice.fileCount === 1 ? 'file' : 'files'} updated</span>}<span>Validation passed</span><span>Recovery copy retained</span></p>
      <div className="applied-update-actions">
        {notice.banking && <a className="primary-button" href="/banking" target="_blank" rel="noopener noreferrer">Open banking app <ExternalLink size={16} /></a>}
        <button className="secondary-button" onClick={onGraph}><Network size={16} />View updated graph <ArrowRight size={16} /></button>
      </div>
    </div>
  </section>;
}
