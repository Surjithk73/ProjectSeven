import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";
import { select, zoom, zoomIdentity } from "d3";
import {
  Maximize2,
  Minus,
  Plus,
  Network,
  List,
  X,
  Search,
  Sparkles,
  ArrowLeft,
  Layers,
} from "lucide-react";
import { impactView, networkView, nodeLabel } from "../workbench";
import { layoutNetwork, keyboardReveal, fitCamera } from "../network-layout";
import { communityProjection, communityColors } from "../community-view";
import { requestJSON } from "../workspace";

const names = {
  operation: "Endpoint",
  call: "Call site",
  function: "Function",
  intent: "Intent",
  requirement: "Rule",
  module: "File",
  class: "Class",
  test: "Test",
  community: "Community",
};
const noGroups = [];

export default function SemanticNetwork({ report, active }) {
  const [groupId, setGroupId] = useState(null),
    [focusId, setFocusId] = useState(null),
    [source, setSource] = useState("detected"),
    [localAI, setLocalAI] = useState(null),
    [aiBusy, setAiBusy] = useState(false),
    [aiError, setAiError] = useState(""),
    [showInferred, setShowInferred] = useState(false);
  const [affectedOnly, setAffectedOnly] = useState(false),
    [allCode, setAllCode] = useState(false),
    [query, setQuery] = useState("");
  const [mode, setMode] = useState(() =>
    window.matchMedia("(max-width:600px)").matches ? "list" : "graph",
  );
  const [selected, setSelected] = useState(null),
    [customPositions, setPositions] = useState({}),
    [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const viewport = useRef(null),
    controller = useRef(null),
    drawer = useRef(null),
    drag = useRef(null);
  const keyboard = useRef(false),
    positionsRef = useRef({}),
    dragMoved = useRef(false);
  const marker = useId().replace(/:/g, "");
  const graph = useMemo(() => {
    if (report.semantic_graph) return report.semantic_graph;
    const original = impactView(
      report.requirement_graph,
      report.impacted_sites,
      false,
    );
    const affected = new Set(
      impactView(
        report.requirement_graph,
        report.impacted_sites,
        true,
      ).nodes.map((n) => n.id),
    );
    return {
      ...original,
      nodes: original.nodes.map((n) => ({
        ...n,
        impact: affected.has(n.id) ? "potential" : undefined,
      })),
    };
  }, [report]);
  const ai = localAI || report.graph_view?.ai;
  const groups =
    source === "ai" && ai
      ? ai.communities
      : report.graph_view?.communities || noGroups;
  const linkedGraph = useMemo(
    () => ({
      ...graph,
      edges: [
        ...graph.edges,
        ...(source === "ai" && showInferred ? ai?.inferred_edges || [] : []),
      ],
    }),
    [graph, source, showInferred, ai],
  );
  const view = useMemo(() => {
    const filtered = networkView(linkedGraph, affectedOnly, query, allCode);
    return groups.length
      ? communityProjection(linkedGraph, filtered, groups, groupId, focusId)
      : filtered;
  }, [linkedGraph, affectedOnly, query, allCode, groups, groupId, focusId]);
  const currentGroup = groups.find((g) => g.id === groupId);
  async function generateAI() {
    setAiBusy(true);
    setAiError("");
    try {
      const value = await requestJSON(`/api/jobs/${report.job_id}/graph/ai`, {
        method: "POST",
      });
      setLocalAI(value);
      setSource("ai");
      setGroupId(null);
      setFocusId(null);
    } catch (e) {
      setAiError(e.message);
    } finally {
      setAiBusy(false);
    }
  }
  function inspect(node) {
    if (node.kind === "community") {
      setGroupId(node.id);
      setFocusId(null);
      setQuery("");
      return;
    }
    setFocusId(node.id);
    setSelected(node);
  }
  const hasNodes = view.nodes.length > 0;
  const layout = useMemo(
    () =>
      layoutNetwork(
        mode === "graph" ? view.nodes : [],
        mode === "graph" ? view.edges : [],
      ),
    [view, mode],
  );
  const { width, height } = layout;
  const positions = Object.fromEntries(
    Object.entries(layout.positions).map(([id, p]) => [
      id,
      { ...p, ...customPositions[id], box: p.box },
    ]),
  );
  useEffect(() => {
    positionsRef.current = positions;
  }, [positions]);
  useEffect(() => {
    const keys = (e) => {
      if (e.key === "Tab") keyboard.current = true;
    };
    const pointer = () => {
      keyboard.current = false;
    };
    window.addEventListener("keydown", keys, true);
    window.addEventListener("pointerdown", pointer, true);
    return () => {
      window.removeEventListener("keydown", keys, true);
      window.removeEventListener("pointerdown", pointer, true);
    };
  }, []);
  const communityMode = !groupId && groups.length > 0;
  const fit = useCallback(() => {
    const current = controller.current;
    if (!current || !viewport.current) return;
    const camera = fitCamera(
      positionsRef.current,
      viewport.current.clientWidth,
      viewport.current.clientHeight,
      communityMode,
    );
    if (!camera) return;
    current.surface.call(
      current.behavior.transform,
      zoomIdentity.translate(camera.x, camera.y).scale(camera.k),
    );
  }, [communityMode]);
  useEffect(() => {
    if (!active || mode !== "graph" || !viewport.current) return;
    const behavior = zoom()
      .scaleExtent([0.15, 3])
      .filter(
        (e) =>
          !drag.current &&
          !e.target.closest("button") &&
          (!e.ctrlKey || e.type === "wheel") &&
          !e.button,
      )
      .on("zoom", (e) => setTransform(e.transform));
    const surface = select(viewport.current).call(behavior);
    controller.current = { surface, behavior };
    const observer = new ResizeObserver(fit);
    observer.observe(viewport.current);
    fit();
    return () => {
      observer.disconnect();
      surface.on(".zoom", null);
      controller.current = null;
    };
  }, [active, mode, width, height, hasNodes, fit, groupId]);
  useEffect(() => {
    if (selected && drawer.current && !drawer.current.open)
      drawer.current.showModal();
  }, [selected]);
  function focus(node) {
    const p = positions[node.id],
      current = controller.current;
    if (!p || !current) return;
    const target = keyboardReveal(
      p,
      viewport.current.clientWidth,
      viewport.current.clientHeight,
      transform,
      keyboard.current && !drag.current,
    );
    if (!target) return;
    current.surface.call(
      current.behavior.transform,
      zoomIdentity.translate(target.x, target.y).scale(target.k),
    );
  }
  const connected = selected
    ? linkedGraph.edges.filter(
        (e) => e.from === selected.id || e.to === selected.id,
      )
    : [];
  return (
    <div className="impact-surface semantic-network">
      <div className="impact-toolbar">
        <div className="community-heading">
          {groupId ? (
            <button
              className="graph-back icon-button"
              aria-label="Back to all groups"
              onClick={() => {
                setGroupId(null);
                setFocusId(null);
                setSelected(null);
              }}
            >
              <ArrowLeft size={19} />
            </button>
          ) : (
            <Layers size={22} />
          )}
          <div>
            <h3>{currentGroup?.name || "Semantic map"}</h3>
            <span className="graph-source-badge">
              {view.nodes.length} {groupId ? "nodes" : "groups"} ·{" "}
              {source === "ai" && ai ? "AI semantic" : "Code relationships"}
            </span>
          </div>
        </div>
        <div className="graph-primary-tools">
          {ai && (
            <select
              aria-label="Graph interpretation"
              value={source}
              onChange={(e) => {
                setSource(e.target.value);
                setGroupId(null);
                setFocusId(null);
                setSelected(null);
              }}
            >
              <option value="detected">Detected</option>
              <option value="ai">AI semantic</option>
            </select>
          )}
          <div className="view-toggle" role="group" aria-label="Graph display">
            <button
              aria-pressed={mode === "graph"}
              onClick={() => setMode("graph")}
            >
              <Network size={16} />
              Graph
            </button>
            <button
              aria-pressed={mode === "list"}
              onClick={() => setMode("list")}
            >
              <List size={16} />
              List
            </button>
          </div>
          <button
            className="primary-button"
            disabled={aiBusy || !report.graph_view?.can_generate}
            onClick={generateAI}
          >
            <Sparkles size={16} />
            {aiBusy ? "Interpreting…" : "Generate AI graph"}
          </button>
        </div>
      </div>
      <div className="graph-controls">
        <label className="graph-search">
          <Search size={18} />
          <input
            aria-label="Search graph"
            placeholder="Find code or endpoint"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <div className="graph-filter-controls">
          <label className="graph-filter">
            <input
              type="checkbox"
              checked={allCode}
              onChange={(e) => setAllCode(e.target.checked)}
            />
            All code
          </label>
          <label className="graph-filter">
            <input
              type="checkbox"
              checked={affectedOnly}
              onChange={(e) => setAffectedOnly(e.target.checked)}
            />
            Affected
          </label>
          {source === "ai" && ai?.inferred_edges?.length > 0 && (
            <label className="graph-filter">
              <input
                type="checkbox"
                checked={showInferred}
                onChange={(e) => setShowInferred(e.target.checked)}
              />
              Inferred links
            </label>
          )}
        </div>
        {mode === "graph" && (
          <div className="graph-camera-controls">
            <button className="secondary-button" onClick={fit}>
              <Maximize2 size={16} />
              Fit
            </button>
            <button
              className="icon-button"
              aria-label="Zoom out"
              onClick={() =>
                controller.current?.surface.call(
                  controller.current.behavior.scaleBy,
                  1 / 1.2,
                )
              }
            >
              <Minus size={17} />
            </button>
            <button
              className="icon-button"
              aria-label="Zoom in"
              onClick={() =>
                controller.current?.surface.call(
                  controller.current.behavior.scaleBy,
                  1.2,
                )
              }
            >
              <Plus size={17} />
            </button>
          </div>
        )}
      </div>
      {aiError && (
        <p className="error-message" role="alert">
          {aiError}
        </p>
      )}
      {!report.graph_view?.can_generate && (
        <p className="graph-ai-setup">
          Configure Gemini in Settings to generate an AI interpretation.
        </p>
      )}
      {!view.nodes.length ? (
        <div className="graph-empty">No matching relationships.</div>
      ) : mode === "list" ? (
        <div className="network-list graph-list-surface">
          {view.nodes.map((n) => (
            <button
              key={n.id}
              className={`network-row kind-${n.kind} ${n.impact ? "is-affected" : ""}`}
              onClick={() => inspect(n)}
              style={{ "--node-color": n.color }}
            >
              <i />
              {nodeLabel(n)}
              <small>{names[n.kind]}</small>
            </button>
          ))}
        </div>
      ) : (
        <div
          className="impact-viewport"
          ref={viewport}
          aria-label="Semantic graph. Drag nodes or canvas; select a node to inspect code."
        >
          <div
            className="impact-plane"
            style={{
              width,
              height,
              transform: `translate(${transform.x}px,${transform.y}px) scale(${transform.k})`,
            }}
          >
            <svg width={width} height={height} aria-hidden="true">
              <defs>
                <marker
                  id={marker}
                  viewBox="0 0 10 10"
                  refX="9"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto"
                >
                  <path d="M0 0 L10 5 L0 10z" />
                </marker>
              </defs>
              {view.edges.map((e, index) => {
                const a = positions[e.from],
                  b = positions[e.to];
                if (!a || !b) return null;
                const red =
                  view.nodes.find((n) => n.id === e.from)?.impact &&
                  view.nodes.find((n) => n.id === e.to)?.impact;
                const ax = a.x + a.box.width / 2,
                  ay = a.y + a.box.diameter / 2,
                  bx = b.x + b.box.width / 2,
                  by = b.y + b.box.diameter / 2;
                const length = Math.max(1, Math.hypot(bx - ax, by - ay)),
                  dx = (bx - ax) / length,
                  dy = (by - ay) / length;
                return (
                  <path
                    key={index}
                    className={`network-edge ${red ? "affected-edge" : ""} ${e.basis === "ai_inference" ? "ai-edge" : ""} ${(e.basis || "").includes("declaration") ? "declared-edge" : ""}`}
                    d={`M${ax + dx * (a.box.diameter / 2 + 3)},${ay + dy * (a.box.diameter / 2 + 3)} L${bx - dx * (b.box.diameter / 2 + 3)},${by - dy * (b.box.diameter / 2 + 3)}`}
                    markerEnd={
                      e.kind === "group_link" ? undefined : `url(#${marker})`
                    }
                  />
                );
              })}
            </svg>
            {view.nodes.map((n) => {
              const p = positions[n.id];
              if (!p) return null;
              return (
                <button
                  key={n.id}
                  className={`network-node kind-${n.kind} ${n.impact ? "is-affected" : ""}`}
                  style={{
                    left: p.x,
                    top: p.y,
                    width: p.box.width,
                    "--node-diameter": `${p.box.diameter}px`,
                    "--node-color": n.color,
                  }}
                  title={nodeLabel(n)}
                  aria-label={`Inspect ${names[n.kind]}: ${nodeLabel(n)}${n.impact ? ", affected" : ""}`}
                  onFocus={(e) => {
                    if (e.currentTarget.matches(":focus-visible")) focus(n);
                  }}
                  onPointerDown={(e) => {
                    e.stopPropagation();
                    keyboard.current = false;
                    dragMoved.current = false;
                    e.currentTarget.setPointerCapture(e.pointerId);
                    drag.current = {
                      id: n.id,
                      x: e.clientX,
                      y: e.clientY,
                      p,
                      scale: transform.k,
                      moved: false,
                    };
                  }}
                  onPointerMove={(e) => {
                    const d = drag.current;
                    if (d?.id !== n.id) return;
                    const dx = (e.clientX - d.x) / d.scale,
                      dy = (e.clientY - d.y) / d.scale;
                    if (Math.abs(dx) + Math.abs(dy) > 4) d.moved = true;
                    setPositions((old) => ({
                      ...old,
                      [n.id]: { ...d.p, x: d.p.x + dx, y: d.p.y + dy },
                    }));
                  }}
                  onPointerUp={(e) => {
                    dragMoved.current = Boolean(drag.current?.moved);
                    drag.current = null;
                    if (e.currentTarget.hasPointerCapture(e.pointerId))
                      e.currentTarget.releasePointerCapture(e.pointerId);
                  }}
                  onPointerCancel={() => {
                    drag.current = null;
                    dragMoved.current = false;
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ")
                      dragMoved.current = false;
                  }}
                  onClick={() => {
                    if (!dragMoved.current) inspect(n);
                    dragMoved.current = false;
                  }}
                >
                  <i>{n.kind === "community" ? n.count : null}</i>
                  <span>
                    {nodeLabel(n).length > 60
                      ? nodeLabel(n).slice(0, 57) + "…"
                      : nodeLabel(n)}
                  </span>
                  {n.kind === "community" && (
                    <small>
                      {n.affected
                        ? `${n.affected} affected`
                        : "No detected impact"}
                    </small>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
      <div className="impact-bottom">
        <p className="network-legend">
          {groups.map((g, i) => (
            <span
              key={g.id}
              style={{
                "--node-color": communityColors[i % communityColors.length],
              }}
            >
              <i />
              {g.name}
            </span>
          ))}
          <span className="affected-key">Red outline · affected</span>
          {showInferred && source === "ai" && (
            <span>Dashed · AI inference</span>
          )}
          {!groups.length && (
            <>
              <span className="kind-operation">
                <i />
                Endpoint
              </span>
              <span className="kind-function">
                <i />
                Code
              </span>
              <span className="kind-intent">
                <i />
                Intent
              </span>
              <span className="is-affected">
                <i />
                Affected
              </span>
            </>
          )}
        </p>
      </div>
      <details className="graph-notes">
        <summary>Coverage · {view.nodes.length} nodes</summary>
        {view.notes.map((n, i) => (
          <p key={i}>
            {n.file ? `${n.file}: ` : ""}
            {n.reason}
          </p>
        ))}
        <p>
          The overview shows a sparse set of recorded group connections.
          Additional links remain available when a node is selected.
        </p>
        {source === "ai" && ai && (
          <>
            <p>
              AI interpretation · {ai.model} · {ai.created_at}
            </p>
            {ai.communities.map((g) => (
              <p key={g.id}>
                <strong>{g.name}:</strong> {g.description}
              </p>
            ))}
          </>
        )}
      </details>
      <dialog
        ref={drawer}
        className="node-drawer"
        aria-labelledby="node-drawer-title"
        onClose={() => setSelected(null)}
        onClick={(e) => {
          if (e.target === drawer.current) drawer.current.close();
        }}
      >
        {selected && (
          <>
            <header>
              <span>{names[selected.kind]}</span>
              <button
                className="icon-button"
                aria-label="Close node details"
                onClick={() => drawer.current.close()}
              >
                <X size={20} />
              </button>
            </header>
            <h2 id="node-drawer-title">{nodeLabel(selected)}</h2>
            {selected.file && (
              <p>
                <code>
                  {selected.file}
                  {selected.line ? `:${selected.line}` : ""}
                </code>
              </p>
            )}
            {selected.impact && (
              <p className="node-impact">
                {selected.impact_reason || "Connected to an affected API call."}
              </p>
            )}
            {selected.code && (
              <pre className="node-code">
                <code>{selected.code}</code>
              </pre>
            )}
            <h3>Connections</h3>
            {connected.map((e, i) => {
              const n = graph.nodes.find(
                (n) => n.id === (e.from === selected.id ? e.to : e.from),
              );
              return (
                n && (
                  <button
                    className="node-connection"
                    key={i}
                    onClick={() => setSelected(n)}
                  >
                    <strong>{e.kind.replaceAll("_", " ")}</strong>
                    <span>{nodeLabel(n)}</span>
                    <small>{e.basis.replaceAll("_", " ")}</small>
                    {e.reason && (
                      <small>
                        {e.reason} · AI score {e.confidence}
                      </small>
                    )}
                  </button>
                )
              );
            })}
            {!connected.length && <p>No resolved connections.</p>}
          </>
        )}
      </dialog>
    </div>
  );
}
