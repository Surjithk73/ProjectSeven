export const themePreference = (value) =>
  ["light", "dark", "system"].includes(value) ? value : "system";
export const resolvedTheme = (preference, darkSystem) =>
  preference === "system" ? (darkSystem ? "dark" : "light") : preference;

export function focusTransform(position, width, height, currentScale) {
  const k = Math.max(0.7, currentScale);
  return {
    x: width / 2 - (position.x + 126) * k,
    y: height / 2 - (position.y + 66) * k,
    k,
  };
}

export function nodeLabel(node) {
  if (node.label) return node.label;
  if (node.kind === "operation") return `${node.method} ${node.endpoint}`;
  if (node.kind === "call") return node.function || "Module call";
  if (node.kind === "requirement") return node.description;
  if (node.kind === "test")
    return node.reference?.split("::").at(-1) || node.function || node.id;
  return node.id;
}

export function networkView(graph, affectedOnly, query = "", allCode = false) {
  let nodes = (graph?.nodes || []).filter(
    (n) => allCode || !["module", "class"].includes(n.kind),
  );
  if (affectedOnly) nodes = nodes.filter((n) => n.impact);
  if (query.trim()) {
    const term = query.trim().toLowerCase();
    const found = new Set(
      nodes
        .filter((n) =>
          `${nodeLabel(n)} ${n.file || ""}`.toLowerCase().includes(term),
        )
        .map((n) => n.id),
    );
    const neighbors = new Set(found);
    for (const e of graph?.edges || [])
      if (found.has(e.from) || found.has(e.to)) {
        neighbors.add(e.from);
        neighbors.add(e.to);
      }
    nodes = nodes.filter((n) => neighbors.has(n.id));
  }
  const ids = new Set(nodes.map((n) => n.id));
  return {
    nodes,
    edges: (graph?.edges || []).filter((e) => ids.has(e.from) && ids.has(e.to)),
    notes: graph?.notes || [],
  };
}

export function impactView(graph, sites = [], affectedOnly = false) {
  if (!graph) return { nodes: [], edges: [], notes: [] };
  const nodes = graph.nodes || [];
  const ids = new Set(nodes.map((n) => n.id));
  const edges = (graph.edges || []).filter(
    (e) => ids.has(e.from) && ids.has(e.to),
  );
  let visible = ids;
  if (affectedOnly) {
    visible = new Set(
      nodes
        .filter(
          (n) =>
            n.kind === "call" &&
            sites.some((s) =>
              ["file", "function", "method", "endpoint"].every(
                (k) => n[k] === s[k],
              ),
            ),
        )
        .map((n) => n.id),
    );
    for (const edge of edges) {
      if (edge.kind === "consumes" && visible.has(edge.from))
        visible.add(edge.to);
      if (edge.kind === "scopes" && visible.has(edge.to))
        visible.add(edge.from);
    }
    for (const edge of edges)
      if (edge.kind === "checked_by" && visible.has(edge.from))
        visible.add(edge.to);
  }
  return {
    nodes: nodes.filter((n) => visible.has(n.id)),
    edges: edges.filter((e) => visible.has(e.from) && visible.has(e.to)),
    notes: graph.notes || [],
  };
}
