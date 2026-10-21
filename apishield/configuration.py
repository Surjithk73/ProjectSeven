"""Strict versioned configuration; paths are relative to the config file."""
from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess


@dataclass(frozen=True)
class Budgets:
    max_attempts: int = 3
    command_timeout_seconds: float = 120
    job_timeout_seconds: float = 600
    output_limit_bytes: int = 65536

    def __post_init__(self):
        for name, value in asdict(self).items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a positive finite number")
            if name in {"max_attempts", "output_limit_bytes"} and not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")


SECRET_NAME = re.compile(r"secret|token|password|passwd|credential|authorization|api_?key|private_?key|access_?key|(?:^|_)auth(?:_|$)|(?:^|_)key$|database_url|connection_string|(?:^|_)dsn$", re.I)
RESERVED_ENV = {"PATH", "PYTHONPATH", "PYTHONHOME", "HOME", "USERPROFILE", "SYSTEMROOT",
                "WINDIR", "COMSPEC", "TEMP", "TMP", "LD_PRELOAD", "LD_LIBRARY_PATH"}


def relative_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError("source path must be a nonempty relative string")
    normalized = value.replace("\\", "/")
    windows = PureWindowsPath(value)
    parts = normalized.split("/")
    reserved = re.compile(r"(?i)^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)")
    if PurePosixPath(normalized).is_absolute() or windows.drive or windows.root or any(part.casefold() in {"..", ".git"} or reserved.match(part) or (part not in {"", "."} and part[-1:] in {" ", "."}) for part in parts) or ":" in normalized:
        raise ValueError(f"unsafe relative source path: {value}")
    return PurePosixPath(normalized).as_posix()


@dataclass(frozen=True)
class IntegrationConfig:
    repository: Path
    base_spec: Path
    target_spec: Path
    code_paths: list[str]
    setup_commands: list[list[str]] = field(default_factory=list)
    test_commands: list[list[str]] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    budgets: Budgets = field(default_factory=Budgets)
    model: str = "gemini-3.8-flash"
    use_intent: bool = True
    ref: str = "HEAD"
    path: Path | None = None
    version: int = 1
    requirements: list[dict] = field(default_factory=list)
    source_mode: str = 'committed'
    http_bindings: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = asdict(self)
        data.pop("path")
        for name in ("repository", "base_spec", "target_spec"):
            data[name] = str(data[name])
        return data


def load_config(path: str | Path) -> IntegrationConfig:
    path = Path(path).resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read integration config: {exc}") from exc
    keys = {"version", "repository", "ref", "code_paths", "base_spec", "target_spec",
            "setup_commands", "test_commands", "environment", "budgets", "model", "use_intent", "requirements", "source_mode", "http_bindings"}
    if not isinstance(data, dict) or set(data) - keys:
        raise ValueError("unknown or invalid integration config keys")
    if type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError("integration config version must be 1")
    resolved = {}
    for name in ("repository", "base_spec", "target_spec"):
        value = data.get(name)
        if not isinstance(value, str) or not value or "\x00" in value:
            raise ValueError(f"{name} must be a local path")
        candidate = path.parent / value
        if candidate.is_symlink():
            raise ValueError(f"{name} cannot be a symlink")
        resolved[name] = candidate.resolve()
        if name == "repository":
            if not resolved[name].is_dir():
                raise ValueError("repository does not exist")
        else:
            try:
                spec = json.loads(resolved[name].read_text(encoding="utf-8"))
                if not isinstance(spec, dict):
                    raise ValueError("contract must be a JSON object")
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid {name}: {exc}") from exc
    code_paths = data.get("code_paths")
    if not isinstance(code_paths, list) or not code_paths:
        raise ValueError("code_paths must be a nonempty list")
    code_paths = [relative_path(value) for value in code_paths]
    commands = {}
    for name in ("setup_commands", "test_commands"):
        value = data.get(name, [])
        if not isinstance(value, list) or any(not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or "\x00" in arg for arg in argv) or not argv[0].strip() for argv in value):
            raise ValueError(f"{name} must contain argv arrays with an executable")
        commands[name] = value
    environment = data.get("environment", {})
    if not isinstance(environment, dict) or any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) or SECRET_NAME.search(name) or name.upper() in RESERVED_ENV or not isinstance(value, str) or "\x00" in value for name, value in environment.items()):
        raise ValueError("environment permits explicit non-secret settings only")
    budgets = data.get("budgets", {})
    if not isinstance(budgets, dict) or set(budgets) - set(Budgets.__dataclass_fields__):
        raise ValueError("unknown or invalid budgets")
    for name in ("ref", "model"):
        value = data.get(name, "HEAD" if name == "ref" else "gemini-3.8-flash")
        if not isinstance(value, str) or not value.strip() or "\x00" in value or (name == "ref" and value.startswith("-")):
            raise ValueError(f"invalid {name}")
    if not isinstance(data.get("use_intent", True), bool):
        raise ValueError("use_intent must be boolean")
    if data.get('source_mode', 'committed') not in {'committed', 'working'}:
        raise ValueError('source_mode must be committed or working')
    bindings = data.get('http_bindings', {})
    if not isinstance(bindings, dict):
        raise ValueError('Invalid HTTP client bindings')
    for file, binding in bindings.items():
        relative_path(file)
        if not isinstance(binding, dict) or set(binding) != {'provider_id', 'base_url', 'receiver'} or binding['receiver'] != 'self.client':
            raise ValueError('Only explicitly configured self.client HTTP receivers are supported')
        from .projects import identifier
        from .contract_fetch import validate_url
        identifier(binding['provider_id']); validate_url(binding['base_url'], True)
    from .requirements import validate_requirements
    requirements = validate_requirements(data.get('requirements', []), code_paths)
    config = IntegrationConfig(**resolved, code_paths=code_paths, requirements=requirements, **commands,
        environment=dict(environment), budgets=Budgets(**budgets), path=path,
        ref=data.get("ref", "HEAD"), model=data.get("model", "gemini-3.8-flash"), use_intent=data.get("use_intent", True),
        source_mode=data.get('source_mode', 'committed'), http_bindings=bindings)
    from .commands import sanitized_environment
    try:
        top = subprocess.check_output(["git", "-C", str(config.repository), "rev-parse", "--show-toplevel"],
            env=sanitized_environment(config), stderr=subprocess.PIPE,
            timeout=min(10, config.budgets.command_timeout_seconds, config.budgets.job_timeout_seconds))
        if Path(top.decode("utf-8").strip()).resolve() != config.repository:
            raise ValueError("repository must name its local Git checkout root")
    except (OSError, UnicodeError, subprocess.SubprocessError) as exc:
        raise ValueError("repository must be a local Git checkout") from exc
    return config
