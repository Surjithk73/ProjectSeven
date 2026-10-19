import test from "node:test";
import assert from "node:assert/strict";
import {
  layoutNetwork,
  nodeGeometry,
  keyboardReveal,
} from "../src/network-layout.js";

test("node size communicates its type", () => {
  assert.ok(
    nodeGeometry({ kind: "module" }).diameter >
      nodeGeometry({ kind: "function" }).diameter,
  );
  assert.ok(
    nodeGeometry({ kind: "operation" }).diameter >
      nodeGeometry({ kind: "test" }).diameter,
  );
});
test("dense network fits its own bounds without overlapping node and label boxes", () => {
  const nodes = Array.from({ length: 48 }, (_, i) => ({
    id: String(i),
    kind: ["module", "operation", "function", "intent", "test"][i % 5],
    label: "Preserve exact transfer value and identity " + i,
  }));
  const edges = nodes.slice(1).map((n) => ({ from: "0", to: n.id }));
  const result = layoutNetwork(nodes, edges);
  for (let i = 0; i < nodes.length; i++)
    for (let j = i + 1; j < nodes.length; j++) {
      const a = result.positions[nodes[i].id],
        b = result.positions[nodes[j].id];
      assert.ok(
        Math.abs(a.x - b.x) >= 170 ||
          a.y + a.box.height <= b.y ||
          b.y + b.box.height <= a.y,
        `${i} overlaps ${j}`,
      );
    }
  assert.ok(
    Object.values(result.positions).every(
      (p) =>
        p.x >= 0 &&
        p.y >= 0 &&
        p.x + 170 <= result.width &&
        p.y + p.box.height <= result.height,
    ),
  );
});
test("pointer focus never changes the camera, and visible keyboard nodes stay put", () => {
  const point = {
    x: 100,
    y: 100,
    box: { width: 170, height: 100, diameter: 30 },
  };
  const camera = { x: 0, y: 0, k: 1 };
  assert.equal(keyboardReveal(point, 600, 400, camera, false), null);
  assert.equal(keyboardReveal(point, 600, 400, camera, true), null);
  const moved = keyboardReveal({ ...point, x: 1000 }, 600, 400, camera, true);
  assert.equal(moved.k, 1);
  assert.equal(moved.x + 1085, 300);
});

import { fitCamera } from "../src/network-layout.js";
test("community camera caps enlargement and centers the diagram", () => {
  const positions = {
    a: { x: 20, y: 30, box: { width: 170, height: 150 } },
    b: { x: 230, y: 200, box: { width: 170, height: 150 } },
  };
  const camera = fitCamera(positions, 1600, 600, true);
  assert.ok(camera.k <= 0.85);
  assert.ok(camera.x > 0 && camera.y > 0);
});
test("settled branches stay close to their actual neighbor, not source list rows", () => {
  const nodes = Array.from({ length: 15 }, (_, i) => ({
    id: String(i),
    kind: "function",
    label: "Function " + i,
  }));
  const edges = [
    { from: "0", to: "14" },
    { from: "14", to: "7" },
    { from: "7", to: "1" },
  ];
  const result = layoutNetwork(nodes, edges);
  const distance = (a, b) =>
    Math.hypot(
      result.positions[a].x - result.positions[b].x,
      result.positions[a].y - result.positions[b].y,
    );
  assert.ok(distance("0", "14") < 450);
});

test('community geometry includes status and conservative wide label allowance',()=>{
 const community=nodeGeometry({kind:'community',label:'W'.repeat(60)});
 assert.ok(community.height>=community.diameter+16+6*20+24);
});
test('large layout preserves all nodes with separate deterministic bounds',()=>{
 const nodes=Array.from({length:1000},(_,i)=>({id:String(i),kind:'function',label:'Wide function '+i}));
 const result=layoutNetwork(nodes,nodes.slice(1).map(n=>({from:'0',to:n.id})));
 assert.equal(Object.keys(result.positions).length,1000);
 const occupied=new Set(Object.values(result.positions).map(p=>`${p.x}:${p.y}`));
 assert.equal(occupied.size,1000);
 assert.ok(Object.values(result.positions).every(p=>p.x+p.box.width<=result.width && p.y+p.box.height<=result.height));
});
