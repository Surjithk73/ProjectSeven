import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  ShieldCheck,
  FolderGit2,
  History,
  Settings2,
  Plus,
  ArrowRight,
  Download,
  RefreshCw,
  X,
  Search,
  Wrench,
  LayoutDashboard,
  BookOpen,
  ArrowLeft,
  ChevronRight,
  GitCompareArrows,
} from "lucide-react";

import {
  requestJSON,
  jobPresentation,
  orderedJobs,
  createSelectionGate,
  graphEvidence,
  refreshedJobReport,
  projectDisplayName,
} from "../workspace";

import "../workspace.css";

import { ChecksPanel, TechnicalPanel } from "../components/RunEvidence";

import Monitoring from "../components/Monitoring";

import ModelSettings from "../components/ModelSettings";

import GitHubPublication, {
  GitHubTarget,
} from "../components/GitHubPublication";

import WorkspaceGuide, { SectionTabs } from "../components/WorkspaceGuide";

import ThemeControl from "../components/ThemeControl";

import ImpactGraph from "../components/SemanticNetwork";

import RunOverview from "../components/RunOverview";

import RepositorySwitcher from "../components/RepositorySwitcher";

import RepairDiff from "../components/RepairDiff";
import AgentActivity from "../components/AgentActivity";
import ChangeNotice from "../components/ChangeNotice";
import AppliedUpdateNotice from "../components/AppliedUpdateNotice";
import IntegrationSnapshot from "../components/IntegrationSnapshot";
import ProviderOverview from "../components/ProviderOverview";
import DeploymentStatus from "../components/DeploymentStatus";
import { activityOutcome } from "../dashboard-details";

import "../workbench.css";

import {
  projectRuns,
  dashboardActions,
  resultSummary,
  errorRecovery,
  patchState,
  applyReviewedUpdate,
  appliedUpdateSummary,
} from "../workspace_flow";

const post = (body) => ({
  method: "POST",

  headers: { "Content-Type": "application/json" },

  body: JSON.stringify(body),
});

const date = (value) =>
  value
    ? new Date(value).toLocaleString([], {
        month: "short",

        day: "numeric",

        hour: "2-digit",

        minute: "2-digit",
      })
    : "Just now";

function Status({ job }) {
  return (
    <span className={`run-status status-${job.status}`}>
      <span aria-hidden="true" />

      {jobPresentation(job).label}
    </span>
  );
}

function IntegrationForm({ onSaved, onClose, initial }) {
  const [error, setError] = useState("");

  const [saving, setSaving] = useState(false);

  async function submit(event) {
    event.preventDefault();

    setSaving(true);

    setError("");

    const form = new FormData(event.currentTarget);

    try {
      const base = form.get("base").size
        ? JSON.parse(await form.get("base").text())
        : initial.base_spec;

      const target = form.get("target").size
        ? JSON.parse(await form.get("target").text())
        : initial?.target_spec || base;

      const options = post({
        name: form.get("name"),

        repository: form.get("repository"),

        code_paths: form

          .get("paths")

          .split(",")

          .map((x) => x.trim())

          .filter(Boolean),

        test_path: "tests",

        base_spec: base,

        target_spec: target,
      });

      if (initial) options.method = "PUT";

      const result = await requestJSON(
        initial ? `/api/integrations/${initial.name}` : "/api/integrations",

        options,
      );

      onSaved(result.name);
    } catch (e) {
      setError(
        e instanceof SyntaxError
          ? "One of the contracts is not valid JSON. Choose a JSON OpenAPI file."
          : e.message,
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="setup-panel" aria-labelledby="setup-title">
      <div className="section-heading">
        <div>
          <h2 id="setup-title">
            {initial ? "Edit project" : "Connect a project"}
          </h2>

          <p>
            {initial
              ? "Upload updated contracts or change the source and test directories. Existing runs keep their original evidence."
              : "Choose a repository on this computer and the API contracts to compare."}
          </p>
        </div>

        <button
          className="icon-button"
          onClick={onClose}
          aria-label="Close project form"
        >
          <X size={20} />
        </button>
      </div>

      <form onSubmit={submit} className="integration-form">
        <label>
          Project name
          <input
            name="name"
            placeholder="shipping-service"
            defaultValue={initial?.name}
            readOnly={!!initial}
            required
            pattern="[A-Za-z0-9_-]{1,64}"
            maxLength={64}
          />
          <small>Letters, numbers, hyphens and underscores.</small>
        </label>

        <label>
          Local Git repository
          <input
            name="repository"
            placeholder="C:\Projects\shipping-service"
            defaultValue={initial?.repository}
            required
          />
          <small>
            Full path to the repository root. Current working files are
            analyzed; a commit is not required.
          </small>
        </label>

        <label>
          Source directories
          <input
            name="paths"
            defaultValue={initial?.code_paths.join(", ") || "src"}
            required
          />
          <small>Relative paths, separated by commas.</small>
        </label>

        <label>
          Current API documentation
          <input
            name="base"
            type="file"
            accept=".json,application/json"
            required={!initial}
          />
          <small>
            {initial
              ? "Leave empty to keep the saved contract."
              : "The OpenAPI JSON used by your current integration."}
          </small>
        </label>

        <label>
          Observed API documentation (optional)
          <input name="target" type="file" accept=".json,application/json" />
          <small>
            {initial
              ? "Leave empty to keep the saved contract."
              : "Leave empty for an unchanged API. Connect a documentation URL under monitoring for live checks."}
          </small>
        </label>

        <div className="form-footer">
          <p>
            Test commands run trusted repository code on this computer. Original
            files stay unchanged. Install your test dependencies in the app’s
            environment first.
          </p>

          <button className="primary-button" disabled={saving}>
            {saving ? "Saving…" : initial ? "Save changes" : "Connect project"}

            <ArrowRight size={16} />
          </button>
        </div>

        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}
      </form>
    </section>
  );
}

function Findings({
  report,

  patch,

  patchError,

  onPatch,

  onCancel,

  onRepair,

  onApply,
  onConnectGitHub,

  initialTab = "summary",
  catalogOnly = report.operation === "scan",

  modelAvailable,
}) {
  const [tab, setTab] = useState(initialTab);
  const [applying, setApplying] = useState(false);
  const appliedNotice = appliedUpdateSummary(report);
  const noticeRef = useRef(null);
  const wasApplied = useRef(Boolean(appliedNotice));
  const isApplied = Boolean(appliedNotice);
  useEffect(() => {
    if (isApplied && !wasApplied.current) {
      noticeRef.current?.focus({preventScroll:true});
      noticeRef.current?.scrollIntoView({behavior:"auto", block:"start"});
    }
    wasApplied.current = isApplied;
  }, [isApplied]);

  async function applyUpdate() {
    if (applying) return;
    setApplying(true);
    try { await onApply(); } finally { setApplying(false); }
  }

  const view = jobPresentation(report);
  const graphReport = graphEvidence(report);

  const summary = resultSummary(report);

  const limitations = [
    ...(report.scan?.limitations || []),

    ...(report.comparison?.limitations || []),
  ];

  const commands = (report.attempts || []).flatMap((attempt) =>
    (attempt.validation || []).map((command) => ({
      ...command,

      attempt: attempt.number,
    })),
  );

  const tabs = [
    ["summary", catalogOnly ? "Endpoints" : "Overview"],
    ...(report.operation === "repair" ? [["activity", "Agent activity"]] : []),

    ["graph", "Impact graph"],

    ...(view.canDownload ? [["patch", "Code changes"]] : []),

    ["checks", "Tests & rules"],

    ...(view.canDownload && report.integration
      ? [["publish", "GitHub draft"]]
      : []),

    ["technical", "Technical details"],
  ];

  const activeTab = tabs.some(([key]) => key === tab) ? tab : "summary";

  function changeTab(value) {
    setTab(value);

    if (value === "patch" && !patch) onPatch();
  }

  function downloadReport() {
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }),
    );

    const anchor = document.createElement("a");

    anchor.href = url;

    anchor.download = `apishield-${report.job_id}.json`;

    anchor.click();

    URL.revokeObjectURL(url);
  }

  return (
    <section
      className="report-panel guided-report"
      aria-labelledby="report-title"
    >
      <div className="section-heading">
        <div>
          <h2 id="report-title">{summary.title}</h2>

          <p>
            {projectDisplayName(report.integration) || "Local command-line run"} ·{" "}
            {date(report.created_at)}
          </p>
        </div>

        {!catalogOnly && <Status job={report} />}

        {view.canDownload && activeTab !== "patch" && (
          <button
            className="primary-button report-review-action"
            onClick={() => changeTab("patch")}
          >
            {isApplied ? "View applied changes" : "Review code change"} <ArrowRight size={16} />
          </button>
        )}
      </div>

      <AppliedUpdateNotice notice={appliedNotice} noticeRef={noticeRef} onGraph={() => changeTab("graph")} />

      <SectionTabs
        label="Result sections"
        tabs={tabs}
        value={activeTab}
        onChange={changeTab}
      />

      {report.operation === "repair" && (
        <div id="panel-activity" role="tabpanel" aria-labelledby="tab-activity" hidden={activeTab !== "activity"} className="result-section">
          <AgentActivity report={report} active={activeTab === "activity"} onCancel={onCancel} onReview={() => changeTab("patch")} />
        </div>
      )}

      <div
        id="panel-graph"
        role="tabpanel"
        aria-labelledby="tab-graph"
        hidden={activeTab !== "graph"}
        className="result-section graph-section"
      >
        <ImpactGraph
          key={graphReport.job_id}
          report={graphReport}
          active={activeTab === "graph"}
        />
      </div>

      <div
        id="panel-summary"
        role="tabpanel"
        aria-labelledby="tab-summary"
        hidden={activeTab !== "summary"}
        className="result-section"
      >
        {!catalogOnly && <ChangeNotice report={report} modelAvailable={modelAvailable} onAskAI={onRepair} />}
        <div hidden={activeTab !== "summary"} className="report-context">
          {view.busy && (
            <div className="running-message" role="status">
              <RefreshCw size={18} className="spin" />

              <p>The job is working in a temporary copy.</p>

              <button className="secondary-button" onClick={onCancel}>
                Cancel run
              </button>
            </div>
          )}

          {report.error && (
            <div className="error-message" role="alert">
              <strong>{view.label}</strong>

              <p>{report.error}</p>

              <p>
                Read the evidence, update Project settings if needed, then start
                a new check.
              </p>
            </div>
          )}

          {report.dirty_source && (
            <p className="report-note">
              Analysis uses your captured current working files.
            </p>
          )}
        </div>

        <RunOverview report={report} catalogOnly={catalogOnly} />
        {report.ai_graph_error && (
          <p className="error-message" role="alert">
            AI interpretation failed: {report.ai_graph_error} The static graph
            remains available.
          </p>
        )}

        {!report.scan && !view.busy && !report.error && (
          <p className="muted">
            This run has no supported call findings. Open Technical details for
            its retained evidence.
          </p>
        )}
      </div>

      {view.canDownload && (
        <div
          id="panel-patch"
          role="tabpanel"
          aria-labelledby="tab-patch"
          hidden={activeTab !== "patch"}
          className="result-section"
        >
          <div className="section-heading">
            <div>
              <h3>{isApplied ? "The applied code change" : "The proposed code change"}</h3>

              <p>Lines marked − are removed; lines marked + are added.</p>
            </div>

            <a
              className="secondary-button"
              href={`/api/jobs/${report.job_id}/patch`}
              download={`apishield-${report.job_id}.patch`}
            >
              <Download size={16} />
              Download patch
            </a>
          </div>

          {patchState(patch, patchError) === "ready" ? (
            <RepairDiff patch={patch} />
          ) : patchError ? (
            <p role="alert">{patchError} Use Reload patch to try again.</p>
          ) : (
            <p role="status">Loading the retained patch…</p>
          )}

          <div className="button-group">
            {report.applied_files &&
              !report.project_workflow &&
              report.proposal_source === "model" &&
              report.application?.status !== "applied" && (
                <button className="primary-button" onClick={applyUpdate} disabled={applying} aria-busy={applying}>
                  {applying ? <>Applying changes… <RefreshCw size={17} className="spin" /></> : <>Apply repair <Wrench size={17} /></>}
                </button>
              )}

            <button className="secondary-button" onClick={onPatch}>
              Reload patch
            </button>

            {report.integration && (
              <button
                className="primary-button"
                onClick={() => setTab("publish")}
              >
                Review GitHub draft <ArrowRight size={17} />
              </button>
            )}
          </div>

          <p className="muted">
            {report.project_workflow ? "Review and merge the GitHub PR to deploy this update to the client machine." : isApplied ? "Changes are applied to your working files. A recovery copy is retained." : "Apply updates current working files without a commit. A recovery copy is retained."}
          </p>
        </div>
      )}

      <div
        id="panel-checks"
        role="tabpanel"
        aria-labelledby="tab-checks"
        hidden={activeTab !== "checks"}
        className="result-section"
      >
        <ChecksPanel report={report} commands={commands} />
      </div>

      {view.canDownload && report.integration && (
        <div
          id="panel-publish"
          role="tabpanel"
          aria-labelledby="tab-publish"
          hidden={activeTab !== "publish"}
          className="result-section"
        >
          {report.project_workflow ? <DeploymentStatus integration={report.integration} jobId={report.job_id} /> : <GitHubPublication
            key={report.job_id}
            integration={report.integration}
            jobId={report.job_id}
            report={report}
            onConnect={onConnectGitHub}
          />}
        </div>
      )}

      <div
        id="panel-technical"
        role="tabpanel"
        aria-labelledby="tab-technical"
        hidden={activeTab !== "technical"}
        className="result-section"
      >
        <TechnicalPanel
          report={report}
          limitations={limitations}
          onDownload={downloadReport}
        />
      </div>
    </section>
  );
}

export default function Workspace() {
  const selection = useMemo(() => createSelectionGate(), []);

  const [workspace, setWorkspace] = useState(null),
    [jobs, setJobs] = useState([]);

  const [integration, setIntegration] = useState(
      () => new URLSearchParams(window.location.search).get("project") || "",
    ),
    [selected, setSelected] = useState("");

  const [report, setReport] = useState(null),
    [patch, setPatch] = useState("");

  const [patchError, setPatchError] = useState("");

  const [overviewTab, setOverviewTab] = useState("summary");

  const [currentInfo, setCurrentInfo] = useState(null);
  const [multiProject, setMultiProject] = useState(null);
  const [catalogOnly, setCatalogOnly] = useState(false);

  const [page, setPage] = useState("workspace"),
    [setupTab, setSetupTab] = useState("contracts");

  const [form, setForm] = useState(false),
    [editing, setEditing] = useState(null);

  const [error, setError] = useState(""),
    [connectionError, setConnectionError] = useState(""),
    [busy, setBusy] = useState(false);

  const [resultFilter, setResultFilter] = useState("");

  const pendingAction = useRef(false);

  const recovery = errorRecovery(error, connectionError);

  useEffect(() => {
    let live = true;

    if (integration && page === "workspace")
      requestJSON(
        `/api/integrations/${encodeURIComponent(integration)}/overview`,
      )
        .then((value) => {
          if (live) setCurrentInfo(value.report);
        })

        .catch(() => {
          /* Explicit overview actions surface failures. */
        });

    return () => {
      live = false;
    };
  }, [integration, page]);

  function choose(id, evidence = null) {
    selection.select(id);

    setSelected(id);

    setReport(evidence);

    setPatch("");

    setPatchError("");
  }

  function selectProject(name) {
    setIntegration(name);

    choose("");

    setForm(false);

    setEditing(null);

    try {
      localStorage.setItem("apishield-project", name);
    } catch {
      /* Storage is optional. */
    }
  }

  function openJob(id, evidence = null, catalog = false) {
    setCatalogOnly(catalog);
    choose(id, evidence);

    setPage("runs");
  }

  const refresh = useCallback(async () => {
    const isCurrent = selection.capture(selected);

    try {
      const [info, history] = await Promise.all([
        requestJSON("/api/workspace"),

        requestJSON("/api/jobs"),
      ]);

      setWorkspace(info);

      setJobs(orderedJobs(history.jobs));

      setIntegration((current) => {
        if (info.integrations.some((item) => item.name === current))
          return current;

        let saved = "";

        try {
          saved = localStorage.getItem("apishield-project") || "";
        } catch {
          /* Storage is optional. */
        }

        return (
          info.integrations.find((item) => item.name === saved)?.name ||
          info.integrations.find((item) => item.example)?.name ||
          info.integrations[0]?.name ||
          ""
        );
      });

      if (selected) {
        const evidence = await requestJSON(`/api/jobs/${selected}`);

        if (isCurrent()) setReport(previous => refreshedJobReport(previous, evidence));
      }

      setConnectionError("");
    } catch (e) {
      setConnectionError(e.message);
    }
  }, [selected, selection]);

  useEffect(() => () => selection.select(""), [selection]);

  useEffect(() => {
    const first = setTimeout(refresh, 0);

    const interval = setInterval(refresh, 3000);

    return () => {
      clearTimeout(first);

      clearInterval(interval);
    };
  }, [refresh]);

  const current = workspace?.integrations.find(
    (item) => item.name === integration,
  );

  const reportProject = workspace?.integrations.find(
    (item) => item.name === report?.integration,
  );

  const recent = projectRuns(jobs, integration);

  const homeActions = dashboardActions(
    integration,
    jobs,
    currentInfo?.integration === integration ? currentInfo.source_hash : null,
    currentInfo?.api_context,
  );

  const active = jobs.some((job) => jobPresentation(job).busy);

  const projectBusy = recent.some((job) => jobPresentation(job).busy);

  async function action(callback) {
    if (pendingAction.current) return;

    pendingAction.current = true;

    setBusy(true);

    setError("");

    try {
      await callback();

      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      pendingAction.current = false;

      setBusy(false);
    }
  }

  async function run(operation, proposal = "model", projectName = integration) {
    if (multiProject?.project_id === projectName && operation === "compare") {
      await action(() => requestJSON(`/api/projects/${encodeURIComponent(projectName)}/check`, {method:"POST"}));
      return;
    }
    if (multiProject?.project_id === projectName && operation === "repair") {
      await action(async () => {
        const value=await requestJSON(`/api/projects/${projectName}/workflows`);
        const workflow=value.workflows.filter(w=>w.state==="awaiting_request").at(-1);
        if(!workflow) throw new Error("Check both providers first; no pending migration is available.");
        const result=await requestJSON(`/api/projects/${projectName}/workflows/${workflow.workflow_id}`,post({action:"generate"}));
        setOverviewTab("activity");openJob(result.job_id,{job_id:result.job_id,integration:projectName,operation:"repair",status:"queued"});
      });
      return;
    }
    setOverviewTab(operation === "repair" ? "activity" : "summary");

    const isCurrent = selection.capture(selected);

    await action(async () => {
      const result = await requestJSON(
        "/api/jobs",

        post({ integration: projectName, operation, proposal }),
      );

      if (!isCurrent()) return;

      if (result.api_context)
        setCurrentInfo((previous) =>
          previous?.integration === projectName
            ? { ...previous, api_context: result.api_context }
            : previous,
        );

      openJob(result.job_id, {
        ...result,

        operation,

        created_at: new Date().toISOString(),
      });
    });
  }

  function connect() {
    setEditing(null);

    setForm(true);

    setSetupTab("contracts");

    setPage("setup");
  }

  function showSetup() {
    setSetupTab("contracts");

    setPage("setup");
  }

  async function tryExample() {
    const example = workspace?.integrations.find((item) => item.example);

    if (example) {
      selectProject(example.name);

      setPage("workspace");

      return;
    }

    await action(async () => {
      const result = await requestJSON("/api/examples/shipping", {
        method: "POST",
      });

      selectProject(result.name);

      setPage("workspace");
    });
  }

  async function exploreCurrent(tab = "summary") {
    if (multiProject?.project_id === integration) {
      await action(async () => {
        const result = await requestJSON(`/api/projects/${encodeURIComponent(integration)}/overview`, {method:"POST"});
        setOverviewTab(tab);
        openJob(result.job_id, {...result, operation:"compare", created_at:new Date().toISOString()}, true);
      });
      return;
    }
    const isCurrent = selection.capture(selected);

    await action(async () => {
      const value = await requestJSON(
        `/api/integrations/${encodeURIComponent(integration)}/overview`,
      );

      if (!isCurrent()) return;

      setCurrentInfo(value.report);

      setOverviewTab(tab);

      openJob(value.report.job_id, value.report, true);
    });
  }

  const navigation = [
    ["workspace", "Overview", LayoutDashboard],

    ["runs", "Activity", History],

    ["setup", "Settings", Settings2],

    ["help", "Help", BookOpen],
  ];

  const titles = {
    workspace: [
      "Overview",

      "Check for API Changes. Explore endpoints and semantic intent.",
    ],

    runs: [
      "Activity",

      "Each check keeps its findings and evidence. Nothing is applied automatically.",
    ],

    setup: [
      "Project settings",

      "Configure one project at a time. Optional tools stay here until you need them.",
    ],

    settings: [
      "AI connection",

      "Connect Google only when you want AI-generated repairs.",
    ],

    help: [
      "A simple way to get started",

      "Try the example first, then follow the same steps with your own project.",
    ],
  };

  function resultRow(job) {
    return (
      <button
        className="guided-run-row"
        key={job.job_id}
        data-job-id={job.job_id}
        onClick={() => openJob(job.job_id, job)}
      >
        <span className="run-operation-icon">
          {job.operation === "scan" ? (
            <Search size={20} />
          ) : job.operation === "compare" ? (
            <GitCompareArrows size={20} />
          ) : (
            <Wrench size={20} />
          )}
        </span>

        <span>
          <strong>
            {job.operation === "scan"
              ? "Code scan"
              : job.operation === "compare"
                ? "API comparison"
                : "Repair review"}
          </strong>

          <small>
            {projectDisplayName(job.integration) || "Local command-line run"} ·{" "}
            {date(job.created_at)}
          </small>
          <span className="run-outcome">{activityOutcome(job)}</span>
        </span>

        <Status job={job} />

        <ChevronRight size={18} aria-hidden="true" />
      </button>
    );
  }

  return (
    <div className="workspace-shell guided-shell">
      <a className="skip-link" href="#workspace-main">
        Skip to workspace
      </a>

      <aside className="workspace-sidebar">
        <a className="workspace-brand" href="/">
          <ShieldCheck size={28} />

          <span>
            APIShield<span className="brand-dot">.</span>
          </span>
        </a>

        <RepositorySwitcher
          projects={workspace?.integrations || []}
          value={integration}
          loading={!workspace}
          onConnect={connect}
          onChoose={(name) => {
            if (
              form &&
              !window.confirm(
                "Switch projects and discard the open project form?",
              )
            )
              return false;

            selectProject(name);

            setResultFilter(name);

            setPage("workspace");

            return true;
          }}
        />

        <button className="sidebar-connect" onClick={connect}>
          <Plus size={18} />
          Connect repository
        </button>

        <nav aria-label="Workspace navigation">
          {navigation.map(([key, label, Icon]) => (
            <button
              key={key}
              className={
                page === key || (key === "setup" && page === "settings")
                  ? "nav-active"
                  : ""
              }
              aria-current={
                page === key || (key === "setup" && page === "settings")
                  ? "page"
                  : undefined
              }
              onClick={() => {
                setPage(key);

                if (key === "runs") {
                  choose("");

                  setResultFilter(integration);
                }
              }}
            >
              <Icon size={19} />

              {label}

              {key === "runs" && active && (
                <span className="active-dot" aria-label="Active jobs" />
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <span className="local-label">
            <span />
            Local application
          </span>

          <a className="banking-demo-link" href={(multiProject?.client_url || current?.client_url) || "/banking"}>
            {(multiProject?.client_url || current?.client_url) ? "CinemaFlow client" : "Banking demo"} <ArrowRight size={16} />
          </a>
        </div>
      </aside>

      <main
        id="workspace-main"
        className={`workspace-main ${page === "runs" && report ? "review-workspace" : ""}`}
      >
        <header className="workspace-header">
          <div>
            <h1>
              {page === "runs" && report
                ? projectDisplayName(report.integration) || "Run review"
                : titles[page][0]}
            </h1>
          </div>

          <div className="header-tools">
            <button
              className="icon-button"
              onClick={refresh}
              aria-label="Refresh workspace"
            >
              <RefreshCw size={18} />
            </button>
          </div>
        </header>

        <section
          className="appearance-settings"
          hidden={page !== "setup" && page !== "settings"}
        >
          <h2>Appearance</h2>

          <ThemeControl />
        </section>

        {(page === "setup" || page === "settings") && (
          <div className="settings-switch">
            <button
              aria-pressed={page === "setup"}
              onClick={() => setPage("setup")}
            >
              <FolderGit2 size={16} /> Project settings
            </button>

            <button
              aria-pressed={page === "settings"}
              onClick={() => setPage("settings")}
            >
              <Settings2 size={16} /> AI connection
            </button>
          </div>
        )}

        {recovery && (
          <div className="error-message" role="alert">
            <strong>Something needs attention</strong>

            <p>{recovery.message}</p>

            <button
              className="secondary-button"
              onClick={() => {
                if (recovery.kind === "action") setError("");
                else refresh();
              }}
            >
              {recovery.button}
            </button>
          </div>
        )}

        {!workspace && !connectionError && (
          <p className="loading-message" role="status">
            Loading your projects…
          </p>
        )}

        {page === "workspace" && workspace && (
          <>
            {!current ? (
              <WorkspaceGuide
                onExample={tryExample}
                onConnect={connect}
                onWorkspace={() => setPage("workspace")}
                busy={busy}
              />
            ) : (
              <>
                <div className="dashboard-home">
                  <header className="project-home-heading">
                    <div>
                      <h2>{projectDisplayName(current.name)}</h2>

                      <span className="project-kind">
                        <FolderGit2 size={15} />

                        {current.kind==='provider' ? 'API provider for '+projectDisplayName(current.project_id) : current.example
                          ? current.name === "banking-example" ? "Banking integration repository" : "Example repository"
                          : "Connected repository"}
                      </span>
                    </div>

                    <button className="secondary-button" onClick={showSetup}>
                      <Settings2 size={16} />
                      Project settings
                    </button>
                  </header>

                  <section
                    className="dashboard-actions"
                    aria-label="Repository actions"
                  >
                    <div className="button-group">
                      <button
                        className="primary-button"
                        disabled={busy || projectBusy}
                        onClick={() =>
                          current.error ? showSetup() : run("compare")
                        }
                      >
                        <GitCompareArrows size={21} />
                        {busy ? "Starting…" : homeActions.primary}
                        <ArrowRight size={20} />
                      </button>

                      <button
                        className="secondary-button"
                        disabled={busy || Boolean(current.error)}
                        onClick={() => exploreCurrent("summary")}
                      >
                        <Search size={19} />
                        API endpoints
                      </button>

                      <button
                        className="secondary-button"
                        disabled={busy || Boolean(current.error)}
                        onClick={() => exploreCurrent("graph")}
                      >
                        <LayoutDashboard size={19} />
                        Semantic graph
                      </button>

                      {homeActions.review && (
                        <button
                          className="secondary-button"
                          disabled={busy}
                          onClick={() => {
                            setOverviewTab("patch");
                            openJob(
                              homeActions.review.job_id,
                              homeActions.review,
                            );
                          }}
                        >
                          Review repair
                        </button>
                      )}
                    </div>

                    {current.error && (
                      <p className="dashboard-action-note" role="alert">
                        {current.error}
                      </p>
                    )}
                  </section>

                  <ProviderOverview key={`providers-${integration}`} integration={integration} onProject={setMultiProject} onOpenJob={id=>{setOverviewTab("activity");openJob(id);}} onInspect={exploreCurrent}/>
                  {multiProject?.project_id !== integration && <IntegrationSnapshot key={integration} integration={integration} report={currentInfo} jobs={jobs} onEndpoints={() => exploreCurrent("summary")} onGraph={() => exploreCurrent("graph")} />}

                  <div className="dashboard-body">
                    <section className="dashboard-activity">
                      <div className="section-heading">
                        <h3>Recent activity</h3>

                        <button
                          className="text-button"
                          onClick={() => {
                            choose("");

                            setResultFilter(integration);

                            setPage("runs");
                          }}
                        >
                          View all
                          <ArrowRight size={16} />
                        </button>
                      </div>

                      {recent.length ? (
                        <div className="dashboard-run-table">
                          <div className="dashboard-table-head">
                            <span>Run</span>

                            <span>Status</span>
                          </div>

                          {recent.slice(0, 3).map(resultRow)}
                        </div>
                      ) : (
                        <div className="dashboard-empty">
                          <History size={28} />

                          <h3>No activity yet</h3>

                          <p>
                            Run your first API check to see its findings here.
                          </p>
                        </div>
                      )}
                    </section>

                    <aside
                      className="dashboard-tools"
                      aria-label="Project tools"
                    >
                      <h3>Project tools</h3>

                      <button onClick={showSetup}>
                        <FolderGit2 size={19} />

                        <span>API contracts & rules</span>

                        <ChevronRight size={16} />
                      </button>

                      <button onClick={() => setPage("settings")}>
                        <Settings2 size={19} />

                        <span>AI connection</span>

                        <ChevronRight size={16} />
                      </button>

                      <a href={(multiProject?.client_url || current?.client_url) || "/banking"}>
                        <LayoutDashboard size={19} />

                        <span>{(multiProject?.client_url || current?.client_url) ? "CinemaFlow client" : "Banking demo"}</span>

                        <ChevronRight size={16} />
                      </a>

                      <button onClick={() => setPage("help")}>
                        <BookOpen size={19} />

                        <span>Usage guide</span>

                        <ChevronRight size={16} />
                      </button>

                      <div className="dashboard-local">
                        <ShieldCheck size={17} />

                        <span>
                          Local workspace
                          <br />
                          <small>
                            {multiProject ? "Updates reach the client after human review, merge and verified deployment." : "Repairs stay proposals until you apply them."}
                          </small>
                        </span>
                      </div>
                    </aside>
                  </div>
                </div>
              </>
            )}
          </>
        )}

        {page === "runs" &&
          workspace &&
          (selected ? (
            <>
              <button
                className="text-button back-link"
                onClick={() => choose("")}
              >
                <ArrowLeft size={17} />
                Back to results
              </button>

              {report ? (
                <Findings
                  key={`${report.job_id}:${overviewTab}`}
                  initialTab={overviewTab}
                  catalogOnly={catalogOnly || report.operation === "scan"}
                  report={report}
                  patch={patch}
                  patchError={patchError}
                  modelAvailable={Boolean(
                    workspace.model_available && reportProject,
                  )}
                  onRepair={
                    reportProject
                      ? () =>
                          run(
                            "repair",

                            "model",

                            report.integration,
                          )
                      : null
                  }
                  onApply={() =>
                    action(async () => {
                      const isCurrent = selection.capture(report.job_id);
                      await applyReviewedUpdate(report, {
                        isCurrent,
                        onApplied: updated => {
                          setReport(updated);
                          if (updated.current_graph_report) setCurrentInfo(updated.current_graph_report);
                        },
                      });
                    })
                  }
                  onConnectGitHub={() => {
                    setIntegration(report.integration);
                    setSetupTab("github");
                    setPage("setup");
                  }}
                  onPatch={() =>
                    action(async () => {
                      const isCurrent = selection.capture(report.job_id);

                      setPatchError("");

                      try {
                        const response = await fetch(
                          `/api/jobs/${report.job_id}/patch`,
                        );

                        if (!response.ok)
                          throw new Error("The retained patch is unavailable.");

                        const text = await response.text();

                        if (isCurrent()) setPatch(text);
                      } catch (e) {
                        if (isCurrent()) setPatchError(e.message);

                        throw e;
                      }
                    })
                  }
                  onCancel={() =>
                    action(() =>
                      requestJSON(`/api/jobs/${report.job_id}/cancel`, {
                        method: "POST",
                      }),
                    )
                  }
                />
              ) : (
                <p role="status">Loading result…</p>
              )}
            </>
          ) : (
            <section className="results-page">
              <div className="results-filter">
                <label htmlFor="results-project">Show results for</label>

                <select
                  id="results-project"
                  value={resultFilter}
                  onChange={(event) => setResultFilter(event.target.value)}
                >
                  <option value="">All projects</option>

                  {workspace.integrations.map((item) => (
                    <option key={item.name} value={item.name}>
                      {projectDisplayName(item.name)}
                    </option>
                  ))}
                </select>
              </div>

              {projectRuns(jobs, resultFilter).length ? (
                <div className="guided-run-list">
                  {projectRuns(jobs, resultFilter).map(resultRow)}
                </div>
              ) : (
                <div className="quiet-empty">
                  <History size={25} />

                  <h2>No results yet.</h2>

                  <p>
                    Run a check from Workspace, then return here to review it.
                  </p>

                  <button
                    className="primary-button"
                    onClick={() => setPage("workspace")}
                  >
                    Go to workspace <ArrowRight size={17} />
                  </button>
                </div>
              )}
            </section>
          ))}

        <section hidden={page !== "setup"} className="project-setup-page">
          {current && (
            <SectionTabs
              label="Project settings sections"
              tabs={[
                ["contracts", "Project & contracts"],

                ["monitor", "Monitoring"],

                ["github", "GitHub"],
              ]}
              value={setupTab}
              onChange={setSetupTab}
            />
          )}

          <div
            id="panel-contracts"
            role="tabpanel"
            aria-labelledby={current ? "tab-contracts" : undefined}
            hidden={setupTab !== "contracts"}
          >
            {form ? (
              <IntegrationForm
                key={editing?.name || "new"}
                initial={editing}
                onClose={() => {
                  setForm(false);

                  setEditing(null);
                }}
                onSaved={(name) => {
                  selectProject(name);

                  setForm(false);

                  setEditing(null);

                  setPage("workspace");

                  refresh();
                }}
              />
            ) : current ? (
              <section className="project-summary">
                <h2>Your connected project</h2>

                <p>
                  APIShield checks current working files in this folder. Keep
                  your old and updated API contracts here in Project settings.
                </p>

                <dl>
                  <dt>Local repository</dt>

                  <dd>{current.repository || current.error}</dd>

                  <dt>Source directories</dt>

                  <dd>{current.code_paths?.join(", ") || "Unavailable"}</dd>

                  <dt>Tests</dt>

                  <dd>
                    {current.test_commands

                      ?.map((command) => command.join(" "))

                      .join(" · ") || "Unavailable"}
                  </dd>
                </dl>

                {current.editable ? (
                  <button
                    className="secondary-button"
                    disabled={busy}
                    onClick={() => {
                      const isCurrent = selection.capture(selected);

                      action(async () => {
                        const config = await requestJSON(
                          `/api/integrations/${encodeURIComponent(current.name)}/config`,
                        );

                        if (isCurrent()) {
                          setEditing(config);

                          setForm(true);
                        }
                      });
                    }}
                  >
                    <Settings2 size={17} />
                    Edit project & contracts
                  </button>
                ) : (
                  <p className="muted">
                    {current.example
                      ? "The example is already configured. Connect your own project when you are ready."
                      : "This project is managed by the server and is read-only here."}
                  </p>
                )}

                <details>
                  <summary>What is an API contract?</summary>

                  <p>
                    A JSON OpenAPI file describing the API’s routes, request
                    fields and responses. Connect the old version and the
                    updated version to check a migration. An ordinary
                    documentation link is not enough.
                  </p>
                </details>
              </section>
            ) : (
              <div className="quiet-empty">
                <h2>Connect a project first.</h2>

                <p>
                  You will need a local Python Git repository, tests and two API
                  contracts.
                </p>

                <button className="primary-button" onClick={connect}>
                  Connect project
                </button>
              </div>
            )}
          </div>

          {current && (
            <>
              <div
                id="panel-monitor"
                role="tabpanel"
                aria-labelledby="tab-monitor"
                hidden={setupTab !== "monitor"}
              >
                <p className="setup-explanation">
                  Optional: check a contract URL on a schedule. Leave the app
                  running for scheduled checks; repairs remain your choice.
                </p>

                <Monitoring
                  key={`monitor-${integration}`}
                  integration={integration}
                  editable={Boolean(current.editable)}
                  modelAvailable={workspace.model_available}
                  onOpenJob={(id) => openJob(id)}
                  onRepairQueued={(id) => {
                    setOverviewTab("activity");
                    openJob(id);

                    refresh();
                  }}
                />
              </div>

              <div
                id="panel-rules"
                role="tabpanel"
                aria-labelledby="tab-rules"
                hidden={setupTab !== "rules"}
              >
                <p>
                  Business intent and missing checks are inferred from source
                  and API documentation during AI repair. No manual rule setup
                  is required.
                </p>
              </div>

              <div
                id="panel-github"
                role="tabpanel"
                aria-labelledby="tab-github"
                hidden={setupTab !== "github"}
              >
                <GitHubTarget
                  key={`github-${integration}`}
                  integration={integration}
                />
              </div>
            </>
          )}
        </section>

        <section
          hidden={page !== "settings"}
          className="settings-panel guided-settings"
        >
          <h2>Connect your AI provider</h2>

          <ModelSettings
            available={workspace?.model_available}
            onSaved={refresh}
          />

          <details>
            <summary>What is sent to Google?</summary>

            <p>
              Generating a repair sends the selected source, API contracts and
              confirmed requirements to Google. Provider charges apply. The
              service account is stored privately on this computer and loaded
              automatically after restarting.
            </p>
          </details>

          <details>
            <summary>Supported projects and test environment</summary>

            <p>
              Current support: committed Python source, JSON OpenAPI contracts
              and supported direct requests/httpx GET/POST calls. Install your
              project’s test dependencies in the app’s Python environment.
              Wrapper clients and dynamic URLs may not be resolved.
            </p>
          </details>
        </section>

        {page === "help" && (
          <WorkspaceGuide
            onExample={tryExample}
            onConnect={connect}
            onWorkspace={() => setPage("workspace")}
            busy={busy}
          />
        )}

        <footer className="workspace-footer">
          {" "}
          <button className="text-button" onClick={() => setPage("help")}>
            Need help getting started?
          </button>
        </footer>
      </main>
    </div>
  );
}
