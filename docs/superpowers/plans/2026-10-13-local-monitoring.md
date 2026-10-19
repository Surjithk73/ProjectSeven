# Local Contract Monitoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Let a local user monitor an approved OpenAPI URL, inspect retained comparison evidence, and explicitly accept a new baseline.

**Architecture:** Store immutable contracts and revisioned monitoring state under the existing external job root. A service-owned scheduler uses the existing bounded executor and comparison engine; browser controls call local-only endpoints. Fetching, state transitions and orchestration are separate focused modules, without another database or scheduler dependency.

**Tech Stack:** Python, FastAPI, existing httpx 0.28.1, filesystem JSON, threading, pytest; React, Lucide, existing CSS and Node tests.

**Spec:** `docs/superpowers/specs/2026-10-13-local-monitoring-design.md` (approved by the user).

## Global Constraints

- Continue in the attached `apishield-phase1` worktree; preserve the original ProjectSeven and client_app repositories.
- Preserve the local, no-sign-in workflow and existing engine, requirement checks and original source integrity.
- Monitoring operates while the app/computer is running; it is not a hosted service.
- Default interval is 60 minutes, with a minimum of 5 minutes for automatic schedules.
- Timeout 15 seconds, maximum 2 MiB response body; JSON OpenAPI only.
- No ambient proxies, browser cookies or controller model/GitHub credentials in fetches.
- HTTPS by default; HTTP/private/local sources require an explicit trusted-local opt-in. Always reject unspecified, multicast and link-local/metadata destinations.
- Never automatically advance the accepted baseline. Formatting/object-key order does not constitute a change; array order remains significant.
- A timer creates scan/comparison evidence only. No model generation, automatic remote publication or automatic merge.
- AI integration/live testing, research evaluation, patents, hosting and early trials remain deferred. GitHub, deeper analysis and environment setup receive their own subsequent spec/plan cycles.

## Review Focus

- Public host redirecting or resolving to a disallowed address: reject each hop and use a transport that connects only to validated addresses (Task 1).
- Integration repository/requirements edits during a fetch: discard stale publication and compare only the captured immutable configuration (Task 3).
- Process loss between snapshot persistence and job submission: recover without duplicate change jobs or fabricated success (Tasks 2–3).
- Baseline acceptance or pause during an active check: keep the selected baseline and prevent late results from overriding newer state (Tasks 2–3).
- Switching integrations during slow browser requests: never show or mutate another integration's monitoring state (Task 4).

## Files and interfaces

- Create `apishield/contract_fetch.py`: URL policy, validated bounded HTTP transport, JSON/canonical hashes.
- Create `apishield/monitor_state.py`: revisioned records, immutable snapshot retention, durable check ownership and change identities.
- Create `apishield/monitoring.py`: orchestration, scheduling and guarded local API routes.
- Modify `apishield/dashboard_jobs.py`: submit a captured configuration through the existing job executor and start/close the monitor lifecycle.
- Modify `dashboard_api.py`: mount monitor routes and eagerly initialize the local service on lifespan startup so restored schedules run before any browser request.
- Create `frontend/src/components/Monitoring.jsx` and `frontend/src/monitoring.js`; modify `frontend/src/pages/Workspace.jsx` and `frontend/src/workspace.css` for the selected-integration panel and evidence navigation.
- Create `tests/test_contract_fetch.py`, `tests/test_monitor_state.py`, `tests/test_monitoring.py`, `frontend/tests/monitoring.test.js`, and `docs/local-monitoring.md`.
- Shared JSON timestamps use UTC ISO format; IDs use existing integration validation. Invalid/stale requests produce 422/409; unknown integration/change produces 404; local-browser guard produces 403.

### Task 1: Bounded contract fetching

**Consumes:** `configuration.SECRET_NAME`; existing httpx dependency.
**Produces:** `fetch_contract(url: str, allow_local: bool = False) -> FetchedContract`, a dataclass with `document: dict`, `raw: bytes`, `raw_hash: str`, `content_hash: str`, `fetched_at: str`; `canonical_hash(document: dict) -> str`; `ContractFetchError(ValueError)`.

- [x] Write `tests/test_contract_fetch.py` tests asserting HTTPS policy; explicit local HTTP acceptance; credentials and secret query rejection; unspecified/multicast/link-local rejection; redirect and DNS address checks; pinned destination on connect; no environment proxies/auth; timeout and streamed body limit; invalid/non-object/non-OpenAPI/nonfinite JSON rejection. Assert `canonical_hash({'openapi':'3.0.0','paths':{}})` is unchanged by object order/whitespace and changes when array order changes. Use controlled transports/resolvers, no public requests.
- [x] Run `python -B -m pytest tests/test_contract_fetch.py -q`; confirm failure for missing interfaces before implementing.
- [x] Implement these interfaces with SHA-256 and strict JSON parsing, streaming limits, at most five validated redirect hops and one overall 15-second deadline. Validate all resolved addresses; preserve original hostname for TLS/Host while pinning the actual destination. Close responses/transports on every exit. If an address family or transport cannot enforce pinning, return a clear error rather than silently falling back to unchecked DNS.
- [x] Run the same test command; require all cases pass. Commit the fetch module and tests.

### Task 2: Durable monitoring state

**Consumes:** Task 1 hashes/dataclass and existing `jobs.atomic_json`/transaction patterns.
**Produces:** `MonitorStore(root: Path)` with `read(integration: str) -> dict`, `configure(integration: str, settings: dict, expected_revision: int, config_token: str) -> dict`, `retain(integration: str, fetched: FetchedContract) -> str`, `accept(integration: str, change_id: str, expected_revision: int) -> dict`. Store has transaction methods used by Task 3 to claim and finish checks; no network or subprocess work inside transactions.

- [x] Write `tests/test_monitor_state.py`: first revision is 0/unconfigured; successful writes increment revision; stale updates conflict; default interval 60/minimum 5; immutable snapshot bytes/hash verification; path traversal/symlink rejection; canonical duplicate reuse; baseline mode `saved` versus `first_fetch`; explicit acceptance only of retained snapshots; acceptance does not mark repair success. Crash/reload retains records and rejects corrupt state with a recoverable diagnostic instead of resetting a baseline.
- [x] Run `python -B -m pytest tests/test_monitor_state.py -q`; verify intended missing-behavior failures.
- [x] Implement state at `_monitoring/<integration>/state.json`, with immutable `snapshots/<raw_hash>.json` and retained metadata mapping canonical identities to raw snapshots. Initial record includes `revision`, `configured`, `enabled`, `source_url`, `allow_local`, `interval_minutes`, `baseline_mode`, `baseline_hash`, `last_observation_hash`, `last_attempt`, `last_success`, `next_due`, `error`, `active_check`, `changes`. A change includes baseline/observed hashes, source configuration token, job ID/status and creation time. Record the baseline/configuration revision at ownership claim; publication must match that claim. Persist job identity before dispatch. Reuse OS-released transaction locks for cross-process correctness; never derive paths from arbitrary browser input.
- [x] Run Task 1–2 tests; require pass and commit state module/tests.

### Task 3: Shared-engine scheduling and local endpoints

**Consumes:** Tasks 1–2; `LocalJobs`, `load_config`, `JobStore.create`, existing comparison engine and `browser_setup.local_browser`.
**Produces:** `MonitorService(jobs: LocalJobs)` with `start() -> None`, `close() -> None`, `check(integration: str) -> dict`, `tick(now: datetime) -> None`. Add `LocalJobs.submit_config(integration: str, config: IntegrationConfig, operation: str) -> dict` (same evidence and ownership as ordinary submissions; no proposal for compare). Keep existing `submit` behavior unchanged.

- [x] Write `tests/test_monitoring.py` with injected clock/fetcher/executor: first-fetch initializes without alert/job; saved-contract baseline reveals existing change; unchanged/format-only response creates no job; repeated baseline/target creates one change/job; meaningful change submits exactly one `compare`; config/requirements are copied from the captured integration and contracts from immutable monitor snapshots. Never call model generation or GitHub. Test failures preserve last good baseline; manual/scheduled overlap; stale fetch after source/baseline/integration edits; pause/re-enable; missed intervals coalesce; interrupted owner/job recovery; cancellation and shutdown; two processes cannot claim the same check. Test job-creation/dispatch failure recovery without duplicate IDs.
- [x] Add endpoint tests for `GET/PUT /api/integrations/{name}/monitoring`, `POST .../monitoring/check`, `POST .../monitoring/accept`, `POST .../monitoring/changes/{change_id}/repair`. PUT body is `{source_url, allow_local, interval_minutes, baseline_mode, enabled, expected_revision}`; accept body is `{change_id, expected_revision}`. Check returns 202 with current check state. Repair explicitly submits a new engine job with that retained baseline/target/config; it requires the current model setting and never runs from the scheduler. Read-only server integrations reject browser mutations. Test local origin/peer guards, strict payloads, conflict/unknown errors, integration edits and snapshot tampering.
- [x] Run `python -B -m pytest tests/test_monitoring.py tests/test_dashboard_jobs.py tests/test_browser_setup.py -q`; verify new tests fail for the expected missing features.
- [x] Implement captured-config submission and the monitor coordinator/router. Derive `config_token` from the full immutable integration config identity/contents. Resolve/pin repository ref at comparison creation through existing job machinery, retain configuration identity and monitor change ID in evidence; never analyze dirty files. Own a single stoppable scheduling loop per local service, wake at most once per second, with no busy polling or HTTP under locks. Persist next due time and claim before queuing checks onto the existing executor; share its two-worker bound. Reconcile orphaned claims/jobs at startup. On close stop scheduling before cancelling owned work; an active fetch respects the bounded timeout and cannot publish after close. Eager service initialization on lifespan must preserve the legacy demo monitor's opt-in behavior.
- [x] Run Task 1–3 tests and existing local engine/runtime/requirements tests; require pass. Commit backend wiring/tests.

### Task 4: Usable browser monitoring and acceptance

**Consumes:** Task 3 API, existing `requestJSON`, `createSelectionGate`, integration metadata and report navigation.
**Produces:** `Monitoring({integration, editable, onOpenJob, onRepairQueued})` component; `monitorPresentation(state) -> {label, detail}`, `validateMonitorInput(input) -> string | null` helpers. Use existing selection gating for asynchronous requests.

- [x] Add Node tests in `frontend/tests/monitoring.test.js` asserting state labels, 60-minute default, rejection below 5 minutes, first-fetch versus saved-baseline copy, optimistic revision payloads, no repair success label on baseline acceptance, and stale selected-integration responses discarded. Run `npm --prefix frontend test`; confirm the new behavior fails before implementation.
- [x] Read Impeccable craft guidance before UI edits. Implement URL/interval/baseline inputs, local-source opt-in, Enable/Pause/Check now, last/next-check/error status and changes list. Preserve current visual language; disable conflicting mutations during pending saves/actions; retain form on failure; show explicit app-running requirement. Baseline acceptance explains acknowledgment, repair is explicit and uses retained change contracts. Link comparison jobs into existing reports. Server-managed controls are read-only. Wrap URLs and keep keyboard focus/loading/errors accessible.
- [x] Run `npm --prefix frontend test`, `npm --prefix frontend run build`, `npm --prefix frontend run lint`; require new tests/build pass and no new lint warnings. Commit frontend/helper tests.
- [x] Start the app with the existing launcher and a controlled local fixture server. In the actual browser, connect a synthetic integration, enable first-fetch monitoring, manually check unchanged/format-only/changed fixtures, open evidence, pause/resume, accept baseline, handle invalid/failed fetch, and restart to confirm persistence. Repeat key flows at desktop and 390-pixel mobile width, including slow response while switching integrations. Verify no overflow/duplicate job and original fixture Git status unchanged. Save screenshots/results, not fabricated browser claims.

### Task 5: Final verification, review and documentation

**Consumes:** Working Tasks 1–4 and their recorded evidence.
**Produces:** User-facing `docs/local-monitoring.md`, updated implementation status and completion report.

- [x] Document setup, both baseline choices, schedule limitations, local-source policy, failure recovery, how comparison/explicit repair differs from baseline acceptance, and where immutable evidence lives. Mark monitoring complete only after its acceptance checks; keep the later GitHub/analysis/environment work visible and AI deferred.
- [x] Run `C:/Users/surji/ProjectSeven/venv/Scripts/python.exe -B -m pytest -q` plus frontend tests/build/lint once after final edits. Use that same Python executable for earlier commands. Record actual results, skips and pre-existing warnings; restore generated reasoning logs without touching user files. Check `git diff --check` and fixture/original repository status.
- [x] Under the preserved native execution method, request one fresh whole-change review using Superpowers executing-plans/requesting-code-review. Fix confirmed important findings with focused regression checks; expand verification only where new changes justify it.
- [x] Commit documentation and verified fixes. Keep work in this attached branch; no merge/push to the original project and no GitHub publication in this monitoring increment. Report how the user runs it and which subsequent subsystem comes next.

## Handoff

Execution method: preserve native execution from the existing project workflow. The agent implements these tasks in this session, with one fresh final reviewer, after the user reviews this written plan. No per-task implementation delegation or AI calls.

Self-review: each spec section maps to Tasks 1–4; restart/concurrency/policy/mobile cases are assigned to concrete tests and acceptance steps. Existing immutable configs/contracts and local job ownership are reused; monitoring adds no new model/provider or hosted subsystem.
