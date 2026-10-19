import { orderedJobs, jobPresentation, requestJSON } from "./workspace.js";

export function appliedUpdateSummary(report) {
  if (report.operation !== "repair" || report.application?.status !== "applied") return null;
  return {
    title: "Changes applied successfully",
    description: "The validated update is now in your working files. The updated integration passed the recorded tests. You can return to your application and try it now.",
    fileCount: report.application.files?.length || 0,
    banking: report.integration === "banking-example",
  };
}

export async function applyReviewedUpdate(report, {request = requestJSON, isCurrent, onApplied}) {
  const application = await request(`/api/jobs/${report.job_id}/apply`, {
    method: "POST", headers: {"Content-Type":"application/json"}, body: "{}",
  });
  if (application.status !== "applied") throw new Error("Apply has not been confirmed. Refresh this result to check its status.");
  if (!isCurrent()) return;
  // Confirm the persisted write immediately; refreshing the graph is separate.
  onApplied({...report, application});
  try {
    const updated = await request(`/api/jobs/${report.job_id}`);
    if (isCurrent()) onApplied(updated);
  } catch {
    if (isCurrent()) throw new Error("Changes were applied successfully, but the latest results could not refresh. Refresh this result to load the updated graph.");
  }
}

export function projectRuns(jobs, name) {
  return orderedJobs(
    jobs.filter(
      (job) =>
        !job.publication_source_job && (!name || job.integration === name),
    ),
  );
}

export function dashboardActions(integration, jobs, sourceHash, apiContext) {
  const review = sourceHash
    ? projectRuns(jobs, integration).find(
        (job) =>
          job.operation === "repair" &&
          job.status === "validated" &&
          job.source_hash === sourceHash &&
          (!apiContext ||
            ["accepted_hash", "observed_hash", "config_fingerprint"].every(
              (key) => job.api_context?.[key] === apiContext[key],
            )) &&
          job.proposal_source !== "offline" &&
          job.application?.status !== "applied",
      ) || null
    : null;
  return { primary: "Check for API Changes", review };
}

export function observeSelectedTab(container, Observer = ResizeObserver) {
  const reveal = () => {
    const selected = container.querySelector('[aria-selected="true"]');
    if (!selected || !container.clientWidth) return;
    const left = selected.offsetLeft;
    const right = left + selected.offsetWidth;
    if (left < container.scrollLeft)
      container.scrollTo({ left, behavior: "auto" });
    else if (right > container.scrollLeft + container.clientWidth)
      container.scrollTo({
        left: right - container.clientWidth,
        behavior: "auto",
      });
  };
  reveal();
  const observer = new Observer(reveal);
  observer.observe(container);
  return () => observer.disconnect();
}

export function errorRecovery(actionError, connectionError) {
  if (actionError)
    return { kind: "action", message: actionError, button: "Dismiss message" };
  if (connectionError)
    return {
      kind: "connection",
      message: connectionError,
      button: "Retry connection",
    };
  return null;
}

export function patchState(patch, error) {
  return patch ? "ready" : error ? "failed" : "loading";
}

export function workspaceSuggestion(project, jobs, modelAvailable) {
  const latest = projectRuns(jobs, project?.name)[0];
  const review = (label) => ({ action: "review", label, jobId: latest.job_id });
  if (latest && jobPresentation(latest).busy) return review("View progress");
  if (latest && ["failed", "needs_input", "cancelled"].includes(latest.status))
    return review("Review what needs attention");
  if (latest?.operation === "repair") return review("Review your repair");
  if (latest?.operation === "compare" && latest.status === "completed") {
    if (!latest.impacted_sites?.length) return review("View the comparison");
    if (project.example)
      return { action: "example", label: "Try the example repair" };
    return modelAvailable
      ? { action: "repair", label: "Generate AI repair" }
      : { action: "model", label: "Set up AI repair" };
  }
  return { action: "compare", label: "Check API changes" };
}

export function resultSummary(report) {
  const applied = appliedUpdateSummary(report);
  if (applied) return {title: applied.title, description: applied.description};
  if (jobPresentation(report).busy)
    return {
      title: "Your check is running",
      description:
        "Work happens in a temporary copy. You can leave this screen and return to Results.",
    };
  if (report.status === "validated")
    return {
      title: "Your repair is ready to review",
      description:
        "The proposed change passed your configured tests. Review the patch before accepting it; your original code is unchanged.",
    };
  if (report.status === "no_change")
    return {
      title: "No repair was needed",
      description:
        "No relevant change was found for the supported API calls. Coverage notes explain what the check could not understand.",
    };
  if (report.status === "needs_input")
    return {
      title: "More information is needed",
      description: "Read the explanation below before trying another repair.",
    };
  if (report.status === "failed")
    return {
      title: "This run needs attention",
      description:
        "The run did not finish successfully. Check the error and test output before starting again.",
    };
  if (report.status === "cancelled")
    return {
      title: "This run was cancelled",
      description:
        "Your original code is unchanged. You can start another check from Workspace.",
    };
  if (report.operation === "scan")
    return {
      title: "Here are the API calls we found",
      description:
        "This scan reads supported calls in your committed Python code. It does not change or repair anything.",
    };
  return {
    title: "Your API comparison is ready",
    description:
      "Review the changes and affected calls below. A comparison does not generate a repair or run repair tests.",
  };
}
