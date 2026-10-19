import { test } from "node:test";
import assert from "node:assert/strict";
import { operationRows, definitionSection } from "../src/overview-view.js";
test("unchanged endpoints retain both versions and removed/added endpoints remain browsable", () => {
  const op = (endpoint) => ({
    method: "GET",
    endpoint,
    definition: {
      responses: { 200: { description: "OK" } },
      security: [{ key: [] }],
    },
  });
  const rows = operationRows({
    before: { operations: [op("/same"), op("/old")] },
    after: { operations: [op("/same"), op("/new")] },
    changes: [
      { method: "GET", endpoint: "/old", status: "removed" },
      { method: "GET", endpoint: "/new", status: "added" },
    ],
  });
  assert.equal(rows.length, 3);
  assert.ok(rows[0].before && rows[0].after);
  assert.equal(rows[0].status, "unchanged");
  assert.equal(rows[1].after, undefined);
  assert.equal(rows[2].status, "added");
  assert.deepEqual(
    definitionSection(rows[0].before, "details").operation.security,
    [{ key: [] }],
  );
});
test("request view preserves required flags and inherited path parameters", () => {
  const op = {
    definition: {
      requestBody: { required: true, content: {} },
      parameters: [{ name: "query" }],
    },
    path_settings: { parameters: [{ name: "account" }] },
  };
  assert.equal(definitionSection(op, "request").requestBody.required, true);
  assert.equal(definitionSection(op, "request").parameters.length, 2);
});

import { pairedLines } from "../src/overview-view.js";
test("comparison highlights additions and removals without coloring unchanged duplicate braces", () => {
  const lines = pairedLines(
    { schema: { type: "integer", description: "same" } },
    { schema: { type: "string", description: "same", format: "money" } },
  );
  assert.ok(
    lines.before.some(
      (l) => l.type === "removed" && l.text.includes("integer"),
    ),
  );
  assert.ok(
    lines.after.some((l) => l.type === "added" && l.text.includes("string")),
  );
  assert.ok(
    lines.after.some((l) => l.type === "added" && l.text.includes("money")),
  );
  assert.ok(
    lines.before.some(
      (l) => l.type === "same" && l.text.includes("description"),
    ),
  );
  assert.ok(
    lines.before.some((l) => l.type === "same" && l.text.trim() === "}"),
  );
  assert.ok(
    pairedLines({ x: 1 }, { x: 1 }).after.every((l) => l.type === "same"),
  );
});
