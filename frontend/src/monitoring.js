export function monitorPresentation(state) {
  if (!state?.configured)
    return {
      label: "Not configured",
      detail: "Connect a contract source to check for changes.",
    };
  if (state.active_check)
    return {
      label: state.baseline_hash ? "Checking" : "Initializing",
      detail: "Downloading and comparing the approved contract.",
    };
  if (state.error)
    return {
      label: "Check failed",
      detail: "Your previous baseline and evidence are preserved.",
    };
  if (!state.enabled)
    return {
      label: "Paused",
      detail: "Automatic checks are paused. You can still check now.",
    };
  return {
    label: "Scheduled",
    detail: "Checks run while APIShield and this computer are running.",
  };
}

export function baselineDescription(mode) {
  return mode === "first_fetch"
    ? "Use the first download as the baseline; initialization creates no change alert."
    : "Compare the first download with your saved current contract to reveal any existing changes.";
}

export function validateMonitorInput(input) {
  try {
    const url = new URL(input.source_url);
    if (
      !(input.allow_local ? ["http:", "https:"] : ["https:"]).includes(
        url.protocol,
      )
    )
      return "Use HTTPS or explicitly allow a trusted local HTTP source.";
    if (url.username || url.password || url.hash)
      return "Remove credentials and fragments from the contract URL.";
  } catch {
    return "Enter a complete OpenAPI contract URL.";
  }
  if (
    !Number.isInteger(Number(input.interval_minutes)) ||
    Number(input.interval_minutes) < 5 ||
    Number(input.interval_minutes) > 10080
  )
    return "Choose a check interval from 5 to 10080 minutes.";
  return null;
}

export function monitorSaveRequest(input, revision, enabled) {
  return {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...input,
      interval_minutes: Number(input.interval_minutes),
      enabled,
      expected_revision: revision,
    }),
  };
}

export function monitorEditDraft(state) {
  return {
    revision: state.revision,
    input: {
      source_url: state.source_url,
      allow_local: state.allow_local,
      interval_minutes: state.interval_minutes,
      baseline_mode: state.baseline_mode,
    },
  };
}
