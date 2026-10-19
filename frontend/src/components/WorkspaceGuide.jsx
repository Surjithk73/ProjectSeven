import { useEffect, useLayoutEffect, useRef } from "react";
import { observeSelectedTab } from "../workspace_flow";
import {
  ArrowRight,
  BookOpen,
  GitCompareArrows,
  ShieldCheck,
  Network,
  Code2,
  FlaskConical,
  Settings2,
  GitPullRequest,
  FileText,
  Activity,
} from "lucide-react";

export function SectionTabs({ label, tabs, value, onChange }) {
  const list = useRef(null);
  useEffect(() => observeSelectedTab(list.current), [value]);
  useLayoutEffect(() => {
    const container = list.current;
    const update = () => {
      const selected = container.querySelector('[aria-selected="true"]');
      if (!selected) return;
      container.style.setProperty("--tab-left", `${selected.offsetLeft}px`);
      container.style.setProperty("--tab-width", `${selected.offsetWidth}px`);
    };
    update();
    const observer = new ResizeObserver(update);
    observer.observe(container);
    return () => observer.disconnect();
  }, [value, tabs]);
  function navigate(event, index) {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    const keys = {
      ArrowRight: (index + 1) % tabs.length,
      ArrowLeft: (index + tabs.length - 1) % tabs.length,
      Home: 0,
      End: tabs.length - 1,
    };
    if (!(event.key in keys)) return;
    event.preventDefault();
    const next = keys[event.key];
    onChange(tabs[next][0]);
    event.currentTarget.parentElement
      .querySelectorAll('[role="tab"]')
      [next].focus();
  }
  return (
    <div ref={list} className="section-tabs" role="tablist" aria-label={label}>
      {tabs.map(([key, text], index) => (
        <button
          key={key}
          type="button"
          role="tab"
          id={`tab-${key}`}
          aria-selected={value === key}
          aria-controls={`panel-${key}`}
          tabIndex={value === key ? 0 : -1}
          onClick={() => onChange(key)}
          onKeyDown={(event) => navigate(event, index)}
        >
          {(() => {
            const Icon = {
              summary: FileText,
              activity: Activity,
              graph: Network,
              patch: Code2,
              checks: FlaskConical,
              publish: GitPullRequest,
              technical: Settings2,
            }[key];
            return Icon ? <Icon size={17} aria-hidden="true" /> : null;
          })()}
          {text}
        </button>
      ))}
    </div>
  );
}

export default function WorkspaceGuide({
  onExample,
  onConnect,
  onWorkspace,
  busy,
}) {
  return (
    <div className="usage-guide">
      <section className="guide-intro">
        <BookOpen size={28} aria-hidden="true" />
        <h2>Start with one API change.</h2>
        <p>
          APIShield helps you find what an API update might break in your Python
          application, test a proposed fix, and review it before accepting it.
        </p>
        <div className="button-group">
          <button
            className="primary-button"
            onClick={onExample}
            disabled={busy}
          >
            Try the free example <ArrowRight size={17} />
          </button>
          <button className="secondary-button" onClick={onConnect}>
            Connect my project
          </button>
        </div>
        <p className="muted">
          The example uses a supplied repair and real tests. It makes no paid AI
          request.
        </p>
      </section>
      <ol className="guide-steps">
        <li>
          <div>
            <h3>Connect your project</h3>
            <p>
              Choose a committed local Python repository, its test folder, and
              the old and new API contracts. These contracts are JSON OpenAPI
              files describing the API.
            </p>
          </div>
        </li>
        <li>
          <div>
            <h3>Check what changed</h3>
            <p>
              Choose <strong>Check API changes</strong>. APIShield compares the
              contracts and identifies supported calls that may be affected.
              This does not make an AI request.
            </p>
          </div>
        </li>
        <li>
          <div>
            <h3>Test a proposed repair</h3>
            <p>
              Choose <strong>Generate AI repair</strong> when you are ready.
              Gemini receives the selected code and contracts; provider charges
              apply. Tests run on a temporary copy.
            </p>
          </div>
        </li>
        <li>
          <div>
            <h3>Review and accept</h3>
            <p>
              Open the result, inspect the patch and test evidence, then
              download the patch or explicitly create a GitHub draft PR. You
              decide whether to apply or merge it.
            </p>
          </div>
        </li>
      </ol>
      <section className="guide-reference">
        <h2>A few useful terms</h2>
        <dl>
          <dt>API contract</dt>
          <dd>
            A JSON OpenAPI file describing endpoints, inputs and responses. It
            is not just a link to an ordinary documentation page.
          </dd>
          <dt>Scan</dt>
          <dd>Find supported API calls in your committed code.</dd>
          <dt>Comparison</dt>
          <dd>
            Identify differences between two API contracts and the calls they
            could affect.
          </dd>
          <dt>Validated repair</dt>
          <dd>
            A proposed patch that passed your configured tests. It still needs
            your review.
          </dd>
          <dt>Draft PR</dt>
          <dd>
            A proposed GitHub change waiting for review. APIShield does not
            merge it.
          </dd>
        </dl>
      </section>
      <section className="guide-reference">
        <h2>Optional tools, when you need them</h2>
        <p>
          <GitCompareArrows size={17} /> <strong>Monitoring</strong> checks an
          API contract URL on a schedule while this app is running. It does not
          automatically request AI repairs.
        </p>
        <p>
          <ShieldCheck size={17} /> <strong>Business rules</strong> describe
          behavior a repair must preserve, such as the exact payment amount.
          Link tests that check those rules.
        </p>
        <p>
          Both are in <strong>Settings → Project settings</strong>. Google
          credentials are in <strong>Settings → AI connection</strong> and must
          be selected again after restarting.
        </p>
        <button className="secondary-button" onClick={onWorkspace}>
          Return to workspace <ArrowRight size={17} />
        </button>
        <details className="legacy-demo-link">
          <summary>Advanced: payment demonstration</summary>
          <p>
            The older payment demo is separate from your connected projects.
          </p>
          <a href="/demo">Open payment demo</a>
        </details>
      </section>
    </div>
  );
}
