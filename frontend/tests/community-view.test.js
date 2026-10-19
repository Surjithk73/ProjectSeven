import test from 'node:test';import assert from 'node:assert/strict';
import {communityProjection} from '../src/community-view.js';
test('community overview reduces cycles and preserves source graph',()=>{
  const graph={nodes:['a','b','c'].map(id=>({id,kind:'function',label:id})),edges:[{from:'a',to:'b'},{from:'b',to:'c'},{from:'c',to:'a'}]};
  const groups=graph.nodes.map(n=>({id:'g'+n.id,name:n.id,members:[n.id]}));
  const view=communityProjection(graph,graph,groups);
  assert.equal(view.nodes.length,3);assert.equal(view.edges.length,2);assert.equal(graph.edges.length,3);
});
test('selecting a node exposes its real links while default detail stays sparse',()=>{
  const graph={nodes:['a','b','c'].map(id=>({id,kind:'function'})),edges:[{from:'a',to:'b'},{from:'b',to:'c'},{from:'c',to:'a'}]};
  const groups=[{id:'g',name:'Payments',members:['a','b','c']}];
  assert.equal(communityProjection(graph,graph,groups,'g').edges.length,2);
  assert.deepEqual(communityProjection(graph,graph,groups,'g','a').edges, [graph.edges[0],graph.edges[2]]);
});
