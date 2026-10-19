import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCollide,
  forceX,
  forceY,
} from "d3";
import { nodeLabel } from "./workbench.js";

export function nodeGeometry(node) {
  const diameter =
    {
      module: 64,
      community: 82,
      class: 54,
      operation: 56,
      intent: 48,
      requirement: 46,
      function: 42,
      call: 40,
      test: 34,
    }[node.kind] || 28;
  const lines = Math.min(
    6,
    Math.max(1, Math.ceil(Math.min((nodeLabel(node) || "").length, 60) / 10)),
  );
  return {
    diameter,
    width: 170,
    height: diameter + 16 + lines * 20 + (node.kind === "community" ? 24 : 0),
  };
}

export function layoutNetwork(source, edges) {
  if (!source.length) return { positions: {}, width: 800, height: 500 };
  // Large views use a linear-time, relationship-ordered grid instead of physics.
  if (source.length > 160) {
    const byId = new Map(source.map((n) => [n.id, n])),
      adjacent = new Map(source.map((n) => [n.id, []]));
    for (const e of edges)
      if (byId.has(e.from) && byId.has(e.to)) {
        adjacent.get(e.from).push(e.to);
        adjacent.get(e.to).push(e.from);
      }
    const visited = new Set(),
      ordered = [];
    for (const n of source) {
      if (visited.has(n.id)) continue;
      const queue = [n.id];
      visited.add(n.id);
      for (let i = 0; i < queue.length; i++) {
        const id = queue[i];
        ordered.push(byId.get(id));
        for (const next of adjacent.get(id))
          if (!visited.has(next)) {
            visited.add(next);
            queue.push(next);
          }
      }
    }
    const columns = Math.ceil(Math.sqrt(source.length * 1.4)),
      rowHeight = Math.max(...source.map((n) => nodeGeometry(n).height)) + 32;
    return {
      positions: Object.fromEntries(
        ordered.map((n, i) => [
          n.id,
          {
            x: 48 + (i % columns) * 210,
            y: 48 + Math.floor(i / columns) * rowHeight,
            box: nodeGeometry(n),
          },
        ]),
      ),
      width: columns * 210 + 96,
      height: Math.ceil(source.length / columns) * rowHeight + 96,
    };
  }
  const nodes = source.map((n, index) => ({
    ...n,
    box: nodeGeometry(n),
    x: 190 * Math.sqrt(index) * Math.cos(index * 2.4),
    y: 190 * Math.sqrt(index) * Math.sin(index * 2.4),
  }));
  const simulation = forceSimulation(nodes)
    .stop()
    .force(
      "link",
      forceLink(edges.map((e) => ({ source: e.from, target: e.to })))
        .id((n) => n.id)
        .distance(250)
        .strength(0.55),
    )
    .force("charge", forceManyBody().strength(-450))
    .force(
      "collide",
      forceCollide((n) => Math.hypot(85, n.box.height / 2) + 8).iterations(4),
    )
    .force("x", forceX(0).strength(0.025))
    .force("y", forceY(0).strength(0.025));
  simulation.tick(350);
  // Resolve rectangular label bounds after physics; do not clamp to a fixed frame.
  for (let pass = 0; pass < 120; pass++) {
    let moved = false;
    for (let i = 0; i < nodes.length; i++)
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i],
          b = nodes[j];
        const dx = 190 - Math.abs(a.x - b.x);
        const ay = a.y + a.box.height / 2,
          by = b.y + b.box.height / 2;
        const dy = (a.box.height + b.box.height) / 2 + 24 - Math.abs(ay - by);
        if (dx <= 0 || dy <= 0) continue;
        moved = true;
        if (dx < dy) {
          const shift = ((dx + 1) / 2) * (a.x <= b.x ? -1 : 1);
          a.x += shift;
          b.x -= shift;
        } else {
          const shift = ((dy + 1) / 2) * (ay <= by ? -1 : 1);
          a.y += shift;
          b.y -= shift;
        }
      }
    if (!moved) break;
  }
  const left = Math.min(...nodes.map((n) => n.x)) - 36,
    top = Math.min(...nodes.map((n) => n.y)) - 36;
  const positions = Object.fromEntries(
    nodes.map((n) => [n.id, { x: n.x - left, y: n.y - top, box: n.box }]),
  );
  return {
    positions,
    width: Math.max(
      800,
      ...Object.values(positions).map((p) => p.x + 170 + 36),
    ),
    height: Math.max(
      500,
      ...Object.values(positions).map((p) => p.y + p.box.height + 36),
    ),
  };
}

export function fitCamera(positions, width, height, communities = false) {
  const points = Object.values(positions);
  if (!points.length || !width || !height) return null;
  const left = Math.min(...points.map((p) => p.x)) - 48;
  const top = Math.min(...points.map((p) => p.y)) - 48;
  const right = Math.max(...points.map((p) => p.x + p.box.width)) + 48;
  const bottom = Math.max(...points.map((p) => p.y + p.box.height)) + 48;
  const k = Math.max(
    0.15,
    Math.min(
      width / (right - left),
      height / (bottom - top),
      communities ? 0.85 : 1.1,
    ),
  );
  return {
    k,
    x: width / 2 - ((left + right) / 2) * k,
    y: height / 2 - ((top + bottom) / 2) * k,
  };
}

export function keyboardReveal(point, width, height, camera, keyboard) {
  if (!keyboard) return null;
  const left = point.x * camera.k + camera.x,
    top = point.y * camera.k + camera.y;
  if (
    left >= 0 &&
    top >= 0 &&
    left + point.box.width * camera.k <= width &&
    top + point.box.height * camera.k <= height
  )
    return null;
  return {
    k: camera.k,
    x: width / 2 - (point.x + point.box.width / 2) * camera.k,
    y: height / 2 - (point.y + point.box.height / 2) * camera.k,
  };
}
