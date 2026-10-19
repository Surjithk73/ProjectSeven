# Phase 2 Task 1 implementation report

Status: DONE. Scope is configuration, committed workspaces, durable jobs and bounded commands. No inference, network publication, original source edits or old module changes were performed.

## Public interfaces

- `apishield.configuration.load_config(path) -> IntegrationConfig`. The config exposes resolved Path values `repository`, `base_spec`, `target_spec`; `code_paths`, `setup_commands`, `test_commands`, `environment`, `budgets`, `model`, `use_intent`, `ref`, `path`, `version`. `to_dict()` produces resolved JSON-safe version-1 configuration. `Budgets` exposes the four plan fields, with defaults 3/120/600/65536. Invalid configuration raises `ValueError`.
- `apishield.jobs.JobStore(root)` exposes `root`, `create(config, operation)`, `get(id)`, `cancel(id)`, and `list_jobs()`. Job IDs are lowercase UUID hex strings; traversal and symlink job paths are rejected. Missing jobs raise `FileNotFoundError`, invalid IDs raise `ValueError`, malformed persisted result evidence returns a failed diagnostic. Cancellation is persistent and exposed as `cancellation_requested` by subsequent reads.
- A `Job` exposes the exact plan fields/methods, plus `operation`. `check()` raises exported `JobCancelled`/`JobTimedOut`. Creation allocates an empty workspace and copies contracts into `contracts/base.json` and `contracts/target.json`; writes immutable initial `config.json`, initial queued `result.json`, and `events.jsonl`. Cleanup removes only workspace, retaining evidence/contracts. `finish()` atomically writes final evidence with job ID/operation and the pinned source metadata. A pending cancellation wins; repeated finish returns the controller-owned terminal result. Command-written `result.json`/`source.json` cannot manufacture the controller's final result.
- `apishield.workspace.prepare_workspace(job)` returns `source_commit`, `dirty_source`, `excluded_files`, `base_spec_hash`, `target_spec_hash`, and persists `source.json`. It exports exact committed Git blobs via one `cat-file --batch`, preserving executable permissions. Git archive attributes cannot silently remove/substitute files. Repeated preparation retains the original pinned commit even if the source advances. Git metadata is recorded before tree validation, retaining source identity on snapshot rejection. Dirty/untracked files are never copied. Symlinks, gitlinks/submodules, path escapes, Windows device names, case collisions and dotenv/private-key files are rejected/excluded as appropriate. Artifacts inside the supplied checkout are rejected.
- `apishield.commands.run_command(argv, job, label)` returns all seven requested fields. It runs argv with cwd explicitly set to the disposable workspace, no shell, minimal OS environment plus explicit allowed settings, shared output byte cap, credential redaction, per-command/total deadlines, and persistent cancellation polling. On Windows it attaches a suspended process to a kill-on-close Job Object before resuming, eliminating the child-spawn attachment race. On POSIX it owns a process group. All owned descendants stop before a result is returned, including after normal parent exit. `sanitized_environment(config)` is the public environment helper.
- Additional internal helpers consumed by the workspace: `atomic_json`, `redact`, `redact_data`, `_WindowsTree`, `_stop`.

## TDD and verification evidence

Commands ran from `C:/Users/surji/.codex/worktrees/apishield-phase1/ProjectSeven` with `C:/Users/surji/ProjectSeven/venv/Scripts/python.exe -B`.

1. RED: `-m pytest tests/test_local_runtime.py -q --tb=short` produced `21 failed in 5.89s`, expected because the local runtime package did not exist. Initial fixture setup assertions were moved to test calls so failures were ordinary missing-feature failures rather than fixture errors.
2. Initial GREEN: same command produced `21 passed in 7.82s`, including a real Windows process spawning a child, cancellation, confirmation both stopped, and retained report after cleanup.
3. Additional RED: exact Git export, stricter config/path handling, and forged terminal results produced `6 failed, 22 passed in 10.90s`. Expected failures included archive export-ignore removing committed source, unsafe settings not rejected, non-Git/subdirectory config accepted, and command-forged validated result accepted.
4. Additional RED: cancellation persistence and repeated-prepare commit pinning produced `2 failed, 27 passed in 13.05s`. Expected failures were missing persisted cancellation flag and a newly advanced source commit replacing the original pin.
5. Final focused GREEN: same command produced `29 passed in 14.41s`.
6. Full suite: `-m pytest -q --tb=short` produced `128 passed, 1 warning in 47.23s`. The warning is the existing Starlette test client use of deprecated `anyio.abc.BlockingPortal`.
7. An earlier full-suite run overlapped the controller's in-progress CLI and produced `126 passed, 1 failed`: `test_cli_invalid_config_returns_json_without_traceback` imported then-missing `apishield.engine` before configuration validation. Controller fixed the import order; final full suite above includes the passing CLI acceptance tests.
8. `git diff --check` found no whitespace errors; Git reported pre-existing/controller-owned LF-to-CRLF notices for `.gitignore` and `docs/phase2-progress.md`.

## Files owned and changed

`apishield/__init__.py`, `apishield/configuration.py`, `apishield/workspace.py`, `apishield/jobs.py`, `apishield/commands.py`, `tests/test_local_runtime.py`, this report. CLI, pyproject and progress files belong to the controller and are excluded from this commit.

## Self-review and limits

Self-review corrected Git archive byte drift, terminal-result forgery, retained commit pinning across repeated preparation, and cancellation visibility after restart. Source/config validation rejects non-Git directories and subdirectories before job artifact creation.

Configured repository commands remain trusted host code; workspace isolation is not a hosted security sandbox. POSIX process-group behavior is implemented but this verification ran on Windows. Snapshot blob data is materialized in memory; no repository-size budget was specified. Duplicate execution and process-loss interruption classification remain engine/dashboard responsibilities; this store supplies persisted queued/terminal evidence and cancellation but does not automatically resume jobs.

## Task review fix round 1

Addressed both Important findings:

- Cancellation and terminal publication now share an OS transaction lock on the job's `state.lock`. Windows uses a byte lock; POSIX uses `flock`. The OS releases ownership if a process dies. If cancellation acquires the transaction first, its persistent request is observed by finish. If finish acquires it first, a concurrent cancel waits for publication and returns the terminal result without claiming an accepted cancellation. A deterministic barrier regression pauses publication immediately before `atomic_json`; a second regression exercises a publisher in a separate Python process and a cancelling controller process. The existing cancellation-before-finish test covers the opposite ordering.
- Job creation retains the exact original contract bytes in controller memory. Preparation and finish check those bytes, restore modified/missing files atomically, and never recalculate creation hashes from mutable copied files. Preparation rejects detected tampering after restoring originals; finish downgrades attempted validation to failed with a contract diagnostic. Cancellation still wins the final status. Final retained contract bytes match their original hashes, including modification after the last preparation. Caller results cannot overwrite the creation hashes or pinned source metadata.

Covering file: `tests/test_local_runtime.py`. Commands use the same interpreter/workspace as above.

RED: `-m pytest tests/test_local_runtime.py -q --tb=short` produced `3 failed, 29 passed in 28.25s`: the publication barrier allowed an accepted cancellation followed by a validated result; re-preparation failed to handle modified/missing copied contracts; finish returned validated despite contract tampering.

GREEN after fixes: same command produced `32 passed in 26.77s`. After adding the separate-process transaction regression, the final focused command produced `33 passed in 31.80s`. No broad rerun was performed for this scoped fix, per controller instruction. The earlier full-suite evidence remains above; the controller owns the subsequent integrated suite.

Fix files: `apishield/jobs.py`, `apishield/workspace.py`, `tests/test_local_runtime.py`, this report. No public interface changes are required by consumers.

## Follow-up: Windows reader/publication race

The controller observed a background dashboard job remaining queued under repeated polling, while an equivalent non-polling run persisted its failed result. Inspection confirmed the polled job retained only its initial queued result and adapter-error event. A deterministic native reproduction held an ordinary `result.json` reader handle open while another thread called finish; Windows rejected replacement with `PermissionError(13, 'Access is denied')`. This directly confirms the file-sharing race rather than inferring it only from adapter behavior.

Atomic JSON and restored contract publication now use `_replace_with_retry`: retry `PermissionError` up to 21 replacement attempts, with exponential delays capped at 50 ms and approximately 0.92 seconds of maximum total delay. Other errors surface immediately. Permanent permission failures still raise, preserve the prior atomic result, and remove the unpublished temporary file. The finish/cancel transaction remains held across publication, preserving the previous cancellation ordering fix.

Covering tests in `tests/test_local_runtime.py` exercise two deterministic transient replacement denials followed by successful durable publication; a permanent denial with bounded retries, unchanged queued evidence and temporary-file cleanup; and an actual Windows reader handle held during terminal publication.

RED command: `C:/Users/surji/ProjectSeven/venv/Scripts/python.exe -B -m pytest tests/test_local_runtime.py -q --tb=short -k 'permission or reader_handle'` from the attached worktree produced `3 failed, 33 deselected in 5.95s`, including the native access-denied reproduction.

Focused GREEN: same command produced `3 passed, 33 deselected in 5.06s`.

Runtime GREEN: `C:/Users/surji/ProjectSeven/venv/Scripts/python.exe -B -m pytest tests/test_local_runtime.py -q --tb=short` produced `36 passed in 44.36s`. No engine, adapter, example or documentation owned by other agents was modified; the integrated suite remains the controller's next verification step.

Fix files: `apishield/jobs.py`, `tests/test_local_runtime.py`, this report. Public interfaces are unchanged.
