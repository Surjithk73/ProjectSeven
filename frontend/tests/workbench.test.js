import test from "node:test";
import assert from "node:assert/strict";
import {
  impactView,
  nodeLabel,
  themePreference,
  resolvedTheme,
  focusTransform,
  networkView,
} from "../src/workbench.js";

test("repository view preserves real impact flags and search context without mutating evidence", () => {
  const graph = {
    nodes: [
      { id: "m", kind: "module", label: "bank.py" },
      { id: "f", kind: "function", label: "pay", impact: "direct" },
      { id: "u", kind: "function", label: "other" },
    ],
    edges: [{ from: "m", to: "f", kind: "contains" }],
  };
  assert.deepEqual(
    networkView(graph, true).nodes.map((n) => n.id),
    ["f"],
  );
  assert.deepEqual(
    networkView(graph, false, "pay", true).nodes.map((n) => n.id),
    ["m", "f"],
  );
  assert.equal(graph.nodes.length, 3);
});

test("keyboard focus centers a node that was panned out of view", () => {
  const transform = focusTransform({ x: 920, y: 600 }, 390, 300, 0.2);
  assert.equal(transform.k, 0.7);
  assert.equal(transform.x + (920 + 126) * transform.k, 195);
  assert.equal(transform.y + (600 + 66) * transform.k, 150);
});

const graph = {
  nodes: [
    { id: "op", kind: "operation", method: "POST", endpoint: "/labels" },
    {
      id: "call",
      kind: "call",
      file: "src/parcel.py",
      function: "create_label",
      method: "POST",
      endpoint: "/labels",
    },
    {
      id: "other",
      kind: "call",
      file: "src/other.py",
      function: "other",
      method: "GET",
      endpoint: "/other",
    },
    {
      id: "rule",
      kind: "requirement",
      description: "Preserve exact grams",
      requirement_id: "weight",
      confirmed: true,
    },
    {
      id: "test",
      kind: "test",
      reference: "tests/test_parcel.py::test_weight",
    },
  ],
  edges: [
    { from: "call", to: "op", kind: "consumes", basis: "scanner" },
    {
      from: "rule",
      to: "call",
      kind: "scopes",
      basis: "developer_declaration",
    },
    {
      from: "rule",
      to: "test",
      kind: "checked_by",
      basis: "developer_declaration",
    },
    { from: "missing", to: "call", kind: "unknown" },
  ],
  notes: [{ reason: "Dynamic URL unresolved" }],
};
test("affected graph retains only real related nodes and exact evidence edges", () => {
  const view = impactView(graph, [graph.nodes[1]], true);
  assert.deepEqual(
    view.nodes.map((n) => n.id),
    ["op", "call", "rule", "test"],
  );
  assert.deepEqual(view.edges, graph.edges.slice(0, 3));
  assert.deepEqual(view.notes, graph.notes);
  assert.equal(graph.nodes.length, 5);
});
test("no affected calls means an empty focus, while all preserves supported nodes", () => {
  assert.equal(impactView(graph, [], true).nodes.length, 0);
  assert.equal(impactView(graph, [], false).nodes.length, 5);
  assert.deepEqual(impactView(null, [], false), {
    nodes: [],
    edges: [],
    notes: [],
  });
});
test("graph labels retain operation method, exact source and declaration identity", () => {
  assert.equal(nodeLabel(graph.nodes[0]), "POST /labels");
  assert.equal(nodeLabel(graph.nodes[1]), "create_label");
  assert.equal(nodeLabel(graph.nodes[3]), "Preserve exact grams");
  assert.equal(nodeLabel(graph.nodes[4]), "test_weight");
});
test("theme preference defaults safely, and system follows OS while explicit choices win", () => {
  for (const invalid of [null, "undefined", "sepia"])
    assert.equal(themePreference(invalid), "system");
  assert.equal(themePreference("dark"), "dark");
  assert.equal(resolvedTheme("system", true), "dark");
  assert.equal(resolvedTheme("system", false), "light");
  assert.equal(resolvedTheme("light", true), "light");
  assert.equal(resolvedTheme("dark", false), "dark");
});
