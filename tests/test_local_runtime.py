"""Real local runtime boundaries; no network or model inference."""
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

import pytest


@pytest.fixture
def runtime():
    if importlib.util.find_spec("apishield") is None:
        def missing(*args):
            raise AssertionError("local runtime package is missing")
        return missing, missing
    from apishield.configuration import load_config
    from apishield.jobs import JobStore
    return load_config, JobStore


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


@pytest.fixture
def integration(tmp_path):
    repo = tmp_path / "source"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "fixture@example.invalid")
    git(repo, "config", "user.name", "Fixture")
    (repo / "src").mkdir()
    (repo / "src/client.py").write_text("VALUE = 7\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture")
    cfgdir = tmp_path / "configuration"
    cfgdir.mkdir()
    for name in ("base.json", "target.json"):
        (cfgdir / name).write_text('{"openapi":"3.0.0"}')
    data = {"version": 1, "repository": "../source", "code_paths": ["src"],
            "base_spec": "base.json", "target_spec": "target.json",
            "test_commands": [[sys.executable, "-c", "print('ok')"]]}
    path = cfgdir / "integration.json"
    path.write_text(json.dumps(data))
    return repo, path, data


def test_config_resolves_external_repository_and_effective_defaults(runtime, integration):
    load, _ = runtime
    repo, path, _ = integration
    config = load(path)
    assert config.repository == repo.resolve()
    assert config.base_spec == path.parent / "base.json"
    assert config.budgets.max_attempts == 3
    assert config.budgets.command_timeout_seconds == 120
    assert config.budgets.job_timeout_seconds == 600
    assert config.budgets.output_limit_bytes == 65536
    assert config.model == "gemini-3.8-flash" and config.use_intent is True


def test_config_preserves_explicit_model_selection(runtime, integration):
    load, _ = runtime
    _, path, data = integration
    data['model'] = 'explicit-provider-model'
    path.write_text(json.dumps(data))
    assert load(path).model == 'explicit-provider-model'


@pytest.mark.parametrize("changes", [
    {"extra": 1}, {"version": 2}, {"code_paths": ["../source"]},
    {"code_paths": ["C:\\outside"]}, {"code_paths": ["/outside"]},
    {"test_commands": ["pytest"]}, {"test_commands": [[""]]},
    {"base_spec": "missing.json"}, {"environment": {"GEMINI_API_KEY": "secret"}},
    {"environment": {"PYTHONPATH": "source"}},
    {"environment": {"AWS_SECRET_ACCESS_KEY": "secret"}},
    {"environment": {"DATABASE_URL": "postgres://user:password@host"}},
    {"code_paths": ["src/.GIT/config"]}, {"code_paths": ["src/CON"]},
    {"budgets": {"job_timeout_seconds": float("nan")}},
    {"budgets": {"max_attempts": 0}}, {"budgets": {"output_limit_bytes": True}},
])
def test_config_rejects_unsafe_or_invalid_settings(runtime, integration, changes):
    load, _ = runtime
    _, path, data = integration
    path.write_text(json.dumps(data | changes))
    with pytest.raises(ValueError):
        load(path)


def test_snapshot_pins_committed_tree_excludes_secrets_and_preserves_dirty_source(runtime, integration, tmp_path):
    from apishield.workspace import prepare_workspace
    load, Store = runtime
    repo, path, _ = integration
    (repo / ".env").write_text("TOKEN=do-not-copy")
    (repo / "private.pem").write_text("-----BEGIN PRIVATE KEY-----\nsecret")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "secret fixture")
    commit = git(repo, "rev-parse", "HEAD")
    (repo / "src/client.py").write_text("VALUE = 99\n")
    (repo / "untracked.txt").write_text("dirty")
    before = git(repo, "status", "--porcelain")
    job = Store(tmp_path / "jobs").create(load(path), "scan")
    evidence = prepare_workspace(job)
    assert evidence["source_commit"] == commit and evidence["dirty_source"] is True
    assert set(evidence["excluded_files"]) == {".env", "private.pem"}
    assert (job.workspace / "src/client.py").read_text() == "VALUE = 7\n"
    assert not (job.workspace / ".env").exists()
    assert not (job.workspace / "private.pem").exists()
    assert not (job.workspace / "untracked.txt").exists()
    assert evidence["base_spec_hash"] == hashlib.sha256((path.parent / "base.json").read_bytes()).hexdigest()
    assert git(repo, "status", "--porcelain") == before
    job.cleanup()
    assert not job.workspace.exists() and (job.path / "contracts/base.json").exists()


def test_snapshot_rejects_git_symlink_and_submodule(runtime, integration, tmp_path):
    from apishield.workspace import prepare_workspace
    load, Store = runtime
    repo, path, _ = integration
    blob = subprocess.check_output(["git", "-C", str(repo), "hash-object", "-w", "--stdin"], input=b"../outside").decode().strip()
    git(repo, "update-index", "--add", "--cacheinfo", f"120000,{blob},src/link")
    git(repo, "commit", "-m", "symlink")
    job = Store(tmp_path / "jobs").create(load(path), "scan")
    with pytest.raises(ValueError, match="symlink"):
        prepare_workspace(job)
    git(repo, "update-index", "--force-remove", "src/link")
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{git(repo, 'rev-parse', 'HEAD')},src/submodule")
    git(repo, "commit", "-m", "submodule")
    job = Store(tmp_path / "other-jobs").create(load(path), "scan")
    with pytest.raises(ValueError, match="submodule"):
        prepare_workspace(job)


def test_snapshot_ignores_archive_attributes_and_freezes_contracts_at_creation(runtime, integration, tmp_path):
    from apishield.workspace import prepare_workspace
    load, Store = runtime
    repo, path, _ = integration
    (repo / ".gitattributes").write_text("src/client.py export-ignore\nversion.txt export-subst\n")
    (repo / "version.txt").write_text("$Format:%H$\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "archive attributes")
    job = Store(tmp_path / "jobs").create(load(path), "scan")
    (path.parent / "base.json").write_text('{"changed":true}')
    evidence = prepare_workspace(job)
    assert (job.workspace / "src/client.py").read_text() == "VALUE = 7\n"
    assert (job.workspace / "version.txt").read_text() == "$Format:%H$\n"
    assert (job.path / "contracts/base.json").read_text() == '{"openapi":"3.0.0"}'
    assert evidence["base_spec_hash"] == hashlib.sha256(b'{"openapi":"3.0.0"}').hexdigest()


def test_configuration_rejects_non_repository_and_source_subdirectory(runtime, integration):
    load, _ = runtime
    _, path, data = integration
    for source in (".", "../source/src"):
        path.write_text(json.dumps(data | {"repository": source}))
        with pytest.raises(ValueError, match="Git"):
            load(path)


def test_store_rejects_artifacts_inside_source_and_job_traversal(runtime, integration, tmp_path):
    load, Store = runtime
    repo, path, _ = integration
    with pytest.raises(ValueError):
        Store(repo / "artifacts").create(load(path), "scan")
    store = Store(tmp_path / "jobs")
    for invalid in ["../source", ".", "", "a/b", "C:\\source"]:
        with pytest.raises(ValueError):
            store.get(invalid)
        with pytest.raises(ValueError):
            store.cancel(invalid)


def test_jobs_persist_independent_results_cancel_events_and_config(runtime, integration, tmp_path):
    from apishield.jobs import JobCancelled
    load, Store = runtime
    _, path, _ = integration
    store = Store(tmp_path / "jobs")
    first = store.create(load(path), "scan")
    second = store.create(load(path), "repair")
    assert Store(store.root).get(first.id)["status"] == "queued"
    assert json.loads((first.path / "config.json").read_text())["repository"] == str(first.config.repository)
    first.event("started", stage="scan")
    store.cancel(first.id)
    assert Store(store.root).get(first.id)["cancellation_requested"] is True
    with pytest.raises(JobCancelled):
        first.check()
    assert not second.cancelled()
    result = first.finish({"status": "completed"})
    assert result["status"] == "cancelled" and result["operation"] == "scan" and result["job_id"] == first.id
    second.finish({"status": "validated"})
    assert Store(store.root).get(second.id)["status"] == "validated"
    assert len(Store(store.root).list_jobs()) == 2
    assert json.loads((first.path / "events.jsonl").read_text().splitlines()[0])["kind"] == "started"
    (second.path / "result.json").write_text("broken")
    assert any(item["status"] == "failed" and item.get("error") for item in store.list_jobs())


def command_job(runtime, integration, tmp_path, **budgets):
    from apishield.workspace import prepare_workspace
    load, Store = runtime
    _, path, data = integration
    path.write_text(json.dumps(data | {"budgets": budgets, "environment": {"SHIP_REGION": "india"}}))
    job = Store(tmp_path / "jobs").create(load(path), "repair")
    prepare_workspace(job)
    return job


def test_subprocess_environment_is_minimal_and_output_is_capped_redacted(runtime, integration, tmp_path, monkeypatch):
    from apishield.commands import run_command
    monkeypatch.setenv("GEMINI_API_KEY", "controller-secret")
    monkeypatch.setenv("PYTHONPATH", "untrusted-controller")
    job = command_job(runtime, integration, tmp_path, output_limit_bytes=512)
    script = "import os; print(os.getenv('GEMINI_API_KEY')); print(os.getenv('PYTHONPATH')); print(os.getenv('SHIP_REGION')); print('api_key=private-secret'); print('x'*2000)"
    result = run_command([sys.executable, "-c", script], job, "tests")
    assert result["exit_code"] == 0 and result["output_limited"] is True
    assert "None\nNone\nindia" in result["stdout"]
    assert "private-secret" not in result["stdout"]
    assert len((result["stdout"] + result["stderr"]).encode()) <= 512


def test_command_timeout_and_total_deadline(runtime, integration, tmp_path):
    from apishield.commands import run_command
    from apishield.jobs import JobTimedOut
    job = command_job(runtime, integration, tmp_path, command_timeout_seconds=0.15, job_timeout_seconds=1)
    result = run_command([sys.executable, "-c", "import time; time.sleep(30)"], job, "tests")
    assert result["timed_out"] is True and result["cancelled"] is False
    job.started_at -= 2
    assert job.remaining() == 0
    with pytest.raises(JobTimedOut):
        job.check()


def test_command_cannot_forge_terminal_job_result_or_source_evidence(runtime, integration, tmp_path):
    from apishield.commands import run_command
    job = command_job(runtime, integration, tmp_path)
    script = "import pathlib,json; pathlib.Path('../result.json').write_text(json.dumps({'job_id': '%s', 'status': 'validated'})); pathlib.Path('../source.json').write_text('{}')" % job.id
    run_command([sys.executable, "-c", script], job, "tests")
    result = job.finish({"status": "failed", "error": "validation failed"})
    assert result["status"] == "failed" and result["source_commit"]
    assert job.finish({"status": "validated"})["status"] == "failed"


def test_repreparing_job_keeps_same_commit_after_source_advances(runtime, integration, tmp_path):
    from apishield.workspace import prepare_workspace
    job = command_job(runtime, integration, tmp_path)
    repo, _, _ = integration
    original_commit = git(repo, "rev-parse", "HEAD")
    (repo / "src/client.py").write_text("VALUE = 123\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "advance")
    evidence = prepare_workspace(job)
    assert evidence["source_commit"] == original_commit
    assert (job.workspace / "src/client.py").read_text() == "VALUE = 7\n"


def test_accepted_cancellation_cannot_lose_to_paused_terminal_write(runtime, integration, tmp_path, monkeypatch):
    import apishield.jobs as jobs
    job = command_job(runtime, integration, tmp_path)
    publication_paused = threading.Event()
    release_publication = threading.Event()
    cancel_started = threading.Event()
    cancel_returned = threading.Event()
    final_results, cancel_results, errors = [], [], []
    real_atomic_json = jobs.atomic_json

    def paused_publication(path, data):
        if path.name == "result.json" and data.get("status") == "validated":
            publication_paused.set()
            assert release_publication.wait(5), "test must release terminal publication"
        real_atomic_json(path, data)

    def finish():
        try:
            final_results.append(job.finish({"status": "validated"}))
        except BaseException as exc:
            errors.append(exc)

    def cancel():
        cancel_started.set()
        try:
            cancel_results.append(jobs.JobStore(job.path.parent).cancel(job.id))
        except BaseException as exc:
            errors.append(exc)
        finally:
            cancel_returned.set()

    monkeypatch.setattr(jobs, "atomic_json", paused_publication)
    finisher = threading.Thread(target=finish)
    canceller = threading.Thread(target=cancel)
    finisher.start()
    try:
        assert publication_paused.wait(5)
        canceller.start()
        assert cancel_started.wait(5)
        returned_while_paused = cancel_returned.wait(0.3)
    finally:
        release_publication.set()
        finisher.join(5)
        if canceller.ident is not None:
            canceller.join(5)
    assert not errors and not finisher.is_alive() and not canceller.is_alive()
    accepted = cancel_results[0].get("cancellation_requested", False)
    if accepted:
        assert final_results[0]["status"] == "cancelled", "an accepted cancellation must win publication"
    else:
        assert not returned_while_paused, "terminal transaction must serialize a late cancellation"
        assert final_results[0]["status"] == cancel_results[0]["status"] == "validated"
    assert jobs.JobStore(job.path.parent).get(job.id)["status"] == final_results[0]["status"]


@pytest.mark.parametrize("stage", ["prepare", "finish"])
def test_contract_tampering_never_replaces_creation_identity(runtime, integration, tmp_path, stage):
    from apishield.workspace import prepare_workspace
    job = command_job(runtime, integration, tmp_path)
    original = b'{"openapi":"3.0.0"}'
    original_hash = hashlib.sha256(original).hexdigest()
    (job.path / "contracts/base.json").write_text('{"tampered":true}')
    (job.path / "contracts/target.json").unlink()
    if stage == "prepare":
        with pytest.raises(ValueError, match="contract"):
            prepare_workspace(job)
        result = job.finish({"status": "failed", "error": "contract tampering"})
    else:
        result = job.finish({"status": "validated"})
        assert result["status"] == "failed" and "contract" in result["error"].lower()
    assert result["base_spec_hash"] == result["target_spec_hash"] == original_hash
    assert (job.path / "contracts/base.json").read_bytes() == original
    assert (job.path / "contracts/target.json").read_bytes() == original


def test_terminal_transaction_serializes_cancellation_from_another_process(runtime, integration, tmp_path):
    _, Store = runtime
    _, config_path, _ = integration
    store = Store(tmp_path / "jobs")
    paused = tmp_path / "publication-paused"
    released = tmp_path / "publication-released"
    script = """
import json, pathlib, sys, time
import apishield.jobs as jobs
from apishield.configuration import load_config
job = jobs.JobStore(pathlib.Path(sys.argv[2])).create(load_config(sys.argv[1]), 'repair')
original = jobs.atomic_json
def barrier(path, data):
    if path.name == 'result.json' and data.get('status') == 'validated':
        pathlib.Path(sys.argv[3]).write_text(job.id)
        deadline = time.monotonic() + 10
        while not pathlib.Path(sys.argv[4]).exists():
            if time.monotonic() >= deadline:
                raise RuntimeError('publication was never released')
            time.sleep(0.01)
    original(path, data)
jobs.atomic_json = barrier
print(json.dumps(job.finish({'status': 'validated'})))
"""
    process = subprocess.Popen([sys.executable, "-B", "-c", script, str(config_path),
        str(store.root), str(paused), str(released)], cwd=Path(__file__).resolve().parents[1],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    cancellation, errors = [], []
    started = threading.Event()
    returned = threading.Event()
    canceller = None
    try:
        deadline = time.monotonic() + 5
        while not paused.exists() and time.monotonic() < deadline and process.poll() is None:
            time.sleep(0.02)
        assert paused.exists(), "separate publisher must reach the transaction barrier"
        job_id = paused.read_text()
        def cancel():
            started.set()
            try:
                cancellation.append(store.cancel(job_id))
            except BaseException as exc:
                errors.append(exc)
            finally:
                returned.set()
        canceller = threading.Thread(target=cancel)
        canceller.start()
        assert started.wait(5)
        returned_before_publication = returned.wait(0.3)
        released.touch()
        stdout, stderr = process.communicate(timeout=5)
        canceller.join(5)
        assert process.returncode == 0, stderr
        assert not errors and not canceller.is_alive()
        assert not returned_before_publication
        assert json.loads(stdout)["status"] == cancellation[0]["status"] == "validated"
        assert not cancellation[0].get("cancellation_requested", False)
    finally:
        released.touch()
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
        if canceller is not None:
            canceller.join(5)


def test_atomic_result_retries_transient_permission_error(runtime, integration, tmp_path, monkeypatch):
    import apishield.jobs as jobs
    job = command_job(runtime, integration, tmp_path)
    real_replace = jobs.os.replace
    rejected = 0
    def transient_replace(source, destination):
        nonlocal rejected
        if Path(destination).name == "result.json" and rejected < 2:
            rejected += 1
            raise PermissionError("temporary sharing violation")
        return real_replace(source, destination)
    monkeypatch.setattr(jobs.os, "replace", transient_replace)
    result = job.finish({"status": "completed"})
    assert rejected == 2 and result["status"] == "completed"
    assert jobs.JobStore(job.path.parent).get(job.id)["status"] == "completed"
    assert not list(job.path.glob(".result.json.*.tmp"))


def test_atomic_result_permanent_permission_failure_is_bounded(runtime, integration, tmp_path, monkeypatch):
    import apishield.jobs as jobs
    job = command_job(runtime, integration, tmp_path)
    real_replace = jobs.os.replace
    rejected = 0
    def permanent_replace(source, destination):
        nonlocal rejected
        if Path(destination).name == "result.json":
            rejected += 1
            raise PermissionError("persistent sharing violation")
        return real_replace(source, destination)
    monkeypatch.setattr(jobs.os, "replace", permanent_replace)
    start = time.monotonic()
    with pytest.raises(PermissionError):
        job.finish({"status": "completed"})
    assert 1 < rejected <= 30
    assert time.monotonic() - start < 2
    assert jobs.JobStore(job.path.parent).get(job.id)["status"] == "queued"
    assert not list(job.path.glob(".result.json.*.tmp"))


@pytest.mark.skipif(os.name != "nt", reason="Windows file sharing semantics")
def test_windows_reader_handle_does_not_lose_terminal_publication(runtime, integration, tmp_path):
    job = command_job(runtime, integration, tmp_path)
    results, errors = [], []
    started = threading.Event()
    def finish():
        started.set()
        try:
            results.append(job.finish({"status": "completed"}))
        except BaseException as exc:
            errors.append(exc)
    finisher = threading.Thread(target=finish)
    # Ordinary CPython file reads deny FILE_SHARE_DELETE on Windows while open.
    with (job.path / "result.json").open("rb"):
        finisher.start()
        assert started.wait(5)
        time.sleep(0.15)
    finisher.join(5)
    assert not finisher.is_alive() and not errors
    assert results[0]["status"] == "completed"
    from apishield.jobs import JobStore
    assert JobStore(job.path.parent).get(job.id)["status"] == "completed"


def process_alive(pid):
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.restype = ctypes.c_void_p
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        code = ctypes.c_ulong()
        kernel.GetExitCodeProcess(ctypes.c_void_p(handle), ctypes.byref(code))
        kernel.CloseHandle(ctypes.c_void_p(handle))
        return code.value == 259
    stat = Path(f"/proc/{pid}/stat")
    if stat.exists() and stat.read_text().split(")", 1)[1].split()[0] == "Z":
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def test_cancellation_stops_real_descendant_and_retains_report(runtime, integration, tmp_path):
    from apishield.commands import run_command
    job = command_job(runtime, integration, tmp_path)
    pidfile = job.path / "child.pid"
    code = "import subprocess,sys,time,pathlib; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); pathlib.Path(sys.argv[1]).write_text(str(p.pid)); time.sleep(60)"
    results = []
    thread = threading.Thread(target=lambda: results.append(run_command([sys.executable, "-c", code, str(pidfile)], job, "tests")))
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not pidfile.exists() and time.monotonic() < deadline:
            time.sleep(0.03)
        assert pidfile.exists(), "command must start a real child"
        pid = int(pidfile.read_text())
        assert process_alive(pid)
        from apishield.jobs import JobStore
        JobStore(job.path.parent).cancel(job.id)
        thread.join(10)
        assert not thread.is_alive()
        assert results[0]["cancelled"] is True
        assert not process_alive(pid)
        job.finish({"status": "cancelled", "validation": results})
        job.cleanup()
        assert (job.path / "result.json").exists()
    finally:
        if thread.is_alive():
            from apishield.jobs import JobStore
            JobStore(job.path.parent).cancel(job.id)
            thread.join(10)
