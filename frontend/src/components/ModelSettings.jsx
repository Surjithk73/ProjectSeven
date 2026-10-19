import { useEffect, useRef, useState } from "react";
import { CheckCircle2, Cloud, Unplug } from "lucide-react";
import { requestJSON, createSelectionGate } from "../workspace";
import {
  validateCredentialFile,
  modelConfigureRequest,
  modelConnectionPresentation,
} from "../model-settings";

export default function ModelSettings({ onSaved }) {
  const [data, setData] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const file = useRef(null);
  const gate = useRef(createSelectionGate());
  useEffect(() => {
    const selection = gate.current;
    selection.select("mounted");
    const current = selection.capture("mounted");
    requestJSON("/api/settings/model")
      .then((value) => {
        if (current()) setData(value);
      })
      .catch((failure) => {
        if (current()) setError(failure.message);
      });
    return () => selection.select("unmounted");
  }, []);
  async function action(kind, event) {
    event?.preventDefault();
    gate.current.select(kind);
    const current = gate.current.capture(kind);
    setBusy(kind);
    setError("");
    setMessage("");
    try {
      let response;
      if (kind === "configure") {
        const value = await validateCredentialFile(file.current.files[0]);
        const request = modelConfigureRequest("google_cloud", value);
        response = await requestJSON(request.path, request.options);
        if (current()) {
          setData(response);
          setMessage(
            "Service account saved privately and loaded automatically after restart.",
          );
        }
      } else if (kind === "test") {
        response = await requestJSON("/api/settings/model/test", {
          method: "POST",
        });
        if (current()) {
          if (response.stale)
            setMessage(
              "The account changed during this test. Test the current account.",
            );
          else if (!response.success) setError(response.error.message);
          else
            setMessage(
              `Google responded successfully in ${response.elapsed_seconds}s.`,
            );
          setData(await requestJSON("/api/settings/model"));
        }
      } else {
        response = await requestJSON("/api/settings/model/clear", {
          method: "POST",
        });
        if (current()) {
          setData(response);
          setMessage("Service-account connection removed.");
        }
      }
      if (current()) onSaved();
    } catch (failure) {
      if (current()) setError(failure.message);
    } finally {
      if (current()) {
        setBusy("");
        if (file.current) file.current.value = "";
      }
    }
  }
  const summary = modelConnectionPresentation(data);
  return (
    <div className="model-settings">
      <p>
        <Cloud size={18} /> Google Cloud service account
      </p>
      <p>
        The saved account is used for every AI request and loads automatically
        after restart.
      </p>
      <form onSubmit={(event) => action("configure", event)}>
        <fieldset disabled={Boolean(busy)} className="model-provider-fields">
          <legend>Replace service account</legend>
          <div className="model-form">
            <label>
              Service-account JSON
              <input
                ref={file}
                type="file"
                accept=".json,application/json"
                required
              />
              <span className="model-field-help">
                Downloaded from Google Cloud, up to 64 KiB
              </span>
            </label>
            <button className="primary-button" disabled={Boolean(busy)}>
              {busy === "configure" ? "Saving..." : "Save service account"}
            </button>
          </div>
        </fieldset>
      </form>
      <div className="model-connection-summary">
        <div>
          <strong>
            {data?.test?.success ? (
              <CheckCircle2 size={17} />
            ) : (
              <Unplug size={17} />
            )}{" "}
            {summary.label}
          </strong>
          <p>{summary.detail}</p>
        </div>
        <div className="model-actions">
          <button
            className="secondary-button"
            disabled={!data?.configured || Boolean(busy)}
            onClick={() => action("test")}
          >
            {busy === "test" ? "Testing..." : "Test connection"}
          </button>
          <button
            className="text-button"
            disabled={!data?.configured || Boolean(busy)}
            onClick={() => action("clear")}
          >
            {busy === "clear" ? "Removing..." : "Remove connection"}
          </button>
        </div>
      </div>
      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}
      <p role="status" aria-live="polite">
        {message}
      </p>
      <p className="model-session-note">
        The private credential stays outside the project. Connection tests and
        AI generation send requests to Google; usage charges apply.
      </p>
    </div>
  );
}
