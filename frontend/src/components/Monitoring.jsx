import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Radio, RefreshCw, Pause, Play, ArrowRight } from "lucide-react";
import { createSelectionGate, requestJSON } from "../workspace";
import {
  baselineDescription,
  monitorPresentation,
  monitorSaveRequest,
  validateMonitorInput,
  monitorEditDraft,
} from "../monitoring";

const blank = {
  source_url: "",
  allow_local: false,
  interval_minutes: 60,
  baseline_mode: "saved",
};
const date = (value) => (value ? new Date(value).toLocaleString() : "Not yet");
const post = (body) => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  ...(body ? { body: JSON.stringify(body) } : {}),
});

export default function Monitoring({
  integration,
  editable,
  onOpenJob,
  onRepairQueued,
  modelAvailable,
}) {
  const [state, setState] = useState(null),
    [input, setInput] = useState(blank),
    [error, setError] = useState("");
  const [pending, setPending] = useState(false),
    [editing, setEditing] = useState(false),
    [accepting, setAccepting] = useState(null);
  const [editRevision, setEditRevision] = useState(0);
  const gate = useMemo(() => createSelectionGate(), []),
    loaded = useRef(false),
    requestId = useRef(0);
  const url = `/api/integrations/${encodeURIComponent(integration)}/monitoring`;
  const load = useCallback(
    async (reset = false) => {
      const current = gate.capture(integration),
        id = ++requestId.current;
      const result = await requestJSON(url);
      if (!current() || id !== requestId.current) return;
      setState(result);
      if (!loaded.current || reset) {
        const draft = monitorEditDraft(result);
        setInput(draft.input);
        setEditRevision(draft.revision);
        setEditing(!result.configured);
        loaded.current = true;
      }
    },
    [gate, integration, url],
  );
  useEffect(() => {
    gate.select(integration);
    const refresh = () =>
      load().catch((e) => {
        if (gate.capture(integration)()) setError(e.message);
      });
    refresh();
    const timer = setInterval(refresh, 3000);
    return () => {
      clearInterval(timer);
      gate.select("");
    };
  }, [integration, gate, load]);

  async function act(callback, reset = false) {
    const current = gate.capture(integration);
    setPending(true);
    setError("");
    try {
      const result = await callback();
      if (!current()) return;
      await load(reset);
      if (current() && result?.job_id) onRepairQueued(result.job_id);
    } catch (e) {
      if (current()) setError(e.message);
    } finally {
      if (current()) setPending(false);
    }
  }
  function save(event) {
    event.preventDefault();
    const problem = validateMonitorInput(input);
    if (problem) {
      setError(problem);
      return;
    }
    act(
      () => requestJSON(url, monitorSaveRequest(input, editRevision, true)),
      true,
    );
  }
  const presentation = monitorPresentation(state),
    canEdit = editable && state?.editable;
  const fieldsDisabled = pending || !canEdit;
  return (
    <section className="monitor-panel" aria-labelledby="monitor-title">
      <div className="section-heading">
        <h2 id="monitor-title">
          <Radio size={20} aria-hidden="true" /> Contract monitoring
        </h2>
        <span
          className={`monitor-state ${state?.error ? "monitor-failed" : ""}`}
          role="status"
        >
          {state ? presentation.label : "Loading"}
        </span>
      </div>
      <p className="muted">
        {presentation.detail} Automatic checks compare contracts; repairs remain
        your choice.
      </p>
      {error && (
        <p className="error-message" role="alert">
          {error}{" "}
          <button onClick={() => act(() => load(true))} disabled={pending}>
            Reload monitoring
          </button>
        </p>
      )}
      {!state && !error && (
        <p className="muted">Loading saved monitoring settings…</p>
      )}
      {state && (
        <>
          {!canEdit && (
            <p className="monitor-note">
              This integration is managed by the server. Connect your own
              integration to configure monitoring.
            </p>
          )}
          {editing && canEdit ? (
            <form className="monitor-form" onSubmit={save}>
              {state.revision !== editRevision && (
                <p className="monitor-note monitor-wide" role="status">
                  Monitoring settings changed while you were editing. Reload
                  saved settings before retrying.
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() => act(() => load(true))}
                  >
                    Reload saved settings
                  </button>
                </p>
              )}
              <label className="monitor-url">
                OpenAPI contract URL
                <input
                  type="url"
                  required
                  value={input.source_url}
                  placeholder="https://api.example.com/openapi.json"
                  disabled={fieldsDisabled}
                  onChange={(e) =>
                    setInput({ ...input, source_url: e.target.value })
                  }
                />
              </label>
              <label>
                Check every (minutes)
                <input
                  type="number"
                  min="5"
                  max="10080"
                  required
                  value={input.interval_minutes}
                  disabled={fieldsDisabled}
                  onChange={(e) =>
                    setInput({ ...input, interval_minutes: e.target.value })
                  }
                />
              </label>
              <label className="monitor-baseline">
                Initial baseline
                <select
                  value={input.baseline_mode}
                  disabled={fieldsDisabled}
                  onChange={(e) =>
                    setInput({ ...input, baseline_mode: e.target.value })
                  }
                >
                  <option value="saved">Saved current contract</option>
                  <option value="first_fetch">First download</option>
                </select>
                <span className="muted">
                  {baselineDescription(input.baseline_mode)}
                </span>
              </label>
              <label className="monitor-optin">
                <input
                  type="checkbox"
                  checked={input.allow_local}
                  disabled={fieldsDisabled}
                  onChange={(e) =>
                    setInput({ ...input, allow_local: e.target.checked })
                  }
                />{" "}
                Allow a trusted local or private-network source, including HTTP
              </label>
              <p className="muted monitor-wide">
                Only enable local sources you trust. JSON OpenAPI contracts are
                limited to 2 MiB. Changing the source starts a new baseline;
                previous evidence stays available.
              </p>
              <div className="monitor-actions monitor-wide">
                <button
                  className="primary"
                  disabled={fieldsDisabled}
                  type="submit"
                >
                  <Play size={15} aria-hidden="true" />
                  {pending
                    ? "Saving…"
                    : state.configured
                      ? "Save and enable"
                      : "Enable monitoring"}
                </button>
                {state.configured && (
                  <button
                    type="button"
                    disabled={pending}
                    onClick={() => {
                      setInput({
                        source_url: state.source_url,
                        allow_local: state.allow_local,
                        interval_minutes: state.interval_minutes,
                        baseline_mode: state.baseline_mode,
                      });
                      setEditing(false);
                      setError("");
                    }}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          ) : state.configured ? (
            <>
              <p className="monitor-source">{state.source_url}</p>
              <dl className="monitor-times">
                <div>
                  <dt>Interval</dt>
                  <dd>{state.interval_minutes} minutes</dd>
                </div>
                <div>
                  <dt>Last successful check</dt>
                  <dd>{date(state.last_success)}</dd>
                </div>
                <div>
                  <dt>Next check</dt>
                  <dd>{state.enabled ? date(state.next_due) : "Paused"}</dd>
                </div>
              </dl>
              <p className="muted">
                Baseline:{" "}
                {state.baseline_hash
                  ? "Accepted contract snapshot"
                  : baselineDescription(state.baseline_mode)}
                {state.allow_local ? " · Trusted local sources allowed" : ""}
              </p>
              {canEdit && (
                <div className="monitor-actions">
                  <button
                    className="primary"
                    disabled={pending || Boolean(state.active_check)}
                    onClick={() =>
                      act(() => requestJSON(url + "/check", post()))
                    }
                  >
                    <RefreshCw size={15} aria-hidden="true" />
                    Check now
                  </button>
                  <button
                    disabled={pending}
                    onClick={() =>
                      act(
                        () =>
                          requestJSON(
                            url,
                            monitorSaveRequest(
                              {
                                source_url: state.source_url,
                                allow_local: state.allow_local,
                                interval_minutes: state.interval_minutes,
                                baseline_mode: state.baseline_mode,
                              },
                              state.revision,
                              !state.enabled,
                            ),
                          ),
                        true,
                      )
                    }
                  >
                    {state.enabled ? (
                      <Pause size={15} aria-hidden="true" />
                    ) : (
                      <Play size={15} aria-hidden="true" />
                    )}
                    {state.enabled ? "Pause" : "Resume"}
                  </button>
                  <button
                    disabled={pending}
                    onClick={() => {
                      const draft = monitorEditDraft(state);
                      setInput(draft.input);
                      setEditRevision(draft.revision);
                      setEditing(true);
                    }}
                  >
                    Edit source
                  </button>
                </div>
              )}
            </>
          ) : (
            <p className="muted">No monitored source has been configured.</p>
          )}
          {state.error && (
            <p className="error-message" role="alert">
              {state.error} Check the source and try Check now. Your accepted
              baseline is preserved.
            </p>
          )}
          <div className="monitor-changes">
            <h3>
              Observed changes{" "}
              <span className="count">{state.changes.length}</span>
            </h3>
            {!state.changes.length && (
              <p className="muted">
                {state.last_success
                  ? "No contract changes observed against the accepted baseline."
                  : "Changes will appear after a successful comparison."}
              </p>
            )}
            {[...state.changes].reverse().map((change) => (
              <div className="monitor-change" key={change.id}>
                <div>
                  <strong>{date(change.created_at)}</strong>
                  <p className="muted">
                    {change.observed_hash === state.baseline_hash
                      ? "Accepted as baseline"
                      : change.baseline_hash === state.baseline_hash
                        ? "Compared with the current baseline"
                        : "Earlier baseline comparison"}{" "}
                    ·{" "}
                    {change.job_status === "completed"
                      ? "Comparison complete"
                      : change.job_status?.replaceAll("_", " ") ||
                        "Comparison queued"}
                  </p>
                </div>
                <div className="monitor-actions">
                  <button
                    disabled={pending || change.job_available === false}
                    onClick={() => onOpenJob(change.job_id)}
                  >
                    View evidence <ArrowRight size={15} aria-hidden="true" />
                  </button>
                  {canEdit && (
                    <>
                      <button
                        disabled={pending || Boolean(state.active_check)}
                        onClick={() =>
                          act(() =>
                            requestJSON(
                              url + `/changes/${change.id}/rescan`,
                              post(),
                            ),
                          )
                        }
                      >
                        Rescan code
                      </button>
                      <button
                        disabled={pending || !modelAvailable}
                        title={
                          !modelAvailable
                            ? "Configure a model key to request a repair"
                            : undefined
                        }
                        onClick={() =>
                          act(() =>
                            requestJSON(
                              url + `/changes/${change.id}/repair`,
                              post(),
                            ),
                          )
                        }
                      >
                        Request repair
                      </button>
                      <button
                        disabled={
                          pending ||
                          change.observed_hash === state.baseline_hash
                        }
                        onClick={() => setAccepting(change)}
                      >
                        Accept as baseline
                      </button>
                    </>
                  )}
                </div>
                {accepting?.id === change.id && (
                  <div
                    className="monitor-accept"
                    role="group"
                    aria-label="Confirm baseline acceptance"
                  >
                    <p>
                      Future checks will compare against this downloaded
                      version. Accepting it acknowledges the contract; it does
                      not repair or validate your code.
                    </p>
                    <button
                      disabled={pending}
                      className="primary"
                      onClick={() =>
                        act(async () => {
                          const result = await requestJSON(
                            url + "/accept",
                            post({
                              change_id: change.id,
                              expected_revision: state.revision,
                            }),
                          );
                          setAccepting(null);
                          return result;
                        })
                      }
                    >
                      Confirm baseline
                    </button>
                    <button
                      disabled={pending}
                      onClick={() => setAccepting(null)}
                    >
                      Keep current baseline
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
