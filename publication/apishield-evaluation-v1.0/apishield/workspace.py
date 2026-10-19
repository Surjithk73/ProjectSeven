"""Export a validated committed tree without reading dirty working files."""
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import hashlib
import shutil

from .configuration import relative_path
from .jobs import atomic_json


def _git(job, *args, binary=False, input_data=None):
    from .commands import _WindowsTree, _stop, sanitized_environment
    job.check()
    deadline = time.monotonic() + min(job.config.budgets.command_timeout_seconds, job.remaining())
    process = tree = None
    # Files avoid pipe deadlocks and allow cancellation while Git reads a large tree.
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr, tempfile.TemporaryFile() as stdin:
        if input_data is not None:
            stdin.write(input_data)
            stdin.seek(0)
        try:
            if os.name == "nt":
                tree = _WindowsTree()
            process = subprocess.Popen(["git", "-C", str(job.config.repository), *args],
                env=sanitized_environment(job.config), stdin=stdin, stdout=stdout, stderr=stderr,
                start_new_session=tree is None,
                creationflags=(0x4 | subprocess.CREATE_NEW_PROCESS_GROUP) if tree else 0)
            if tree:
                tree.attach_and_resume(process)
            while process.poll() is None:
                job.check()
                if time.monotonic() >= deadline:
                    raise ValueError("local Git snapshot command timed out")
                time.sleep(0.02)
            if process.returncode:
                stderr.seek(0)
                raise ValueError(f"local Git snapshot failed: {stderr.read(4096).decode('utf-8', errors='replace')}")
        except OSError as exc:
            raise ValueError(f"local Git snapshot failed: {exc}") from exc
        finally:
            if process is not None:
                _stop(process, tree)
            elif tree:
                tree.stop()
        stdout.seek(0)
        output = stdout.read()
    job.check()
    return output if binary else output.decode("utf-8", errors="strict").strip()


def _secret(name: str, content: bytes) -> bool:
    lower = Path(name).name.lower()
    return (lower == ".env" or lower.startswith(".env.") or lower.endswith((".pem", ".key", ".p12", ".pfx"))
        or lower in {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
        or b"PRIVATE KEY-----" in content)


def prepare_workspace(job) -> dict:
    job.check()
    if job._restore_contracts():
        raise ValueError("contract snapshots were modified; original snapshots restored")
    repo = job.config.repository.resolve()
    top = Path(_git(job, "rev-parse", "--show-toplevel")).resolve()
    if top != repo:
        raise ValueError("repository must name its Git checkout root")
    if job.config.source_mode == 'working':
        return capture_working_snapshot(job)
    if job._source_metadata:
        source_commit = job._source_metadata["source_commit"]
        dirty = job._source_metadata["dirty_source"]
    else:
        source_commit = _git(job, "rev-parse", "--verify", f"{job.config.ref}^{{commit}}")
        dirty = bool(_git(job, "status", "--porcelain", "--untracked-files=all"))
    evidence = {"source_commit": source_commit, "dirty_source": dirty, "excluded_files": [],
        "base_spec_hash": job._initial["base_spec_hash"],
        "target_spec_hash": job._initial["target_spec_hash"]}
    job._source_metadata = json.loads(json.dumps(evidence))
    atomic_json(job.path / "source.json", evidence)
    entries = _git(job, "ls-tree", "-rz", source_commit, binary=True).split(b"\0")
    blobs = []
    destinations = set()
    for entry in entries:
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, oid = metadata.split(b" ")
        name = relative_path(raw_path.decode("utf-8"))
        if mode == b"120000":
            raise ValueError("Git symlink entries are unsupported")
        if mode == b"160000":
            raise ValueError("Git submodule entries are unsupported")
        if mode not in {b"100644", b"100755"} or kind != b"blob":
            raise ValueError("unsupported Git tree entry")
        destination = job.workspace / name
        if job.workspace.resolve() not in destination.resolve().parents:
            raise ValueError("Git tree path escape")
        canonical = str(destination).casefold()
        if canonical in destinations:
            raise ValueError("Git tree has colliding paths")
        destinations.add(canonical)
        blobs.append((oid, name, destination, mode))
    # Read raw objects: git archive's export-ignore/export-subst attributes alter committed bytes.
    output = _git(job, "cat-file", "--batch", binary=True,
                  input_data=b"".join(oid + b"\n" for oid, _, _, _ in blobs))
    stream = io.BytesIO(output)
    files = []
    excluded = []
    for oid, name, destination, mode in blobs:
        job.check()
        header = stream.readline().rstrip(b"\n").split(b" ")
        if len(header) != 3 or header[:2] != [oid, b"blob"]:
            raise ValueError("invalid Git blob snapshot response")
        size = int(header[2])
        content = stream.read(size)
        if len(content) != size or stream.read(1) != b"\n":
            raise ValueError("truncated Git blob snapshot response")
        if _secret(name, content):
            excluded.append(name)
        else:
            files.append((destination, content, int(mode, 8)))
    if stream.read(1):
        raise ValueError("unexpected Git blob snapshot data")
    if job.workspace.exists():
        job.cleanup()
    job.workspace.mkdir()
    for destination, content, mode in files:
        job.check()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        destination.chmod(mode & 0o777)
    evidence["excluded_files"] = sorted(excluded)
    job._source_metadata = json.loads(json.dumps(evidence))
    atomic_json(job.path / "source.json", evidence)
    job.event("workspace_prepared", **evidence)
    return evidence


def working_files(job):
    """Inventory eligible current bytes; never traverse dependency or secret trees."""
    repo = job.config.repository.resolve()
    names = _git(job, 'ls-files', '-z', '--cached', '--others', '--exclude-standard', binary=True)
    excluded_parts = {'.git', 'node_modules', 'venv', '.venv', '__pycache__', '.pytest_cache',
                      '.project-backups', '.app-logs', 'dist', 'build'}
    files, excluded, total, destinations = {}, [], 0, set()
    for raw in sorted(set(names.split(b'\0')) - {b''}):
        job.check()
        name = relative_path(raw.decode('utf-8'))
        path = repo / name
        if any(part.casefold() in excluded_parts for part in Path(name).parts):
            excluded.append(name)
            continue
        if any(p.is_symlink() for p in [path, *path.parents] if p != repo and repo in p.parents):
            raise ValueError('Working snapshot cannot contain symlinks')
        if repo not in path.resolve().parents:
            raise ValueError('Working snapshot path escape')
        if not path.exists():
            continue  # Tracked deletions are part of the current source state.
        if not path.is_file():
            raise ValueError('Working snapshot requires regular files; submodules are unsupported')
        canonical = name.casefold()
        if canonical in destinations:
            raise ValueError('Working snapshot has colliding paths')
        destinations.add(canonical)
        if path.stat().st_size > 4 * 1024 * 1024:
            raise ValueError('Working source file exceeds 4 MiB')
        content = path.read_bytes()
        if _secret(name, content):
            excluded.append(name)
            continue
        total += len(content)
        if total > 32 * 1024 * 1024:
            raise ValueError('Working source snapshot exceeds 32 MiB')
        files[name] = (content, path.stat().st_mode & 0o777)
    return files, excluded


def capture_working_snapshot(job) -> dict:
    retained = job.path / 'source-tree'
    if not job._source_metadata:
        files, excluded = working_files(job)
        hashes = {name: hashlib.sha256(content).hexdigest() for name, (content, _) in files.items()}
        evidence = {'source_mode': 'working', 'source_commit': _git(job, 'rev-parse', '--verify', 'HEAD^{commit}'),
                    'source_hash': hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(),
                    'files': hashes, 'dirty_source': bool(_git(job, 'status', '--porcelain')),
                    'excluded_files': sorted(excluded), 'base_spec_hash': job._initial['base_spec_hash'],
                    'target_spec_hash': job._initial['target_spec_hash']}
        retained.mkdir()
        for name, (content, mode) in files.items():
            destination = retained / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            destination.chmod(mode)
        job._source_metadata = evidence
        atomic_json(job.path / 'source.json', evidence)
    evidence = job._source_metadata
    if retained.is_symlink() or not retained.is_dir():
        raise ValueError('Missing or unsafe working snapshot')
    current = {}
    for source in retained.rglob('*'):
        job.check()
        if source.is_symlink():
            raise ValueError('Retained working source was modified with a symlink')
        if source.is_file():
            current[source.relative_to(retained).as_posix()] = hashlib.sha256(source.read_bytes()).hexdigest()
    if current != evidence['files']:
        raise ValueError('Retained working source was modified')
    job.cleanup()
    shutil.copytree(retained, job.workspace)
    job.event('workspace_prepared', **evidence)
    return dict(evidence)
