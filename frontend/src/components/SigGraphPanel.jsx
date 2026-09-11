import { Share2 } from 'lucide-react';

function SigGraph({ graph }) {
  if (!graph || !graph.nodes || graph.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-400 text-xs font-mono">
        Graph builds after first agent run...
      </div>
    );
  }

  const nodes = graph.nodes || [];
  const links = graph.links || [];

  // Simple fixed layout for 3 nodes
  const positions = {
    0: { x: 90, y: 30 },
    1: { x: 90, y: 100 },
    2: { x: 90, y: 170 },
  };

  const typeConfig = {
    endpoint:  { color: '#6366f1', label: 'API Endpoint' },
    call_site: { color: '#f59e0b', label: 'Call Site' },
    intent:    { color: '#10b981', label: 'Intent' },
  };

  return (
    <svg viewBox="0 0 180 220" className="w-full h-44">
      {links.map((link, i) => {
        const sourceIdx = typeof link.source === 'number' ? link.source : nodes.findIndex(n => n.id === link.source);
        const targetIdx = typeof link.target === 'number' ? link.target : nodes.findIndex(n => n.id === link.target);
        const sp = positions[sourceIdx] || { x: 90, y: 50 };
        const tp = positions[targetIdx] || { x: 90, y: 150 };
        return (
          <g key={i}>
            <line x1={sp.x} y1={sp.y + 12} x2={tp.x} y2={tp.y - 12}
              stroke="#d1d5db" strokeWidth="1.5" strokeDasharray="4 2" markerEnd="url(#arr)" />
            <text x={(sp.x + tp.x) / 2 + 5} y={(sp.y + tp.y) / 2}
              fontSize="7" fill="#9ca3af" textAnchor="middle">{link.relation}</text>
          </g>
        );
      })}
      <defs>
        <marker id="arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
          <path d="M0,0 L0,6 L6,3 z" fill="#d1d5db" />
        </marker>
      </defs>
      {nodes.map((node, i) => {
        const pos = positions[i] || { x: 90, y: 50 + i * 70 };
        const cfg = typeConfig[node.type] || { color: '#6b7280', label: 'Node' };
        const label = typeof node.id === 'string' ? node.id.split(':')[0].replace('client_app/', '') : `Node ${i}`;
        return (
          <g key={i}>
            <rect x={pos.x - 60} y={pos.y - 12} width="120" height="24"
              rx="6" fill={cfg.color} fillOpacity="0.12" stroke={cfg.color} strokeWidth="1.5" />
            <text x={pos.x} y={pos.y + 4} fontSize="8" fill={cfg.color} textAnchor="middle" fontWeight="600">
              {label.length > 18 ? label.slice(0, 18) + '...' : label}
            </text>
          </g>
        );
      })}
      {/* Legend */}
      {Object.entries(typeConfig).map(([type, cfg], i) => (
        <g key={type}>
          <rect x="4" y={192 + i * 10} width="8" height="8" rx="2" fill={cfg.color} fillOpacity="0.2" stroke={cfg.color} strokeWidth="1" />
          <text x="16" y={199 + i * 10} fontSize="7" fill="#9ca3af">{cfg.label}</text>
        </g>
      ))}
    </svg>
  );
}

export default function SigGraphPanel({ graph }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center">
          <Share2 className="w-4 h-4 text-amber-600" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Semantic Intent Graph</h3>
          <p className="text-xs text-gray-500">Endpoint → Call Site → Intent</p>
        </div>
      </div>
      <SigGraph graph={graph} />
    </div>
  );
}
