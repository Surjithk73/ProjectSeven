"""Filesystem job evidence and cancellation independent of dashboard state."""
from datetime import datetime, timezone
from contextlib import contextmanager
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import threading
import time
import uuid

from .configuration import IntegrationConfig


class JobCancelled(RuntimeError):
    pass


class JobTimedOut(RuntimeError):
    pass


@contextmanager
def _job_transaction(path: Path):
    """Serialize terminal publication and cancellation across processes.

    OS locks are released on process exit; the persistent file is not a stale
    ownership marker. Every participant locks the same first byte/inode.
    """
    with (path / "state.lock").open("a+b") as stream:
        if stream.seek(0, os.SEEK_END) == 0:
            stream.write(b"\0")
            stream.flush()
        deadline = time.monotonic() + 10
        while True:
            try:
                stream.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as exc:
                if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                    raise
                if time.monotonic() >= deadline:
                    raise TimeoutError("job state transaction is busy") from exc
                time.sleep(0.01)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _replace_with_retry(source: Path, destination: Path) -> None:
    """Readers briefly deny replacement on Windows; persistent failures surface."""
    delay = 0.01
    for attempt in range(21):
        try:
            os.replace(source, destination)
            return
        except PermissionError:
            if attempt == 20:
                raise
            time.sleep(delay)
            delay = min(0.05, delay * 2)


def _atomic_bytes(path: Path, content: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        _replace_with_retry(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_json(path: Path, data: dict) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        _replace_with_retry(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class Job:
    def __init__(self, job_id: str, path: Path, config: IntegrationConfig, operation: str):
        self.id = job_id
        self.path = path
        self.workspace = path / "workspace"
        self.config = config
        self.operation = operation
        self.started_at = time.monotonic()
        self._lock = threading.RLock()
        self._initial = {"job_id": job_id, "operation": operation, "status": "queued",
                         "created_at": timestamp(), "budgets": config.to_dict()["budgets"]}
        self._source_metadata = {}
        self._contract_bytes = {}
        self._terminal = None
        self._model_connection = None

    def _restore_contracts(self) -> bool:
        """Retain creation bytes and report any modified/missing snapshot."""
        root = self.path / "contracts"
        if not root.is_dir() or root.is_symlink() or root.resolve() != self.path.resolve() / "contracts":
            raise ValueError("unsafe contract snapshot directory")
        changed = False
        for name, original in self._contract_bytes.items():
            contract = root / name
            try:
                intact = not contract.is_symlink() and contract.read_bytes() == original
            except OSError:
                intact = False
            if not intact:
                changed = True
                _atomic_bytes(contract, original)
        return changed

    def event(self, kind: str, **data) -> None:
        from .commands import redact_data
        entry = {**data, "kind": kind, "time": timestamp(), "job_id": self.id}
        encoded = (json.dumps(redact_data(entry), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        with self._lock:
            fd = os.open(self.path / "events.jsonl", os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
            try:
                os.write(fd, encoded)
                os.fsync(fd)
            finally:
                os.close(fd)

    def cancelled(self) -> bool:
        return (self.path / "cancel.requested").exists()

    def remaining(self) -> float:
        return max(0.0, self.config.budgets.job_timeout_seconds - (time.monotonic() - self.started_at))

    def check(self) -> None:
        if self.cancelled():
            raise JobCancelled("job cancellation requested")
        if self.remaining() <= 0:
            raise JobTimedOut("job deadline exceeded")

    def finish(self, result: dict) -> dict:
        from .commands import redact_data
        with self._lock, _job_transaction(self.path):
            if self._terminal is not None:
                return json.loads(json.dumps(self._terminal))
            contract_error = None
            try:
                if self._restore_contracts():
                    contract_error = "contract snapshots were modified; original snapshots restored"
            except (OSError, ValueError) as exc:
                contract_error = f"contract snapshot verification failed: {exc}"
            final = {**self._initial, **result, **self._source_metadata, "job_id": self.id, "operation": self.operation,
                     "base_spec_hash": self._initial["base_spec_hash"],
                     "target_spec_hash": self._initial["target_spec_hash"],
                     "finished_at": timestamp()}
            if contract_error:
                final["status"] = "failed"
                final["error"] = contract_error
                final.pop("patch", None)
            if self.cancelled():
                final["status"] = "cancelled"
                final.pop("patch", None)
            final = redact_data(final)
            atomic_json(self.path / "result.json", final)
            self._terminal = json.loads(json.dumps(final))
            return final

    def cleanup(self) -> None:
        # The workspace is a fixed child of the known job directory, never a supplied path.
        if self.workspace.is_symlink():
            self.workspace.unlink()
        elif self.workspace.exists():
            shutil.rmtree(self.workspace)


class JobStore:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def _path(self, job_id: str) -> Path:
        if not isinstance(job_id, str) or not re.fullmatch(r"[0-9a-f]{32}", job_id):
            raise ValueError("invalid job ID")
        path = self.root / job_id
        if path.is_symlink() or path.resolve().parent != self.root:
            raise ValueError("unsafe job path")
        if not path.is_dir():
            raise FileNotFoundError(f"job {job_id} does not exist")
        return path

    def create(self, config: IntegrationConfig, operation: str, *, job_id: str | None = None) -> Job:
        if operation not in {"scan", "compare", "repair"}:
            raise ValueError("invalid job operation")
        source = config.repository.resolve()
        if self.root == source or source in self.root.parents:
            raise ValueError("job artifacts must be outside the source repository")
        self.root.mkdir(parents=True, exist_ok=True)
        job_id = job_id or uuid.uuid4().hex
        if not re.fullmatch(r'[0-9a-f]{32}', job_id):
            raise ValueError('invalid reserved job ID')
        path = self.root / job_id
        path.mkdir()
        job = Job(job_id, path, config, operation)
        try:
            job.workspace.mkdir()
            (path / "contracts").mkdir()
            hashes = {}
            for label, spec in (("base", config.base_spec), ("target", config.target_spec)):
                content = spec.read_bytes()
                job._contract_bytes[f"{label}.json"] = content
                (path / "contracts" / f"{label}.json").write_bytes(content)
                hashes[f"{label}_spec_hash"] = hashlib.sha256(content).hexdigest()
            atomic_json(path / "config.json", config.to_dict())
            job._initial.update(hashes)
            atomic_json(path / "result.json", job._initial)
            (path / "events.jsonl").touch()
        except BaseException:
            shutil.rmtree(path)
            raise
        return job

    def get(self, job_id: str) -> dict:
        path = self._path(job_id)
        try:
            for attempt in range(21):
                try:
                    content = (path / "result.json").read_text(encoding="utf-8")
                    break
                except PermissionError:
                    if attempt == 20:
                        raise
                    time.sleep(min(0.01 * (attempt + 1), 0.05))
            value = json.loads(content)
            if not isinstance(value, dict) or value.get("job_id") != job_id or not isinstance(value.get("status"), str):
                raise ValueError("invalid result metadata")
            if (path / "cancel.requested").exists():
                value["cancellation_requested"] = True
            return value
        except (OSError, UnicodeError, ValueError) as exc:
            return {"job_id": job_id, "status": "failed", "error": f"malformed job evidence: {exc}"}

    def cancel(self, job_id: str) -> dict:
        path = self._path(job_id)
        with _job_transaction(path):
            result = self.get(job_id)
            if result.get("status") in {"queued", "running"}:
                with (path / "cancel.requested").open("a", encoding="utf-8") as stream:
                    stream.flush()
                    os.fsync(stream.fileno())
                return {**result, "cancellation_requested": True}
            return result

    def list_jobs(self) -> list[dict]:
        if not self.root.exists():
            return []
        results = []
        for path in sorted(self.root.iterdir()):
            if re.fullmatch(r"[0-9a-f]{32}", path.name):
                try:
                    results.append(self.get(path.name))
                except (ValueError, FileNotFoundError) as exc:
                    results.append({"job_id": path.name, "status": "failed", "error": str(exc)})
        return results
