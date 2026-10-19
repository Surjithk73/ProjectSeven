import test from "node:test";
import assert from "node:assert/strict";
import * as workspace from "../src/workspace.js";

test("changing a confirmed definition clears its confirmation", () => {
  assert.equal(typeof workspace.editRequirement, "function");
  const rule = {
    id: "exact-weight",
    description: "Exact grams",
    confirmed: true,
    checks: ["tests/test.py::test_x"],
  };
  assert.equal(
    workspace.editRequirement(rule, { description: "Exact cents" }).confirmed,
    false,
  );
  assert.equal(
    workspace.editRequirement(rule, { checks: ["tests/test.py::test_y"] })
      .confirmed,
    false,
  );
});

test("passed prose without completed command evidence is never shown as checked", () => {
  assert.equal(typeof workspace.requirementPresentation, "function");
  const rule = {
    status: "passed",
    confirmed: true,
    checks: ["tests/test.py::test_x"],
    evidence: [],
  };
  assert.notEqual(
    workspace.requirementPresentation(rule).label,
    "Checks passed",
  );
  const evidence = [
    { command: { exit_code: 0 }, result: { passed: true, tests: 1 } },
  ];
  assert.equal(
    workspace.requirementPresentation({ ...rule, evidence }).label,
    "Checks passed",
  );
  assert.notEqual(
    workspace.requirementPresentation({
      ...rule,
      evidence: [
        {
          command: { exit_code: 0, timed_out: true },
          result: { passed: true, tests: 1 },
        },
      ],
    }).label,
    "Checks passed",
  );
});

test("relationships show declared rules and tests alongside resolved consuming calls", () => {
  assert.equal(typeof workspace.requirementRelations, "function");
  const graph = {
    nodes: [
      {
        id: "r",
        kind: "requirement",
        requirement_id: "exact-weight",
        checks: ["tests/test.py::test_x"],
      },
      {
        id: "c",
        kind: "call",
        file: "src/client.py",
        function: "ship",
        method: "POST",
        endpoint: "/ship",
      },
    ],
    edges: [{ kind: "scopes", from: "r", to: "c" }],
  };
  assert.equal(
    workspace.requirementRelations(graph)[0].requirement_id,
    "exact-weight",
  );
  assert.equal(workspace.requirementRelations(graph)[0].endpoint, "/ship");
  assert.deepEqual(workspace.requirementRelations(graph)[0].checks, [
    "tests/test.py::test_x",
  ]);
  assert.deepEqual(workspace.requirementRelations({}), []);
});

test("pending saves freeze definition edits and use the full integration edit token", () => {
  const rule = { description: "Exact grams", confirmed: false };
  assert.deepEqual(
    workspace.editRequirement(rule, { description: "New input" }, true),
    rule,
  );
  assert.equal(typeof workspace.requirementsSaveRequest, "function");
  const request = workspace.requirementsSaveRequest(
    { edit_token: "context-token", requirements_hash: "rules-only" },
    [rule],
  );
  assert.equal(JSON.parse(request.body).expected_hash, "context-token");
});

test("empty requirement evidence never implies that a scan ran tests", async () => {
  const { readFile } = await import("node:fs/promises");
  const source = await readFile(
    new URL("../src/components/Requirements.jsx", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(
    source,
    /This\s+run\s+uses\s+configured\s+test\s+evidence\s+only/,
  );
});
