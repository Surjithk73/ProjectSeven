export const communityColors = [
  "#2e67ff",
  "#00cdcc",
  "#f9ff40",
  "#00eeba",
  "#a78bfa",
];

export function sparseEdges(nodes, edges) {
  const parent = new Map(nodes.map((n) => [n.id, n.id]));
  const find = (id) => {
    while (parent.get(id) !== id) id = parent.get(id);
    return id;
  };
  return [...edges]
    .sort((a, b) => (b.count || 1) - (a.count || 1))
    .filter((e) => {
      if (!parent.has(e.from) || !parent.has(e.to)) return false;
      const a = find(e.from),
        b = find(e.to);
      if (a === b) return false;
      parent.set(a, b);
      return true;
    });
}

export function communityProjection(
  graph,
  filtered,
  groups,
  groupId = null,
  focusId = null,
) {
  const membership = new Map(
    groups.flatMap((g, i) =>
      g.members.map((id) => [
        id,
        { ...g, color: communityColors[i % communityColors.length] },
      ]),
    ),
  );
  const colored = filtered.nodes.map((n) => ({
    ...n,
    community: membership.get(n.id)?.id,
    color: membership.get(n.id)?.color,
  }));
  if (groupId) {
    let nodes = colored.filter((n) => n.community === groupId);
    if (focusId) {
      const nearby = new Set([focusId]);
      for (const e of graph.edges)
        if (e.from === focusId || e.to === focusId) {
          nearby.add(e.from);
          nearby.add(e.to);
        }
      nodes = colored.filter(
        (n) => n.community === groupId || nearby.has(n.id),
      );
    }
    const ids = new Set(nodes.map((n) => n.id));
    const edges = graph.edges.filter((e) => ids.has(e.from) && ids.has(e.to));
    return {
      nodes,
      edges: focusId
        ? edges.filter((e) => e.from === focusId || e.to === focusId)
        : sparseEdges(nodes, edges),
      notes: filtered.notes,
      totalEdges: edges.length,
    };
  }
  const nodes = groups
    .map((g, i) => {
      const members = colored.filter((n) => n.community === g.id);
      return {
        id: g.id,
        kind: "community",
        label: g.name,
        description: g.description,
        color: communityColors[i % communityColors.length],
        count: members.length,
        members: members.map((n) => n.id),
        affected: members.filter((n) => n.impact).length,
        impact: members.some((n) => n.impact) ? "potential" : undefined,
      };
    })
    .filter((n) => n.count);
  const ids = new Set(nodes.map((n) => n.id)),
    aggregate = new Map();
  for (const e of filtered.edges) {
    const from = membership.get(e.from)?.id,
      to = membership.get(e.to)?.id;
    if (!from || !to || from === to || !ids.has(from) || !ids.has(to)) continue;
    const inferred = e.basis === "ai_inference";
    const key = [from, to].sort().join("|") + (inferred ? "|ai" : "|recorded");
    if (!aggregate.has(key))
      aggregate.set(key, {
        from,
        to,
        kind: "group_link",
        basis: inferred ? "ai_inference" : "recorded_aggregate",
        count: 0,
      });
    aggregate.get(key).count++;
  }
  return {
    nodes,
    edges: sparseEdges(nodes, [...aggregate.values()]),
    notes: filtered.notes,
    totalEdges: aggregate.size,
  };
}
