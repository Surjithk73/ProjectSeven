import test from "node:test";
import assert from "node:assert/strict";
import {
  projectRuns,
  workspaceSuggestion,
  resultSummary,
  observeSelectedTab,
  errorRecovery,
  patchState,
} from "../src/workspace_flow.js";

const project = { name: "shipping", example: false };
const job = (operation, status, extra = {}) => ({
  job_id: "current",
  integration: "shipping",
  operation,
  status,
  created_at: "2026-10-13",
  ...extra,
});
test("internal revalidation stays attached to the original repair, not ordinary history", () => {
  const original = job("repair", "validated", {
    job_id: "original",
    created_at: "2026-10-12",
  });
  const internal = job("repair", "failed", {
    job_id: "verification",
    publication_source_job: "original",
    created_at: "2026-10-14",
  });
  assert.deepEqual(
    projectRuns([internal, original], "shipping").map((item) => item.job_id),
    ["original"],
  );
  assert.equal(
    workspaceSuggestion(project, [internal, original], true).jobId,
    "original",
  );
  assert.deepEqual(
    projectRuns([internal, original], "").map((item) => item.job_id),
    ["original"],
  );
});
test("tab selection reveals horizontal overflow without scrolling the page", () => {
  const calls = [];
  let resize;
  let disconnected = false;
  class Observer {
    constructor(callback) {
      resize = callback;
    }
    observe() {}
    disconnect() {
      disconnected = true;
    }
  }
  let selected = {
    offsetLeft: 420,
    offsetWidth: 100,
    scrollIntoView() {
      throw new Error("Page must not scroll");
    },
  };
  const container = {
    clientWidth: 390,
    scrollLeft: 0,
    querySelector: () => selected,
    scrollTo(options) {
      calls.push(options);
      this.scrollLeft = options.left;
    },
  };
  const stop = observeSelectedTab(container, Observer);
  assert.deepEqual(calls, [{ left: 130, behavior: "auto" }]);
  selected = { offsetLeft: 10, offsetWidth: 100 };
  resize();
  assert.equal(calls[1].left, 10);
  resize();
  assert.equal(calls.length, 2);
  stop();
  assert.equal(disconnected, true);
});
test("action failures are never described as connection retries", () => {
  assert.equal(errorRecovery("Patch unavailable", "").kind, "action");
  assert.equal(
    errorRecovery("Patch unavailable", "Cannot reach app").button,
    "Dismiss message",
  );
  assert.equal(
    errorRecovery("", "Cannot reach app").button,
    "Retry connection",
  );
  assert.equal(errorRecovery("", ""), null);
});
test("a failed patch stays failed after dismissing the general action message", () => {
  assert.equal(patchState("", "Patch unavailable"), "failed");
  assert.equal(patchState("", ""), "loading");
  assert.equal(patchState("diff text", ""), "ready");
});

test("workspace recommends an unpaid comparison for a new project", () => {
  assert.equal(workspaceSuggestion(project, [], true).action, "compare");
});
test("another project’s repair never becomes the selected project’s next step", () => {
  const other = job("repair", "validated", { integration: "payments" });
  assert.equal(workspaceSuggestion(project, [other], true).action, "compare");
  assert.deepEqual(projectRuns([other], "shipping"), []);
});
test("active and failed runs direct users to evidence, without retrying", () => {
  for (const state of [
    "queued",
    "running",
    "failed",
    "needs_input",
    "cancelled",
  ]) {
    const suggestion = workspaceSuggestion(
      project,
      [job("repair", state)],
      true,
    );
    assert.equal(suggestion.action, "review");
    assert.equal(suggestion.jobId, "current");
  }
});
test("only an affected completed comparison offers repair, with explicit model access", () => {
  const affected = job("compare", "completed", {
    impacted_sites: [{ file: "src/client.py" }],
  });
  assert.equal(workspaceSuggestion(project, [affected], true).action, "repair");
  assert.equal(workspaceSuggestion(project, [affected], false).action, "model");
  assert.equal(
    workspaceSuggestion({ ...project, example: true }, [affected], false)
      .action,
    "example",
  );
  assert.equal(
    workspaceSuggestion(
      project,
      [job("compare", "completed", { impacted_sites: [] })],
      true,
    ).action,
    "review",
  );
});
test("a validated repair is reviewed before any publication", () => {
  const suggestion = workspaceSuggestion(
    project,
    [job("repair", "validated")],
    true,
  );
  assert.equal(suggestion.action, "review");
  assert.equal(suggestion.jobId, "current");
});
test("results can show all projects while preserving newest-first ordering", () => {
  const older = job("scan", "completed", { created_at: "2026-10-12" });
  const newer = job("scan", "completed", {
    integration: "payments",
    created_at: "2026-10-14",
  });
  assert.deepEqual(
    projectRuns([older, newer], "").map((x) => x.created_at),
    ["2026-10-14", "2026-10-12"],
  );
});
test("beginner summaries do not claim scans repaired code or tests proved everything", () => {
  assert.match(resultSummary(job("scan", "completed")).title, /API calls/);
  assert.match(
    resultSummary(job("repair", "validated")).description,
    /review/i,
  );
  assert.match(
    resultSummary(job("repair", "no_change")).description,
    /supported/i,
  );
});
