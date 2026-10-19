import { Fragment, useState } from "react";
import { ArrowRight, FileCode2, GitCompareArrows } from "lucide-react";
import { endpointIdentity } from '../project-workflow';
import {
  endpointPresentation,
  definitionSection,
  pairedLines,
} from "../overview-view";
const json = (value) => JSON.stringify(value, null, 2);
function ContractPane({
  title,
  contract,
  operation,
  section,
  compared,
  lines,
  status,
}) {
  return (
    <section className={`contract-pane pane-${status}`}>
      <header>
        <span>{title}</span>
        <span className="contract-version">
          {contract?.info?.version || "—"}
        </span>
      </header>
      {!operation ? (
        <div className="contract-missing">
          {compared
            ? "Endpoint not present in this version."
            : "No comparison in this run."}
        </div>
      ) : (
        <>
          <div className="contract-caption">
            <strong>
              {operation.definition?.summary || endpointIdentity(operation.endpoint).path}
            </strong>
            {operation.definition?.description && (
              <p>{operation.definition.description}</p>
            )}
          </div>
          <pre tabIndex={0} aria-label={`${title} ${section}`}>
            <code>
              {lines.map((line, i) => (
                <Fragment key={i}>
                  <span className={`diff-line diff-${line.type}`}>
                    <span aria-hidden="true" className="diff-marker">
                      {line.type === "added"
                        ? "+"
                        : line.type === "removed"
                          ? "−"
                          : " "}
                    </span>
                    {line.text}
                  </span>
                  {"\n"}
                </Fragment>
              ))}
            </code>
          </pre>
        </>
      )}
    </section>
  );
}
export default function RunOverview({ report, catalogOnly }) {
  const [selection, setSelection] = useState(null),
    [section, setSection] = useState("request");
  const overview = report.contract_overview;
  const { comparing, rows } = endpointPresentation(report, catalogOnly);
  const selected =
    rows.find((row) => row.key === selection) ||
    rows.find((row) => row.status !== "unchanged") ||
    rows[0];
  const lines = comparing
    ? pairedLines(
        selected?.before
          ? definitionSection(selected.before, section, overview.before)
          : null,
        selected?.after
          ? definitionSection(selected.after, section, overview.after)
          : null,
      )
    : {
        before: json(
          selected?.before
            ? definitionSection(selected.before, section, overview.before)
            : null,
        )
          .split("\n")
          .map((text) => ({ text, type: "same" })),
      };
  return (
    <div className="run-overview comparison-studio">
      <header className="comparison-heading">
        <div>
          <GitCompareArrows size={22} />
          <h3>{overview?.before?.info?.title || "API details"}</h3>
        </div>
        <span>
          {rows.length} endpoints{" "}
          {comparing && `· ${overview?.changes?.length || 0} changed`}
        </span>
      </header>
      {rows.length ? (
        <div className="comparison-workspace">
          <nav className="endpoint-rail" aria-label="API endpoints">
            {rows.map((row) => (
              <button
                className={
                  comparing ? `endpoint-${row.status}` : "endpoint-current"
                }
                key={row.key}
                aria-pressed={selected?.key === row.key}
                onClick={() => setSelection(row.key)}
              >
                <span className="endpoint-topline">
                  <span className={`method method-${row.method.toLowerCase()}`}>
                    {row.method}
                  </span>
                  {comparing && (
                    <span className={`endpoint-status status-${row.status}`}>
                      {row.status}
                    </span>
                  )}
                </span>
                <code>
                  {endpointIdentity(row.endpoint).path.split("/").map((part, index) => (
                    <Fragment key={index}>
                      {index > 0 && <wbr />}
                      {index > 0 ? "/" : ""}
                      {part}
                    </Fragment>
                  ))}
                </code>
                {endpointIdentity(row.endpoint).provider && <span className="project-endpoint-provider">{endpointIdentity(row.endpoint).provider}</span>}
              </button>
            ))}
          </nav>
          <div className="comparison-main">
            <div className="comparison-selection">
              <code>
                {selected.method} {endpointIdentity(selected.endpoint).path}
              </code>
              {comparing && <ArrowRight size={17} />}
              {comparing && (
                <span className={`endpoint-status status-${selected.status}`}>
                  {selected.status}
                </span>
              )}
            </div>
            <div
              className="definition-tabs"
              role="group"
              aria-label="Endpoint details"
            >
              {["request", "responses", "details", "schemas"].map((value) => (
                <button
                  key={value}
                  aria-pressed={section === value}
                  onClick={() => setSection(value)}
                >
                  {value === "details"
                    ? "Full details"
                    : value === "schemas"
                      ? "Shared schemas"
                      : value}
                </button>
              ))}
            </div>
            <div
              className={`contract-columns ${comparing ? "" : "endpoint-catalog-pane"}`}
              key={`${selected.key}:${section}`}
            >
              <ContractPane
                title={comparing ? "Original" : "Endpoint details"}
                contract={overview.before}
                operation={selected.before}
                section={section}
                compared={true}
                lines={lines.before}
                status={selected.status === "removed" ? "removed" : "neutral"}
              />
              {comparing && (
                <ContractPane
                  title="Updated"
                  contract={overview.after}
                  operation={selected.after}
                  section={section}
                  compared={!!report.comparison}
                  lines={lines.after}
                  status={selected.status === "added" ? "added" : "neutral"}
                />
              )}
            </div>
          </div>
        </div>
      ) : (
        <p>
          {overview?.unavailable || "No API operations recorded in this run."}
        </p>
      )}
      <div className="comparison-footer">
        <span>
          <FileCode2 size={15} />
          {report.source_commit?.slice(0, 12) || "Source not analyzed"}
        </span>
        <details>
          <summary>Source calls · {report.scan?.sites?.length || 0}</summary>
          {(report.scan?.sites || []).map((site, i) => (
            <p key={i}>
              <code>
                {site.method} {site.endpoint}
              </code>{" "}
              · {site.file}:{site.line} · {site.function}
              {site.intent && <span> · {site.intent}</span>}
            </p>
          ))}
        </details>
        {comparing && report.impacted_sites?.length > 0 && (
          <details>
            <summary>Affected calls · {report.impacted_sites.length}</summary>
            {report.impacted_sites.map((site, i) => (
              <p key={i}>
                <code>
                  {site.file}:{site.line}
                </code>{" "}
                · {site.function} · {site.method} {site.endpoint}
              </p>
            ))}
          </details>
        )}
      </div>
      {comparing &&
        (overview?.shared_changed ||
          Object.keys(overview?.metadata_changes || {}).length > 0) && (
          <details className="comparison-metadata">
            <summary>API settings & metadata changes</summary>
            <pre>
              {json({
                shared: overview.shared_changes,
                metadata: overview.metadata_changes,
              })}
            </pre>
          </details>
        )}
    </div>
  );
}
