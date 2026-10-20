export async function requestJSON(path, options = {}, fetcher = fetch) {
  let response;
  try {
    response = await fetcher(path, options);
  } catch {
    throw new Error("Cannot reach APIShield. Start the app and retry.");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail =
      typeof data.detail === "string"
        ? data.detail
        : "Check your inputs and try again.";
    throw new Error(detail);
  }
  return data;
}

export function jobPresentation(job) {
  const labels = {
    queued: "Queued",
    running: "Running",
    completed: "Completed",
    validated: "Tests passed",
    no_change: "No relevant change",
    needs_input: "Needs your input",
    failed: "Failed",
    cancelled: "Cancelled",
  };
  const operation =
    { scan: "Scan", compare: "Compare", repair: "Repair" }[job.operation] ||
    "Run";
  return {
    operation,
    label: labels[job.status] || "Unknown",
    busy: ["queued", "running"].includes(job.status),
    canDownload:
      job.status === "validated" &&
      job.operation === "repair" &&
      Boolean(job.patch),
  };
}

export function graphEvidence(report) {
  return report.application?.status === "applied" && report.current_graph_report
    ? report.current_graph_report
    : report;
}

export function projectDisplayName(name) {
  return ({'banking-example':'NexusBank Integration',cinemaflow:'CinemaFlow Integration','cinema-theatre':'IMAX','cinema-payment':'GPay'})[name] || name;
}

export function repositoryGroups(projects) {
  return {repositories:projects.filter(p=>p.kind!=='provider'),providers:projects.filter(p=>p.kind==='provider')};
}

export function contractDisplayTitle(title) {
  return ({'Grand Cinema theatre provider':'IMAX theatre provider','CinemaPay simulated payment provider':'GPay payment provider'})[title] || title || 'API details';
}

export function providerDisplayName(id) {
  return ({theatre:'IMAX',payment:'GPay'})[id] || id;
}

export function refreshedJobReport(current, incoming) {
  // A poll already in flight when Apply commits can contain the older result.
  return current?.job_id === incoming.job_id && current.application?.status === "applied" && incoming.application?.status !== "applied"
    ? current : incoming;
}

export function orderedJobs(jobs) {
  return [...jobs].sort((a, b) =>
    (b.created_at || "").localeCompare(a.created_at || ""),
  );
}

export function createSelectionGate() {
  let selected = "",
    version = 0;
  return {
    select(id) {
      selected = id;
      version++;
    },
    capture(id) {
      const token = version;
      return () => selected === id && token === version;
    },
  };
}

export function editRequirement(rule, changes, saving = false) {
  if (saving) return rule;
  return { ...rule, ...changes, confirmed: false };
}

export function requirementsSaveRequest(data, requirements) {
  return {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ requirements, expected_hash: data.edit_token }),
  };
}

export function requirementPresentation(rule) {
  const checked =
    rule.status === "passed" &&
    rule.confirmed &&
    rule.checks?.length > 0 &&
    rule.evidence?.length === rule.checks.length &&
    rule.evidence.every(
      (item) =>
        item.command?.exit_code === 0 &&
        !item.command.timed_out &&
        !item.command.cancelled &&
        item.result?.passed &&
        item.result.tests > 0,
    );
  if (checked) return { label: "Checks passed", tone: "passed" };
  const labels = {
    failed: "Checks failed",
    needs_input: "Needs input",
    not_applicable: "Not affected",
    unconfirmed: "Unconfirmed",
    pending: "Not checked",
  };
  return {
    label: labels[rule.status] || "Not checked",
    tone: rule.status === "failed" ? "failed" : "neutral",
  };
}

export function requirementRelations(graph) {
  const nodes = new Map((graph.nodes || []).map((node) => [node.id, node]));
  return (graph.edges || [])
    .filter((edge) => edge.kind === "scopes")
    .flatMap((edge) => {
      const rule = nodes.get(edge.from),
        call = nodes.get(edge.to);
      return rule?.kind === "requirement" && call?.kind === "call"
        ? [
            {
              ...call,
              requirement_id: rule.requirement_id,
              checks: rule.checks || [],
            },
          ]
        : [];
    });
}
