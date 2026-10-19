# GitHub Draft Proposals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish every source edit from a revalidated repair as one explicitly requested GitHub draft PR, with durable evidence and duplicate protection.

**Architecture:** A retained patch is checked and reconstructed into an offline candidate for the existing engine. A bounded GitHub CLI adapter creates source blobs/tree/commit; a publication service owns target revisions, proposal identity, reservations and reconciliation. Browser and CLI use that same service without altering the source checkout or repair result.

**Tech Stack:** Existing Python/FastAPI, dataclasses/stdlib, installed Git/gh, React/Lucide/CSS, pytest and Node tests. No new dependencies, GitHub App, token form or provider framework.

**Spec:** `docs/superpowers/specs/2026-10-13-github-drafts-design.md`, approved by the user. Preserve native execution: implement in this session, one fresh final reviewer.

## Global Constraints

- Work only in `C:/Users/surji/.codex/worktrees/apishield-phase1/ProjectSeven`; keep its branch/worktree and preserve original repositories.
- Existing CLI credential store; fixed `github.com` destination. No model secrets, token environment fallback, interactive login, fork, implicit push or OAuth permission expansion.
- Publication requires a validated repair, validation-time patch digest, successful offline revalidation, explicit target and an inspected server-prepared proposal. Older digest-less repairs require regeneration.
- Remote base tip must equal the repair's pinned source commit. Never silently rebase or force-update a branch. Recheck before remote effects and before PR creation; document the remaining race after the last check.
- Publish only permitted changed existing Python source files. Tests/config/contracts, symlinks/submodules, binary/add/delete/rename/no-op changes and known private-key markers are rejected.
- All changed files go into one tree/commit/PR. Original source stays untouched; monitoring and AI generation never publish automatically.
- Deterministic `codex/apishield-…` branches, durable reservations and cross-process ownership prevent duplicate publication. Partial remote effects are reconciled, never blindly reset or rolled back.
- Real test is only `Surjithk73/APIGuardTesting`: synthetic shipping `main`, one offline two-file repair and one draft PR. No merge/close/delete/settings changes or paid AI calls. Attach created PR to this chat.
- Research/patent/hosting/trials remain deferred; deeper supported analysis and integration environments remain subsequent stages.
- Python commands below use `C:/Users/surji/ProjectSeven/venv/Scripts/python.exe -B`. Each task commits only its owned files after its GREEN check.

## Review Focus

- A retained patch, target or verification artifact changes between preview and publish: reject it before further remote effects (Tasks 1/3).
- GitHub accepts a branch/PR write but the process loses its response: explicit reconciliation finds the matching publication and avoids another PR (Tasks 2/3).
- A deterministic branch already exists with different source/tree/parent: refuse overwrite and surface a collision (Tasks 2/3).
- A base branch advances after initial preflight or publication begins: preserve partial-effect evidence, stop at the next checkpoint and never silently rebase (Task 3).
- Target/job selection changes while preparation or UI requests are pending: optimistic revisions and selection gates prevent publishing another target's proposal (Tasks 3/4).

## File map

- Modify `apishield/engine.py`: record validated patch digest; preserve existing candidate/validation behavior.
- Create `apishield/publication_prepare.py`: verify retained evidence, reconstruct allowed files and revalidate offline through the engine.
- Create `apishield/github_cli.py`: bounded credential-store-only gh adapter and Git-data operations.
- Create `apishield/publication_state.py`: revisioned targets, immutable proposals, publication records and ownership using existing atomic JSON/OS locks.
- Create `apishield/publication.py`: prepare/publish/reconcile orchestration and guarded browser router.
- Modify `apishield/dashboard_jobs.py`, `dashboard_api.py`, `apishield/cli.py`: service lifecycle, router and shared CLI commands.
- Create `frontend/src/components/GitHubPublication.jsx`, `frontend/src/publication.js`, `frontend/tests/publication.test.js`; modify Workspace and its CSS for target setup/proposal review.
- Create `tests/test_publication_prepare.py`, `tests/test_github_cli.py`, `tests/test_publication_state.py`, `tests/test_publication.py`, `tests/test_publication_api.py`, `tests/test_publication_cli.py` and controlled fixture helpers; write setup/validation docs at handoff.

### Task 1: Retained patch integrity and offline preparation

**Interfaces:** Produces `prepare_repair(store: JobStore, job_id: str, check=None) -> dict` in `publication_prepare.py`, returning `source_job_id`, `verification_job_id`, `source_commit`, `patch_sha256`, `patch`, `files` (sorted path/content/mode/blob-hash records), `evidence_sha256`, and safe validation summary. Consumes existing `run_job(..., candidate_path=..., job=...)`, `prepare_workspace`, `apply_candidate` and strict config loading. New validated results include `patch_sha256`.

- [x] Write failing tests: `test_validated_patch_has_creation_digest`, `test_two_file_offline_revalidation_preserves_source_and_original_result`, `test_preparation_rejects_tampered_or_digestless_artifact`, `test_only_allowed_existing_python_changes`, `test_failed_requirement_check_blocks_preparation`, `test_offline_preparation_never_infers`. Assert exact patch hash, sorted two-file contents, linked distinct verification job, unchanged original bytes/results and no ready proposal after failed checks. Parametrize escape/symlink/binary/add/delete/rename/protected/no-op/private-key-marker cases.
- [x] Run `python -B -m pytest tests/test_publication_prepare.py -q`. Expected: new interface/digest assertions FAIL before implementation.
- [x] Record the digest when the engine writes a validated patch. Reconstruct the source at its retained SHA with retained contract/config snapshots; use Git's bounded patch inspection/application in the disposable copy, never a hand-written unified-diff parser. Convert changed files to full-file old/new snippets and re-run the shared repair engine with an explicit offline candidate. Require its complete validated patch/digest to match the proposed diff; hash the verification evidence and retain it separately. Reuse configured budgets/cancellation and protected-file checks; no additional model route.
- [x] Run preparation tests plus `tests/test_local_engine.py` and `tests/test_requirements.py`. Expected: PASS, originals unchanged. Commit digest/preparation/tests.

### Task 2: Bounded GitHub CLI adapter

**Interfaces:** `GhClient.api(method: str, endpoint: str, payload: dict | None, *, deadline: float, check=None) -> dict | list`; `GhClient.inspect_target(repository: str, base: str, *, deadline: float) -> dict` returns safe account/repository/permission/base-commit/tree metadata; `GhClient.create_draft(repository: str, base: str, head: str, title: str, body: str, *, deadline: float) -> dict` returns verified URL/number/draft/head/base/commit. Adapter also exposes `create_source_commit(target: dict, files: list[dict], message: str, *, deadline: float, check=None) -> dict`, `ensure_branch(target: dict, branch: str, commit: dict, *, deadline: float) -> dict`, `find_publication(target: dict, branch: str, expected: dict, *, deadline: float) -> dict | None`. All accept validated controller values only.

- [x] Write failing mocked-subprocess tests for explicit github.com/repo/base/head argv, JSON/body files with actual newlines, disabled prompts, absent GH_TOKEN/GITHUB_TOKEN/model secrets/endpoint overrides, no token/secret-path/raw-stderr echoes, 45-second command/remaining-total deadline, 2 MiB response cap, terminated owned process trees and missing CLI/auth/permission errors. Prove one tree/commit contains both changed blobs and preserves unchanged base entries. Test matching versus colliding branch, ambiguous PR response and closed/merged existing PR reuse without recreation.
- [x] Run `python -B -m pytest tests/test_github_cli.py -q`. Expected: missing adapter tests FAIL.
- [x] Implement fixed argv/no shell, temporary request/body files outside source, bounded stdout/stderr capture and a controller environment allowlist retaining the CLI's normal user/profile/config directory access. Strip token/model/proxy/endpoint overrides; disable prompts. Validate owner/repository and base ref using bounded Git ref checks. Use Git-data APIs for blobs/tree/commit/ref; `gh pr create --repo … --base … --head … --draft --title … --body-file … --no-maintainer-edit`. Never use dry-run, implicit push/fork or legacy publisher. Verify returned URLs and actual PR metadata; reconcile branch tree/parent/content/message against expected inputs before reuse.
- [x] Run adapter tests. Expected: PASS with zero real GitHub writes. Commit adapter/tests.

### Task 3: Durable publication service and recovery

**Interfaces:** `PublicationStore(root: Path)` persists targets/proposals/publications under `_publication`; `read_target(integration: str) -> dict`, `save_target(integration: str, target: dict, expected_revision: int) -> dict`, `read(proposal_id: str) -> dict`. `PublicationService(jobs: LocalJobs, github: GhClient | None=None)` exposes `configure(integration, repository, base, expected_revision) -> dict`, `prepare(integration, job_id, expected_revision) -> dict`, `publish(proposal_id, expected_revision) -> dict`, `reconcile(proposal_id) -> dict`, `cancel_prepare(proposal_id) -> dict`, `close()`. Prepare/publish reserve durable state before returning and enqueue work on the existing executor; responses contain proposal ID/state, never credentials. Safe records include linked job IDs, source/patch/evidence hashes, target revision, branch, expected tree/commit, phase, errors, partial effects and PR metadata.

- [x] Write failing store/service tests for atomic revision conflicts, safe IDs/paths/lock files, two-process ownership, deterministic identity across equivalent jobs, reservation-before-dispatch, initial wrong/stale base, target edits during prepare, artifact edits after preview, offline failure/cancellation, identical simultaneous publish requests and restart at every remote-effect boundary. Assert PR summaries exclude raw logs, local paths, credentials and issue-closing directives, and label GitHub CI unverified. Mock an accepted branch/PR response loss; assert one matching PR after explicit reconciliation, no force-write, and collision refusal. Advance the base before writes/after commit/before PR; assert stale state and retained partial artifacts at detected checkpoints.
- [x] Run `python -B -m pytest tests/test_publication_state.py tests/test_publication.py -q`. Expected: new state/service assertions FAIL.
- [x] Implement with existing atomic JSON and OS locks: short state transactions plus separate nonblocking execution ownership, no state lock held across network/tests. Identity is SHA256 of canonical repository/base/source-commit/patch-hash; use `codex/apishield-` plus its first 24 hex characters. Target revision and verified-artifact hash gate readiness/publication. Publishing budget is 180 seconds total, commands bounded by Task 2 and remaining time. Persist reservation/expected inputs before each remote effect; never overwrite repair result. Reconcile interrupted records read-only and require explicit Create/Retry to continue writes. Query matching remote branch/PR before retry; closed/merged PR is existing publication. Preserve unknown outcomes as reconciliation-needed. Lifecycle shutdown cancels local preparations and records uncertain publication phases rather than promising remote rollback.
- [x] Run store/service tests plus monitoring/dashboard regressions. Expected: PASS, no implicit remote writes or inference. Commit state/service/tests.

### Task 4: Guarded API, CLI and browser proposal review

**Interfaces:** Add guarded `GET/PUT /api/integrations/{name}/github`, `POST /api/integrations/{name}/proposals` with `{job_id, expected_revision}`, `GET /api/proposals/{id}`, and explicit POST actions `/publish` (expected revision), `/reconcile`, `/cancel`. Integrations get a `GitHubTarget({integration})` editor; validated reports get `GitHubPublication({integration, jobId})`. API only takes target IDs/revisions, never file contents/commands/tokens. CLI adds `proposal prepare JOB --repository OWNER/REPO --base BRANCH`, `proposal publish ID`, `proposal reconcile ID`, `proposal report ID`, with common `--jobs-dir`; all use Task 3 service. CLI prepare shows the exact proposed body and returns identity, publish explicitly writes.

- [x] Write failing API/CLI tests for local peer/host/origin guards, unknown fields/commands, invalid jobs/targets, matching target revisions, GET without writes, asynchronous safe states, source/result immutability, CLI no-write prepare, explicit publish and credential-free JSON. Write frontend tests for all state labels, prepare-versus-publish requests, revision capture, stale async selection changes, pending-edit preservation, duplicate submission and published/reconciliation links. Expected frontend presentation for an unverified GitHub check is `GitHub CI: not verified`.
- [x] Run `python -B -m pytest tests/test_publication_api.py tests/test_publication_cli.py -q` and `npm --prefix frontend test`. Expected: new interfaces/helpers FAIL before implementation.
- [x] Wire service lifecycle/router/CLI. Use strict local target validation and safe command-error responses. Read Impeccable craft floor before UI edits; preserve the existing white/slate/violet workspace. Show target/account status, read-only complete diff and proposed title/body, verified evidence, clear stale/error/reconcile states and the explicit Create draft PR action. Freeze pending target edits, retain original revision in drafts and use existing selection gates. Keep existing patch/report downloads and non-publishable reports functional; add no login/token/merge controls.
- [x] Run API/CLI tests, frontend tests/build/lint and `git diff --check`. Expected: PASS/no new warnings. Commit wiring/UI/tests. Verify mocked desktop/mobile target/prepare/publish/stale/duplicate/restart flows with zero real remote writes.

### Task 5: Controlled remote acceptance, final review and handoff

**Interfaces:** Uses Tasks 1–4 through the finished app; creates only the approved fixture base and one real draft PR. Produces `docs/github-drafts-setup.md`, `docs/github-drafts-validation.md` and updated delivery status.

- [x] Prepare a deterministic two-file shipping fixture, contracts, fixed independent tests and offline candidate in a new external test directory. Run its failing baseline and expected passing repair locally first; show exact seed tree/repair diff in retained evidence. Re-inspect repository emptiness/account; if unexpectedly populated, do not overwrite its base—record the change and use an existing matching fixture or request clarification.
- [x] Seed the reviewed synthetic tree on `main` in `Surjithk73/APIGuardTesting` using the controlled adapter, preserving the resulting SHA. Clone outside ProjectSeven and connect that exact source/base to the local app. Create and revalidate the two-file offline repair, inspect its proposal, then explicitly publish one draft through the app. Expected: both source files in one commit/PR, draft true, captured base, no protected edits, originals unchanged. Repeat the same publish action once; expected: same PR URL/number and one matching PR. Record remote metadata and attach the created PR to this chat. No extra PR, merge, close, delete, paid inference or repository setting changes.
- [x] Exercise actual desktop/mobile setup/preview/publish/link/restart behavior, within Impeccable's two-round visual ceiling. Record actual states/errors, local test/requirement evidence, source hashes, remote commit/PR and partial-effect/reconciliation limitations. Write setup/validation docs and mark deeper analysis/environment setup as still pending.
- [x] Run full Python suite, frontend tests/build/lint and `git diff --check` after final edits. Expected: PASS, existing platform skip/warnings recorded. Restore only generated reasoning-log changes. Commit verified code/evidence/docs.
- [x] Request one fresh final reviewer under native Superpowers, with this spec/plan, ledger decisions and all Review Focus cases. Fix confirmed Important/Critical findings in one observed RED→GREEN pass followed by the green full suite; no independent re-review. Record decisions/minors, complete checkboxes, keep branch/worktree and restart the finished app. Report real PR link, how to use it and remaining stages.

## Self-review and execution handoff

Spec coverage: source/evidence and offline-only revalidation → Task 1; bounded credential-store/API boundary → Task 2; target revisions, duplicates, failures and reconciliation → Task 3; local guards, shared CLI and complete browser review → Task 4; one actual controlled draft, review and truthful docs → Task 5. Each Review Focus item has assigned regressions. Task signatures/state fields are shared consistently; no GitHub App/merge/provider redesign is included.

The user has already selected native execution. Written-plan approval starts implementation; the method question is not repeated. The remote test uses only the approved synthetic fixture/repository, and the app's future Create draft PR action is the user's explicit publication choice.
