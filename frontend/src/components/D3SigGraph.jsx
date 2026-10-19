import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export default function D3SigGraph({ data, isBroken }) {
  const svgRef = useRef(null);
  
  // Stable string to prevent re-rendering on identical polling data
  const dataString = JSON.stringify({
    nodes: data?.nodes?.map(n => n.id),
    edges: data?.edges?.map(e => [e.source.id || e.source, e.target.id || e.target])
  });

  useEffect(() => {
    if (!data || !data.nodes || data.nodes.length === 0) return;

    // Deep copy data because D3 mutates the nodes and edges
    const graphData = JSON.parse(JSON.stringify(data));

    const width = 800;
    const height = 650;

    // Clear previous graph
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height])
      .attr("style", "max-width: 100%; height: 100%;");

    // Add zoom
    const g = svg.append("g");
    svg.call(d3.zoom().on("zoom", (event) => {
      g.attr("transform", event.transform);
    }));

    // Setup simulation with tuned physics for disconnected graphs
    const simulation = d3.forceSimulation(graphData.nodes)
      .force("link", d3.forceLink(graphData.edges).id(d => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-150))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("x", d3.forceX(width / 2).strength(0.05))
      .force("y", d3.forceY(height / 2).strength(0.05))
      .force("collide", d3.forceCollide().radius(35));

    // Set of broken endpoints
    const brokenEndpoints = new Set(['/charge', '/analytics/log', '/invoice/generate', '/refund']);
    
    // Helper to check if a node is in a broken path
    const isBrokenNode = (d) => {
      if (!d) return false;
      if (brokenEndpoints.has(d.id)) return true;
      if (d.type === 'call_site' && d.code) {
        return Array.from(brokenEndpoints).some(ep => d.code.includes(ep));
      }
      if (d.type === 'intent') {
        // Find if this intent is connected to a broken call site
        const connectedCallSite = graphData.edges.find(e => (e.target.id || e.target) === d.id && e.relation === 'serves');
        if (connectedCallSite) {
          const sourceId = connectedCallSite.source.id || connectedCallSite.source;
          const callSiteNode = graphData.nodes.find(n => n.id === sourceId);
          if (callSiteNode && callSiteNode.code) {
             return Array.from(brokenEndpoints).some(ep => callSiteNode.code.includes(ep));
          }
        }
      }
      return false;
    };

    // Draw links
    const link = g.append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(graphData.edges)
      .join("line")
      .attr("stroke-width", 2)
      .attr("stroke", d => {
        // Highlight the broken path if isBroken is true
        if (isBroken) {
          const sourceId = d.source.id || d.source;
          const targetNode = typeof d.target === 'object' ? d.target : graphData.nodes.find(n => n.id === d.target);
          const sourceBroken = brokenEndpoints.has(sourceId);
          const targetBroken = isBrokenNode(targetNode);
          if (sourceBroken || targetBroken) return '#ef4444'; // red-500
        }
        return '#cbd5e1'; // slate-300
      });

    // Draw nodes
    const node = g.append("g")
      .selectAll("circle")
      .data(graphData.nodes)
      .join("circle")
      .attr("r", d => d.type === 'endpoint' ? 12 : d.type === 'intent' ? 16 : 8)
      .attr("fill", d => {
        if (isBroken && isBrokenNode(d)) {
          return '#ef4444'; // Red for broken path
        }
        if (d.type === 'endpoint') return '#10b981'; // green
        if (d.type === 'intent') return '#8b5cf6'; // purple
        return '#3b82f6'; // blue (call site)
      })
      .attr("stroke", "#fff")
      .attr("stroke-width", 2);

    // Add labels
    const label = g.append("g")
      .selectAll("text")
      .data(graphData.nodes)
      .join("text")
      .text(d => {
        if (d.type === 'endpoint') return d.id;
        if (d.type === 'intent') return d.id;
        return d.id.split(':').pop(); // Just function name for call site
      })
      .attr("font-size", "10px")
      .attr("dx", 15)
      .attr("dy", 4)
      .attr("fill", "#475569")
      .attr("font-family", "sans-serif");

    // Add drag behavior
    node.call(d3.drag()
      .on("start", (event) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      })
      .on("drag", (event) => {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      })
      .on("end", (event) => {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }));

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
        
      label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    });

    return () => simulation.stop();
  }, [dataString, isBroken]);

  return (
    <svg ref={svgRef} className="w-full h-full bg-slate-50/50 rounded-lg cursor-grab active:cursor-grabbing"></svg>
  );
}
