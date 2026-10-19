import {
  FlaskConical,
  ShieldCheck,
  FileCode2,
  ScanSearch,
  Fingerprint,
  Download,
  CircleCheck,
  CircleMinus,
  CircleAlert,
} from "lucide-react";
import { RequirementRelationships } from "./Requirements";

export function ChecksPanel({ report, commands }) {
  return (
    <div className="validation-workspace">
      <header className="evidence-title">
        <FlaskConical size={24} />
        <div>
          <h3>Tests & business rules</h3>
          <p>
            Repair tests check the proposed code. Rules check what it must
            preserve.
          </p>
        </div>
      </header>
      <div className="validation-columns">
        <section className="test-executions">
          <div className="evidence-section-title">
            <h4>Test executions</h4>
            <span className="evidence-count">{commands.length} recorded</span>
          </div>
          {commands.length ? (
            commands.map((command, index) => {
              const passed =
                command.exit_code === 0 &&
                !command.timed_out &&
                !command.cancelled;
              const label = command.timed_out
                ? "Timed out"
                : command.cancelled
                  ? "Cancelled"
                  : passed
                    ? "Passed"
                    : "Failed";
              const Icon = passed ? CircleCheck : CircleAlert;
              return (
                <details
                  key={index}
                  className={`execution-record execution-${passed ? "passed" : "failed"}`}
                >
                  <summary>
                    <Icon size={18} />
                    <strong>Attempt {command.attempt}</strong>
                    <span className="execution-status">{label}</span>
                    <span className="execution-duration">
                      {typeof command.duration_seconds === "number"
                        ? `${command.duration_seconds.toFixed(1)}s`
                        : "—"}
                    </span>
                  </summary>
                  <pre>
                    {command.stdout || "No standard output."}
                    {command.stderr && `\n${command.stderr}`}
                  </pre>
                  {command.output_limited && (
                    <p>Output was capped by the configured budget.</p>
                  )}
                </details>
              );
            })
          ) : (
            <div className="tests-unrun">
              <CircleMinus size={32} />
              <strong>Tests haven’t run yet</strong>
              <p>
                This {report.operation || "analysis"} run recorded no repair
                tests.
              </p>
              <span>Repair runs show their test output here.</span>
            </div>
          )}
        </section>
        <section className="business-rule-evidence">
          <div className="evidence-section-title">
            <div>
              <ShieldCheck size={19} />
              <h4>AI-inferred intent</h4>
            </div>
            <span className="evidence-count">
              {report.ai_intent?.rules?.length || 0} rules
            </span>
          </div>
          {report.ai_intent?.rules?.length ? (
            report.ai_intent.rules.map((rule) => (
              <article className="requirement-row" key={rule.id}>
                <strong>{rule.description}</strong>
                <p>
                  <code>
                    {rule.file} · {rule.function}
                  </code>
                </p>
                <small>
                  AI-inferred ·{" "}
                  {report.generated_validation?.passed
                    ? "Generated checks passed"
                    : "Not validated"}
                </small>
              </article>
            ))
          ) : (
            <p className="muted">
              Gemini infers intent and missing checks when an API repair is
              requested. No manual rule setup is required.
            </p>
          )}
        </section>
      </div>
      {report.requirement_graph && (
        <details className="evidence-disclosure">
          <summary>
            <FileCode2 size={17} />
            Source → rules → tests
          </summary>
          <RequirementRelationships graph={report.requirement_graph} />
        </details>
      )}
    </div>
  );
}

export function TechnicalPanel({ report, limitations, onDownload }) {
  const records = [
    ["Run ID", report.job_id],
    ["Code commit", report.source_commit || "Not pinned yet"],
    ["Original API fingerprint", report.base_spec_hash || "Not recorded yet"],
    ["Updated API fingerprint", report.target_spec_hash || "Not recorded yet"],
    [
      "Business rules fingerprint",
      report.requirements_hash || "No requirement snapshot in this run",
    ],
  ];
  return (
    <div className="technical-workspace">
      <header className="evidence-title">
        <ScanSearch size={24} />
        <div>
          <h3>Analysis details</h3>
          <p>Coverage notes and the exact snapshots used in this run.</p>
        </div>
      </header>
      <div className="technical-columns">
        <section className="analysis-coverage">
          <div className="evidence-section-title">
            <h4>Coverage & limitations</h4>
            <span className="evidence-count">{limitations.length} notes</span>
          </div>
          {limitations.length ? (
            <ul className="coverage-notes">
              {limitations.map((item, index) => (
                <li key={index}>
                  <CircleAlert size={18} />
                  <div>
                    <p>{typeof item === "string" ? item : item.reason}</p>
                    {item.file && <code>{item.file}</code>}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="coverage-empty">
              No additional coverage notes recorded. Passing tests does not
              establish complete correctness.
            </p>
          )}
          {report.comparison && (
            <details className="evidence-disclosure">
              <summary>
                <FileCode2 size={17} />
                Full API contract diff
              </summary>
              <pre>{JSON.stringify(report.comparison.diff, null, 2)}</pre>
            </details>
          )}
        </section>
        <section className="run-record">
          <div className="evidence-section-title">
            <div>
              <Fingerprint size={19} />
              <h4>Run record</h4>
            </div>
          </div>
          <p className="run-record-help">
            Fingerprints identify the exact input files, so results can be
            traced and reproduced.
          </p>
          <dl>
            {records.map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>
                  <code>{value}</code>
                </dd>
              </div>
            ))}
          </dl>
          <button className="secondary-button" onClick={onDownload}>
            <Download size={17} />
            Download JSON report
          </button>
        </section>
      </div>
    </div>
  );
}
