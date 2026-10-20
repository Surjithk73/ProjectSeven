import { useRef } from "react";
import { FolderGit2, ChevronDown, Check, Plus } from "lucide-react";
import { projectDisplayName, repositoryGroups } from "../workspace";

export default function RepositorySwitcher({
  projects = [],
  value,
  onChoose,
  onConnect,
  loading,
}) {
  const menu = useRef(null),
    trigger = useRef(null);
  const selected = projects.find((project) => project.name === value);
  const groups=repositoryGroups(projects);
  const close = () => {
    if (menu.current) menu.current.open = false;
  };
  return (
    <details
      className="repository-switcher"
      ref={menu}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) close();
      }}
      onKeyDown={(event) => {
        if (event.key === "Escape") {
          close();
          trigger.current?.focus();
          event.preventDefault();
        }
      }}
    >
      <summary ref={trigger} aria-label="Choose repository">
        <span className="repository-mark">
          <FolderGit2 size={21} />
        </span>
        <span className="repository-name">
          <strong title={projectDisplayName(selected?.name)}>
            {projectDisplayName(selected?.name) || "Choose repository"}
          </strong>
          <small>
            {loading
              ? "Loading…"
              : selected?.example
                ? selected.name === "banking-example" ? "Banking integration" : "Example project"
                : selected
                  ? selected.kind==='provider' ? 'API provider · '+projectDisplayName(selected.project_id) : "Client repository"
                  : `${projects.length} connected`}
          </small>
        </span>
        <ChevronDown size={16} className="repository-chevron" />
      </summary>
      <div className="repository-menu">
        {[["Repositories",groups.repositories],["API providers",groups.providers]].map(([label,items])=><div key={label}>
        {items.length>0&&<div className="repository-menu-label">{label}</div>}
        {items.map((project) => (
          <button
            key={project.name}
            aria-pressed={project.name === value}
            onClick={() => {
              if (onChoose(project.name) !== false) {
                close();
                trigger.current?.focus();
              }
            }}
          >
            <FolderGit2 size={18} />
            <span>
              <strong>{projectDisplayName(project.name)}</strong>
              <small>
                {project.kind==='provider' ? 'Provider for '+projectDisplayName(project.project_id) : project.name === "banking-example" ? "Banking integration" : project.example ? "Example project" : "Client repository"}
              </small>
            </span>
            {project.name === value && <Check size={17} />}
          </button>
        ))}</div>)}
        {!projects.length && (
          <p>
            {loading
              ? "Loading repositories…"
              : "No repositories connected yet."}
          </p>
        )}
        <button
          className="repository-connect"
          onClick={() => {
            close();
            trigger.current?.focus();
            onConnect();
          }}
        >
          <Plus size={19} />
          Connect repository
        </button>
      </div>
    </details>
  );
}
