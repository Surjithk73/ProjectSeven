import test from "node:test";
import assert from "node:assert/strict";
import {
  monitorPresentation,
  validateMonitorInput,
  monitorSaveRequest,
  baselineDescription,
  monitorEditDraft,
} from "../src/monitoring.js";
import { createSelectionGate } from "../src/workspace.js";

const input = {
  source_url: "https://example.test/openapi.json",
  allow_local: false,
  interval_minutes: 60,
  baseline_mode: "saved",
};

test("monitor states explain what has actually happened", () => {
  assert.equal(
    monitorPresentation({ configured: false }).label,
    "Not configured",
  );
  assert.equal(
    monitorPresentation({ configured: true, enabled: false }).label,
    "Paused",
  );
  assert.equal(
    monitorPresentation({
      configured: true,
      enabled: true,
      active_check: {},
      baseline_hash: null,
    }).label,
    "Initializing",
  );
  assert.equal(
    monitorPresentation({
      configured: true,
      enabled: true,
      active_check: {},
      baseline_hash: "hash",
    }).label,
    "Checking",
  );
  assert.equal(
    monitorPresentation({ configured: true, enabled: true, error: "offline" })
      .label,
    "Check failed",
  );
  assert.equal(
    monitorPresentation({ configured: true, enabled: true }).label,
    "Scheduled",
  );
  assert.ok(
    !monitorPresentation({
      configured: true,
      enabled: true,
      baseline_hash: "hash",
    }).label.includes("repaired"),
  );
});

test("input validation and exact optimistic payload", () => {
  assert.equal(validateMonitorInput(input), null);
  assert.match(validateMonitorInput({ ...input, interval_minutes: 4 }), /5/);
  assert.match(
    validateMonitorInput({ ...input, source_url: "http://127.0.0.1/spec" }),
    /HTTPS/,
  );
  assert.equal(
    validateMonitorInput({
      ...input,
      allow_local: true,
      source_url: "http://127.0.0.1/spec",
    }),
    null,
  );
  const request = monitorSaveRequest(input, 7, true);
  assert.equal(request.method, "PUT");
  assert.deepEqual(JSON.parse(request.body), {
    ...input,
    enabled: true,
    expected_revision: 7,
  });
});

test("baseline choices distinguish existing change from initialization", () => {
  assert.match(baselineDescription("saved"), /saved current contract/);
  assert.match(baselineDescription("first_fetch"), /first download/);
  assert.match(baselineDescription("first_fetch"), /no change alert/);
});

test("late integration responses and actions are discarded", () => {
  const gate = createSelectionGate();
  gate.select("parcel");
  const parcel = gate.capture("parcel");
  gate.select("billing");
  assert.equal(parcel(), false);
  gate.select("parcel");
  assert.equal(parcel(), false);
});

test("an editing draft retains its revision while server polling advances", () => {
  const draft = monitorEditDraft({ ...input, revision: 7 });
  const newer = {
    ...input,
    source_url: "https://new.example/spec",
    revision: 8,
  };
  const request = monitorSaveRequest(
    { ...draft.input, interval_minutes: 10 },
    draft.revision,
    true,
  );
  const body = JSON.parse(request.body);
  assert.equal(body.expected_revision, 7);
  assert.notEqual(body.expected_revision, newer.revision);
  assert.equal(body.source_url, input.source_url);
});
