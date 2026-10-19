import test from "node:test";
import assert from "node:assert/strict";
import {
  requestJSON,
  jobPresentation,
  orderedJobs,
  createSelectionGate,
  graphEvidence,
} from "../src/workspace.js";

test("applied repair graphs use rebuilt current evidence; proposals retain impact", () => {
  const current = { job_id: "current", semantic_graph: { nodes: [{ id: "refund-v2" }], edges: [] } };
  const original = { job_id: "repair", semantic_graph: { nodes: [{ id: "refund-v1", impact: "direct" }], edges: [] }, current_graph_report: current };
  assert.equal(graphEvidence(original), original);
  const applied = { ...original, application: { status: "applied" } };
  assert.equal(graphEvidence(applied), current);
  assert.equal(original.semantic_graph.nodes[0].impact, "direct");
  assert.equal(graphEvidence({ ...applied, current_graph_report: undefined }).job_id, "repair");
});

test("HTTP failures surface actionable backend details", async () => {
  await assert.rejects(
    requestJSON("/api/jobs", {}, async () => ({
      ok: false,
      status: 422,
      json: async () => ({ detail: "Commit your source first" }),
    })),
    /Commit your source first/,
  );
});
test("only validated repairs expose patches, missing evidence stays missing", () => {
  assert.equal(
    jobPresentation({ status: "failed", patch: "candidate.patch" }).canDownload,
    false,
  );
  assert.equal(
    jobPresentation({
      status: "validated",
      operation: "repair",
      patch: "candidate.patch",
    }).canDownload,
    true,
  );
  assert.equal(
    jobPresentation({ status: "completed", operation: "scan" }).label,
    "Completed",
  );
  assert.equal(
    jobPresentation({ status: "needs_input" }).label,
    "Needs your input",
  );
});
test("history is newest first without mutating server data", () => {
  const jobs = [
    { job_id: "old", created_at: "2026-10-10" },
    { job_id: "new", created_at: "2026-10-12" },
  ];
  assert.equal(orderedJobs(jobs)[0].job_id, "new");
  assert.equal(jobs[0].job_id, "old");
});

test("late evidence from a previously selected run is discarded, including selecting it again", () => {
  const gate = createSelectionGate();
  gate.select("A");
  const oldA = gate.capture("A");
  gate.select("B");
  const currentB = gate.capture("B");
  assert.equal(oldA(), false);
  assert.equal(currentB(), true);
  gate.select("A");
  assert.equal(oldA(), false);
  assert.equal(currentB(), false);
  assert.equal(gate.capture("A")(), true);
});
test("malformed persisted jobs still have a readable fallback", () => {
  assert.equal(
    jobPresentation({
      job_id: "broken",
      status: "failed",
      error: "Invalid evidence",
    }).operation,
    "Run",
  );
});
