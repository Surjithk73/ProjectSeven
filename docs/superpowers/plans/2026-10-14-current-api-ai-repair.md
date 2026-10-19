# Current API and AI Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native execution, or superpowers:subagent-driven-development if the user selects that method. Implement task-by-task using the approved spec. Steps use checkbox syntax.

**Goal:** Make the local app detect active API changes and produce reviewed, tested AI repairs that can be applied to current working files without commits.

**Architecture:** Reuse the existing job engine, frozen contracts, graph builder, Gemini connector and validation commands. Add browser working-tree snapshots, accepted/observed contract state, bounded AI intent/check generation and guarded local Apply. Banking executes the registered demo adapter, making its V1/V2 state the source of the observed documentation.

**Tech Stack:** Existing Python/FastAPI/Pydantic/httpx/google-genai, React/Vite, Git CLI, pytest and Node test runner. No new product dependencies.

**Spec:** `docs/superpowers/specs/2026-10-14-current-api-ai-repair-design.md`

## Global constraints

- Work in `C:/Users/surji/ProjectSeven`; do not change the stale linked worktree or `.project-backups`.
- Apply modifies current working files only: no automatic Git commit, branch, push or PR. Keep implementation changes uncommitted too.
- Model is `gemini-3.8-flash`; no silent model/provider substitution or supplied-candidate fallback in browser repairs.
- Existing tests remain protected. Generated checks are separate and labelled AI-generated.
- Current-code scans include permitted working files; existing committed-source CLI/publication behavior remains available.
- Preserve white/blue themes, dark repair diff, historical job evidence, budgets, cancellation, path/secret checks and local-origin restrictions.
- Existing AI connection test failed twice with HTTP 503. Live AI completion must be demonstrated separately from mocked tests.

## Review focus

1. An unrelated user edit while a repair is being reviewed must not be overwritten or silently excluded from validation: Tasks 1 and 6.
2. Switching V2 back to V1 while a job runs must not change that job's captured contract or permit stale Apply: Tasks 2 and 6.
3. A generated check that passes trivially or rewrites existing tests must not establish a validated repair: Tasks 4 and 5.
4. A process/write failure halfway through Apply must retain recoverable original files and must not advance the accepted contract: Task 6.
5. Old history, stale async responses and another project's repair must not control current actions or graph impact: Task 7.

## File responsibilities

Modify existing `apishield/workspace.py`, `configuration.py`, `dashboard_jobs.py`, `engine.py`, `generation.py`, `browser_setup.py`, `banking.py`, `overview.py`, `graph_semantics.py` and their tests where those responsibilities already live. Add only three focused backend modules: `current_api.py` for accepted/observed context, `intent.py` for AI intent/generated checks, and `local_apply.py` for reviewed writes/recovery. Reuse `commands.py`, `editing.py`, `jobs.py` and contract-fetch helpers rather than copying them.

Frontend changes stay in `pages/Workspace.jsx`, `pages/Banking.jsx`, `workspace_flow.js`, `components/Requirements.jsx`, `RunEvidence.jsx`, `RunOverview.jsx`, existing setup/model components and `workbench.css`/`theme.css`. Reuse SemanticNetwork and RepairDiff.

Verification commands below run from the project root unless marked frontend. Python is `venv/Scripts/python.exe -B`. Keep each regression test focused on externally observable behavior.

### Task 1: Immutable browser snapshots of working files

**Files:** `apishield/configuration.py`, `workspace.py`, `jobs.py`, `dashboard_jobs.py`; tests `tests/test_local_engine.py`, new `tests/test_working_snapshot.py`.

**Interfaces:** Add `IntegrationConfig.source_mode` with `committed` default and `working` browser selection. Add `capture_working_snapshot(job) -> dict` and reuse `prepare_workspace(job) -> dict` for replaying either snapshot. Working metadata contains `source_mode`, `source_commit`, `source_hash`, `files` (path-to-content hash), exclusions and dirty status. Captured source bytes live in the job's retained `source-tree`, separate from its disposable execution workspace.

- [ ] Add regressions: dirty tracked code and eligible untracked code/tests appear in working mode; committed mode excludes them; excluded secret/ignored files never appear; symlinks/path escapes fail.
- [ ] Run `venv/Scripts/python.exe -B -m pytest tests/test_working_snapshot.py -q`; establish expected failures before implementation.
- [ ] Implement Git-assisted eligible-file inventory, content/byte limits, secret filtering and per-job immutable retention using existing path/atomic-write helpers. Retries copy retained bytes, never reread the checkout.
- [ ] Prove source hash changes on a user edit and remains pinned during retries. Run working snapshot tests plus `tests/test_local_engine.py`.

### Task 2: Accepted versus active API contracts

**Files:** new `apishield/current_api.py`; `banking.py`, `browser_setup.py`, `dashboard_jobs.py`; new `tests/test_current_api.py`, existing `tests/test_banking_demo.py`.

**Interfaces:** `capture_api_context(jobs, integration) -> dict` returns retained `base_spec`, `target_spec`, `accepted_hash`, `observed_hash`, `source_kind`, `provider_version` and integration revision. `accept_api_context(jobs, integration, context) -> dict` advances accepted state only after successful Apply. Add banking GET `/api/banking/openapi` serving a copy of the active V1/V2 contract. Reuse configured monitor documentation fetch where available; local/uploaded documentation reads current target contents.

- [ ] Add tests asserting V1/V1 has zero changes; V2 against accepted V1 produces actual changes; checking does not advance baseline; V2 -> V1 is unchanged before Apply; captured job contracts stay fixed during a provider switch.
- [ ] Run `venv/Scripts/python.exe -B -m pytest tests/test_current_api.py -q` and establish failures.
- [ ] Persist accepted contract/context under job storage per integration. Browser submit uses working mode plus captured active docs. Initialize banking baseline to V1; remove fixed V2 target coupling. Preserve ordinary CLI config behavior.
- [ ] Run current API, banking and dashboard-job regressions. Assert a failed Apply cannot accept a contract and a static uploaded document is labelled static.

### Task 3: Current endpoint and graph overview

**Files:** `dashboard_jobs.py`, `overview.py`, `repository_graph.py`, new-module `current_api.py`; new `tests/test_current_overview.py`.

**Interfaces:** GET `/api/integrations/{name}/overview` returns source/context hashes, accepted contract details, supported consumed endpoints, coverage notes, graph, most relevant current comparison and AI intent status. Reuse `scan_sources`, `build_repository_graph` and retained overview formatting. Cache only by current source/API context and invalidate on changes.

- [ ] Test an integration with no jobs returns its used endpoints and static graph; a working-file edit appears without committing; old comparison impact is absent from a fresh unaffected overview; unresolved calls remain coverage gaps.
- [ ] Run `venv/Scripts/python.exe -B -m pytest tests/test_current_overview.py -q` before implementation.
- [ ] Implement current-context overview with neutral initial impact and matching-context unresolved impact only. Avoid history mutation and repeat model calls during polling.
- [ ] Run overview, repository graph and dashboard tests; compare captured HEAD before/after to prove reads create no commits.

### Task 4: Gemini intent and independent generated checks

**Files:** new `apishield/intent.py`; `graph_semantics.py`, `requirements.py`, `browser_setup.py`; new `tests/test_ai_intent.py`, existing `tests/test_graph_semantics.py`.

**Interfaces:** `infer_intent(context, connection, *, check=None) -> dict` returns versioned inferred rules with real source references, validated graph interpretation and generated checks. `discover_test_commands(snapshot_root) -> list[list[str]]` supports existing pytest and declared standard package test tooling with explicit unsupported diagnostics. Generated checks use `tests/apishield_generated/test_*.py` for the supported Python repair flow. Returned provenance includes model and source/contract hashes.

- [ ] Test real-reference validation, invalid JSON, out-of-scope files, oversized output, duplicate rules, protected-file overwrite attempts and missing-runner diagnostics. Test no AI credential/unavailable provider leaves static overview usable.
- [ ] Run `venv/Scripts/python.exe -B -m pytest tests/test_ai_intent.py -q` and establish failures.
- [ ] Build a bounded structured request from retained source/docs/tests/graph, reusing model_client, graph validators, redaction and cancellation. Treat repository text as untrusted data. Set 120 graph nodes, 128 KiB prompt context and 4096 output tokens using existing graph limits; report larger unsupported contexts explicitly.
- [ ] Cache automatic intent by source + accepted/observed contract + model hashes. Generated tests cannot edit existing tests/hooks/config or arbitrary command lines. Preserve existing tests as independent evidence and report inadequate generated checks rather than counting empty/skipped execution as success.
- [ ] Run AI-intent and graph tests with fake clients only; verify these tests never use real configured credentials.

### Task 5: AI-only browser repair with combined validation

**Files:** `engine.py`, `generation.py`, `dashboard_jobs.py`, `editing.py`, `requirements.py`; `tests/test_local_engine.py`, `tests/test_dashboard_jobs.py`, new `tests/test_ai_repair_flow.py`.

**Interfaces:** Browser POST `/api/jobs` repair accepts model proposals only. Repair jobs consume Task 1's frozen working snapshot, Task 2's API context and Task 4's inference; retain independent generated-check files and patch evidence. Existing CLI offline candidate support remains for regression fixtures, not browser fallback.

- [ ] Test browser `proposal=example` is rejected, no-change repair makes no repair-generation call, existing and generated tests are both executed, failed/empty/skipped generated checks cannot yield validated status, and attempts reuse frozen source/checks.
- [ ] Run `venv/Scripts/python.exe -B -m pytest tests/test_ai_repair_flow.py -q` and establish failures.
- [ ] Remove browser example-candidate selection, supply captured graph/intent/docs context to generate_candidate, and discover validation commands automatically. Keep impacted-source edit restrictions; allow only separately validated new check files through their dedicated generation path.
- [ ] Retain original snapshot, reviewed replacement bytes, generated checks, hashes and usage for Apply even after execution-workspace cleanup. Preserve existing test mutation protection and command evidence.
- [ ] Run engine/dashboard/intent/repair regressions. Ensure model errors remain errors and no fixture repair is silently selected.

### Task 6: Reviewed Apply and actual banking adapter

**Files:** new `apishield/local_apply.py`; `banking.py`, `dashboard_jobs.py`, `current_api.py`; new `tests/test_local_apply.py`, existing `tests/test_banking_demo.py`.

**Interfaces:** `apply_local_repair(jobs, integration, job_id) -> dict` behind local-origin POST `/api/jobs/{job_id}/apply`. Returns application status, backup identifier and source/API context. Writes reviewed retained replacements and generated checks only. GET job report exposes application outcome. Banking reads the registered example's adapter files, with no supplied-candidate substitution.

- [ ] Test only validated model repairs apply; stale source/contract/integration/evidence is rejected; duplicate Apply is idempotent; paths/symlinks fail; existing file modes/unrelated files are preserved; HEAD/branch remain identical.
- [ ] Run `venv/Scripts/python.exe -B -m pytest tests/test_local_apply.py -q` and establish failures.
- [ ] Serialize Apply per integration, preflight all files, retain backup/recovery manifest in job storage, use existing atomic byte replacement and roll back written files on an injected failure. Advance accepted contract only after all writes succeed.
- [ ] Connect controlled banking adapter execution to applied working files. Provider switch changes no client files. Explicit demo reset restores demo-owned V1 client/provider/baseline only. Test V2 operation failures before repair and successes with a validated applied model-shaped test patch.
- [ ] Rebuild/invalidate current overview after Apply; distinguish successful application from failed refresh. Run Apply/current API/banking tests including crash/recovery manifest behavior.

### Task 7: Dashboard, overview, intent and Apply user flow

**Files:** `frontend/src/pages/Workspace.jsx`, `Banking.jsx`, `workspace_flow.js`, existing setup, Requirements and evidence components, `workbench.css`, `theme.css`; `frontend/tests/workspace_flow.test.js`, `repair-state.test.js`.

**Interfaces:** Use current overview, API context, AI intent and Apply APIs above. Primary action never changes away from the exact label `Check for API Changes` except its running state. Conditional repair review is a separate secondary action with matching integration/source/contract hashes.

- [ ] Add flow regressions for no jobs, unchanged comparison, affected comparison, validated/unapplied/applied repair, failed job, switching projects and stale async replies. Assert primary action remains compare and old/unrelated repairs do not surface as current review.
- [ ] Run `npm test` in `frontend` and establish expected failures.
- [ ] Add visible API endpoints and Semantic graph overview actions, wire comparison to active documentation, show AI-generated intent provenance/runner coverage, remove required manual rules/test fields and supplied-repair controls. Banking exposes provider V1/V2 and current applied state only.
- [ ] Add Review -> Apply states with stale/failure recovery. Enlarge dashboard action buttons and move a compact Recent activity section below them; preserve white page, blue selections, responsive navigation and dark RepairDiff.
- [ ] Run frontend tests/lint/build. Use only permitted visual evidence; session browser restriction means no alternative automation/CDP workaround. Do not claim rendered visual verification without a permitted current capture.

### Task 8: Controlled end-to-end and live AI verification

**Files:** regression tests above; add `docs/current-api-ai-repair-walkthrough.md` with truthful run/use instructions and outstanding provider limits.

- [ ] Run the targeted backend regressions in Tasks 1-6, then broader existing backend checks affected by changed config/source modes, and frontend test/lint/build once. Resolve failures before claiming completion.
- [ ] Verify HTTP serves the current built frontend. Stop/restart only this app's managed server after backend changes and after checking queued/running jobs. Do not stop unrelated services.
- [ ] Exercise V1 check -> overview -> switch V2 -> check -> explicit AI repair -> existing/generated tests -> review -> Apply -> functioning demo -> neutral current graph -> V2/V2 unchanged, against a disposable demo integration.
- [ ] Run one bounded minimal provider check before graph/intent/repair live tests. If it succeeds, record actual graph, generated-check and repair evidence including costs/usage. If it fails, retain the exact failure and leave live criteria incomplete; no repeated polling or fixture fallback.
- [ ] Document working-file behavior, recovery backup location, supported runners/source coverage and static versus live documentation. Confirm no Git commits/branches/pushes/PRs were created by Apply or this implementation.
- [ ] Report completed versus genuinely blocked acceptance criteria with links to evidence. A mocked V1/V2 integration test is not live Gemini validation.

## Self-review and execution choice

The tasks cover the approved contract flow, current overview, automatic intent/checks, AI-only repair, uncommitted Apply, dashboard changes and actual model testing. Each depends on earlier captured-context interfaces, so one native implementation sequence is recommended over separate parallel plans. Tests cover the five review-focus conditions in their owning tasks. Native execution approved and implemented. See current-api-execution-ledger.md for RED/GREEN evidence, final review fixes, HTTP checks, deviations and the unresolved live provider criteria.
