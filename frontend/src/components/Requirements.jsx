import { useEffect, useState } from "react";
import { Plus, X, Check, Pencil, Trash2 } from "lucide-react";
import {
  requestJSON,
  editRequirement,
  requirementPresentation,
  requirementRelations,
  requirementsSaveRequest,
} from "../workspace";

const blank = () => ({
  id: "",
  description: "",
  scope: { file: "", function: "" },
  origin: "developer",
  confirmed: false,
  checks: [],
});

export function RequirementRelationships({ graph }) {
  const relations = requirementRelations(graph);
  return (
    <>
      <p className="muted">
        Source operations come from static analysis. Rule and test links are
        developer declarations; they do not prove complete test coverage.
      </p>
      {relations.map((item, index) => (
        <div className="requirement-row" key={index}>
          <strong>{item.requirement_id}</strong>
          <p>
            <code>
              {item.file} · {item.function}
            </code>
          </p>
          <p>
            Consumes{" "}
            <code>
              {item.method} {item.endpoint || "unresolved URL"}
            </code>
          </p>
          <p>
            Linked checks:{" "}
            {item.checks.length
              ? item.checks.map((check) => (
                  <code className="requirement-reference" key={check}>
                    {check}
                  </code>
                ))
              : "none declared"}
          </p>
        </div>
      ))}
      {(graph.notes || []).map((note, index) => (
        <p className="muted" key={index}>
          {note.requirement_id || note.file}: {note.reason}
        </p>
      ))}
      {!relations.length && (
        <p className="muted">
          No declared requirements are linked to supported calls in this
          snapshot.
        </p>
      )}
    </>
  );
}

export function RequirementEvidence({ outcomes = [] }) {
  if (!outcomes.length)
    return (
      <p className="muted">
        No explicit business requirement checks were run for this report.
      </p>
    );
  return (
    <div className="requirement-list">
      {outcomes.map((rule) => {
        const view = requirementPresentation(rule);
        return (
          <article className="requirement-row" key={rule.id}>
            <div className="requirement-heading">
              <strong>{rule.id}</strong>
              <span className={`requirement-status requirement-${view.tone}`}>
                {view.label}
              </span>
            </div>
            <p>{rule.description}</p>
            <code>
              {rule.scope.file} · {rule.scope.function}
            </code>
            {rule.reason && <p className="requirement-reason">{rule.reason}</p>}
            {(rule.evidence || []).map((item, index) => (
              <details className="command-evidence" key={index}>
                <summary>
                  {item.reference} · {item.result?.tests ?? 0} collected ·{" "}
                  {item.result?.passed ? "Passed" : "Not established"}
                </summary>
                <pre>
                  {item.command.stdout}
                  {item.command.stderr}
                </pre>
              </details>
            ))}
          </article>
        );
      })}
    </div>
  );
}

export default function Requirements({ integration, suggestions = [] }) {
  const [data, setData] = useState(null),
    [draft, setDraft] = useState(null),
    [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [saving, setSaving] = useState(false);
  const endpoint = `/api/integrations/${encodeURIComponent(integration)}/requirements`;
  useEffect(() => {
    let current = true;
    requestJSON(endpoint)
      .then((value) => {
        if (current) setData(value);
      })
      .catch((e) => {
        if (current) setError(e.message);
      });
    return () => {
      current = false;
    };
  }, [endpoint]);
  async function reload() {
    try {
      setData(await requestJSON(endpoint));
      setError("");
      setNotice("Saved rules reloaded. Your unsaved draft is still open.");
    } catch (e) {
      setError(e.message);
    }
  }
  async function save(rules, message) {
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const result = await requestJSON(
        endpoint,
        requirementsSaveRequest(data, rules),
      );
      setData(result);
      setDraft(null);
      setEditingId(null);
      setNotice(message);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }
  function edit(rule, id = null) {
    setDraft({
      ...rule,
      scope: { ...rule.scope },
      checks: [...rule.checks],
      confirmed: false,
    });
    setEditingId(id);
    setError("");
    setNotice("");
  }
  function change(changes) {
    setDraft((previous) => editRequirement(previous, changes, saving));
  }
  function submit(event) {
    event.preventDefault();
    if (
      data.requirements.some(
        (rule) => rule.id === draft.id && rule.id !== editingId,
      )
    ) {
      setError("That rule ID is already used. Choose a different ID.");
      return;
    }
    const normalized = {
      ...draft,
      checks: draft.checks.map((check) => check.trim()).filter(Boolean),
    };
    save(
      [
        ...data.requirements.filter((rule) => rule.id !== editingId),
        normalized,
      ],
      "Draft saved. Review the saved rule, then choose Confirm rule.",
    );
  }
  return (
    <section
      className="requirements-panel"
      aria-labelledby="requirements-title"
    >
      <div className="section-heading">
        <div>
          <h2 id="requirements-title">Business requirements</h2>
          <p>
            Define what an API migration must preserve, and link committed tests
            that check it.
          </p>
        </div>
        {data?.editable && !draft && (
          <button
            className="secondary-button"
            disabled={saving}
            onClick={() => edit(blank())}
          >
            <Plus size={16} />
            Add rule
          </button>
        )}
      </div>
      {!data && !error && <p role="status">Loading saved requirements…</p>}
      {error && (
        <div className="error-message" role="alert">
          <p>{error}</p>
          <button
            className="secondary-button"
            disabled={saving}
            onClick={reload}
          >
            Reload saved rules
          </button>
        </div>
      )}
      {notice && (
        <p className="notice" role="status">
          {notice}
        </p>
      )}
      {data && !data.editable && (
        <p className="muted">
          Read-only:{" "}
          {integration === "shipping-example"
            ? "the example includes a supplied rule and an independent test."
            : "update this integration’s trusted server configuration to change requirements."}
        </p>
      )}
      {draft && (
        <form className="requirement-form integration-form" onSubmit={submit}>
          <div className="requirement-heading requirement-wide">
            <h3>{editingId ? "Edit rule" : "New rule"}</h3>
            <button
              type="button"
              className="icon-button"
              disabled={saving}
              onClick={() => setDraft(null)}
              aria-label="Close rule editor"
            >
              <X size={18} />
            </button>
          </div>
          <label>
            Rule ID
            <input
              disabled={saving}
              required
              pattern="[A-Za-z0-9_-]{1,64}"
              maxLength={64}
              value={draft.id}
              onChange={(e) => change({ id: e.target.value })}
              placeholder="preserve-exact-weight"
            />
          </label>
          <label className="requirement-wide">
            Business rule
            <textarea
              disabled={saving}
              required
              maxLength={2000}
              rows={3}
              value={draft.description}
              onChange={(e) => change({ description: e.target.value })}
              placeholder="Preserve the exact integer weight supplied by the caller."
            />
          </label>
          <label>
            Source file
            <input
              disabled={saving}
              required
              value={draft.scope.file}
              onChange={(e) =>
                change({ scope: { ...draft.scope, file: e.target.value } })
              }
              placeholder="src/parcel.py"
            />
          </label>
          <label>
            Function
            <input
              disabled={saving}
              required
              value={draft.scope.function}
              onChange={(e) =>
                change({ scope: { ...draft.scope, function: e.target.value } })
              }
              placeholder="create_label"
            />
          </label>
          <label className="requirement-wide">
            Pytest references
            <textarea
              disabled={saving}
              rows={3}
              value={draft.checks.join("\n")}
              onChange={(e) => change({ checks: e.target.value.split("\n") })}
              placeholder="tests/test_parcel.py::test_shipping_preserves_package_and_weight"
            />
            <small>
              One test function per line. Tests must be committed and runnable
              in the app’s environment. No command flags.
            </small>
          </label>
          <p className="requirement-wide muted">
            Saving creates an unconfirmed draft. Confirmation is your
            declaration that the rule and its linked tests are appropriate; only
            a completed run establishes check results.
          </p>
          <button className="primary-button" disabled={saving}>
            {saving ? "Saving…" : "Save draft"}
          </button>
        </form>
      )}
      {data && !data.requirements.length && !draft && (
        <p className="muted">
          No rules yet. For example: preserve exact integer grams, keep the
          customer identity, or never substitute a charge for a refund.
        </p>
      )}
      <div className="requirement-list">
        {(data?.requirements || []).map((rule) => (
          <article className="requirement-row" key={rule.id}>
            <div className="requirement-heading">
              <strong>{rule.id}</strong>
              <span className="requirement-status">
                {rule.confirmed
                  ? "Confirmed declaration"
                  : "Draft — review required"}
              </span>
            </div>
            <p>{rule.description}</p>
            <code>
              {rule.scope.file} · {rule.scope.function}
            </code>
            <ul>
              {rule.checks.map((check) => (
                <li key={check}>
                  <code>{check}</code>
                </li>
              ))}
            </ul>
            {!rule.checks.length && (
              <p className="muted">
                No linked checks. If confirmed and affected, this rule will
                require input before repair.
              </p>
            )}
            {data?.editable && !draft && (
              <div className="requirement-actions">
                {!rule.confirmed && (
                  <button
                    className="secondary-button"
                    disabled={saving}
                    onClick={() =>
                      save(
                        data.requirements.map((item) =>
                          item.id === rule.id
                            ? { ...item, confirmed: true }
                            : item,
                        ),
                        "Rule confirmed. Start a new run to check it.",
                      )
                    }
                  >
                    <Check size={15} />
                    Confirm rule
                  </button>
                )}
                <button
                  className="secondary-button"
                  disabled={saving}
                  onClick={() => edit(rule, rule.id)}
                >
                  <Pencil size={15} />
                  Edit rule
                </button>
                <button
                  className="secondary-button"
                  disabled={saving}
                  onClick={() =>
                    save(
                      data.requirements.filter((item) => item.id !== rule.id),
                      "Rule removed from future runs. Past evidence is unchanged.",
                    )
                  }
                >
                  <Trash2 size={15} />
                  Remove rule
                </button>
              </div>
            )}
          </article>
        ))}
      </div>
      {data?.editable && suggestions.length > 0 && (
        <details className="requirement-suggestions">
          <summary>Suggested source intent · review required</summary>
          <p className="muted">
            Comments are suggestions, not verified requirements. Review the
            scope and add tests before confirming.
          </p>
          {suggestions
            .filter(
              (rule) => !data.requirements.some((item) => item.id === rule.id),
            )
            .map((rule) => (
              <div className="requirement-row" key={rule.id}>
                <p>{rule.description}</p>
                <code>
                  {rule.scope.file} · {rule.scope.function}
                </code>
                <button
                  className="secondary-button"
                  disabled={!!draft || saving}
                  onClick={() => edit(rule)}
                >
                  Review suggestion
                </button>
              </div>
            ))}
        </details>
      )}
    </section>
  );
}
