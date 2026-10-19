# Two-machine movie-booking demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Execute directly here after user approval.

**Goal:** Demonstrate CinemaFlow breaking after independent theatre/payment API changes, receiving a validated AI-generated GitHub PR, and recovering automatically after a human merges it.

**Architecture:** Reuse APIShield monitoring, repair, graph, activity, and publication services on System A. Run independent HTTP providers, a client release, and an outbound deployment helper on System B; group provider integrations under one client project and coordinate updates per repository. GitHub records PR, merge, CI, and deployment evidence.

**Tech Stack:** Existing Python/FastAPI, React/Vite, pytest, Git/GitHub CLI, PowerShell, SQLite; Windows on both machines. No new orchestration platform or inbound webhook service.

**Spec:** [Agreed workflow and proposed design](../specs/2026-10-19-two-machine-movie-demo-design.md).

## Global Constraints

- Manual mode is the default; automatic edit mode ends at a validated PR. Human review and merge are mandatory.
- Both Windows machines use the same Wi-Fi/LAN; service ports are configurable, defaulting to 8002 on A and 8100/8101/8102 on B.
- Payment and theatre providers are simulations; no real payments and no official Google Pay integration.
- AI updates use the existing managed JSON service-account connection; no credentials enter Git, prompts, test workspaces, or deployment receipts.
- Current single-provider configurations, banking examples, and historical evidence remain readable.
- Provider identity includes origin/provider ID, method, and path. Shared client repositories serialize automatic updates.
- Existing loopback browser policy and bounded LAN fetch opt-in remain enforced.
- Deploy only an associated, merged PR's exact revision after successful CI. Advance provider baselines only after verified deployment.
- Current code goes to ProjectSeven; deployed movie client goes to APIGuardTesting, preserving existing history and shipping files.
- App implementation starts only after this plan is approved. The initial requested snapshot publication is a separate authorized action.

## Review Focus

1. Both providers change during one PR: no lost event, duplicate PR, or stale patch application (Tasks 4–5).
2. Provider or GitHub becomes unreachable: retain evidence and expose the failing phase without reporting recovery (Tasks 4–6).
3. Merge is successful but client deployment fails: rollback and keep unresolved impact visible (Tasks 6–7).
4. Endpoint paths collide across providers or are dynamic: namespace correctly and show uncertain attribution (Task 3).
5. Reset or restart encounters user work: limit reset to dedicated demo state and preserve remote history/provider databases (Tasks 2, 6, 8).

## Delivery order and file ownership

Tasks 1–2 establish the independent demo. Task 3 provides multi-provider identity. Tasks 4–6 close the monitoring-to-deployment loop. Task 7 exposes the real state, and Task 8 rehearses it. Existing files named below are verified in the current checkout; new files are proposed implementation locations.

| Area | Main files | Responsibility |
|---|---|---|
| Providers | `demo/providers/theatre.py`, `payment.py`, `state.py`; `demo/contracts/` | Independent V1/V2 HTTP services, durable simulated state |
| Client template | `demo/movie-client/movie_booking/`; `demo/movie-client/.github/workflows/ci.yml` | Deployable client source copied to APIGuardTesting, tests and CI |
| Project model | `apishield/projects.py`, `project_store.py`; `configuration.py` | Client project and provider child configuration, migration |
| Graph identity | `apishield/repository_graph.py`, `analysis.py`, `comparison.py` | Provider-qualified calls, inventory and impact attribution |
| Automation | `apishield/automation.py`; `monitoring.py`, `monitor_state.py` | Durable automatic dispatch and repository coordination |
| PR lifecycle | `apishield/publication.py`, `publication_state.py`, `github_cli.py` | Existing publisher integration, merge/CI/receipt reconciliation |
| Deployment | `demo/deployment/agent.py`, `release.py`, `receipt.py` | B-side polling, exact-SHA releases, rollback and receipts |
| API/UI | `apishield/project_api.py`; `dashboard_api.py`; existing frontend workspace and activity components | Settings, provider filters and lifecycle state |
| Operations | `demo/scripts/`, `docs/demo/` | Setup, diagnostics, reset and rehearsal |

## Task 1: Publish a recoverable current-project snapshot

**Files:** Existing changed/untracked project files; `docs/demo/snapshot-inventory.md` (new). No application behavior changes.

**Interface:** Produces the actual ProjectSeven baseline commit SHA and a documented list of excluded private/runtime material. Do not invent a SHA.

- [ ] Inventory tracked/untracked files, ignored material, repository sizes, archives, and credential candidates. Inspect flagged content locally without printing secrets.
- [ ] Confirm origin, GitHub identity, and remote divergence; preserve user modifications and existing remote commits. Exclude actual credentials, environments, caches, runtime state and private backups; document large artifact handling if GitHub limits require a separate release.
- [ ] Stage the audited snapshot, run `git diff --cached --check`, inspect the staged inventory, commit with `chore: preserve current APIShield project snapshot`, and push normally to `Surjithk73/ProjectSeven`. No force push.
- [ ] Compare remote and local commit IDs; record upload success separately from CI status. A failed CI job is not a failed upload and is not called passing.

## Task 2: Build independent providers and the movie client

**Create:** `demo/providers/{theatre,payment,state}.py`, `demo/contracts/{theatre-v1,theatre-v2,payment-v1,payment-v2}.json`, `demo/movie-client/movie_booking/{app,theatre_client,payment_client,booking}.py`, `demo/movie-client/movie_booking/static/`, `demo/movie-client/tests/`, dependency lockfiles, and `demo/movie-client/.github/workflows/ci.yml`.

**Interfaces:** Theatre serves shows, seats, holds, confirmations and its active OpenAPI contract. Payment serves idempotent create/status operations and its active contract. Client adapter functions are `list_shows()`, `get_seats(show_id)`, `hold_seats(show_id, seat_ids)`, `create_payment(booking_id, amount_paise, currency, idempotency_key)`, and `confirm_booking(hold_id, payment_id)`; each accepts an injected HTTP client/base URL through construction rather than hardcoded localhost.

- [ ] Add failing tests: V1 booking succeeds; payment V2 fails the unchanged V1 adapter; theatre V2 fails the unchanged V1 adapter; exact paise and INR remain unchanged; repeated payment key charges once; two holds cannot reserve one seat; expired holds/declines cannot confirm booking.
- [ ] Run `venv/Scripts/python.exe -m pytest demo/movie-client/tests -q`; confirm tests fail for missing implementations before implementing.
- [ ] Implement SQLite-backed providers and the V1-only client. Provider admin changes active version independently; client deployments cannot reset provider state. Build the CinemaFlow flow and separate provider control screens using existing frontend conventions/theme.
- [ ] Run the same tests plus provider tests in `tests/test_movie_providers.py`; verify the intended V2 incompatibilities are asserted rather than accidental test failures. Start three real HTTP processes in a test fixture and verify cross-process calls.
- [ ] Commit `feat: add independent cinema client and versioned demo providers`. Introduce the template under `movie_booking/` in APIGuardTesting using a normal branch/PR, preserving existing shipping files. Retain the template revision in ProjectSeven and record the deployed repo revision; later AI changes target APIGuardTesting only.

## Task 3: Add client projects, provider children, and qualified graph identity

**Create:** `apishield/projects.py`, `apishield/project_store.py`, `tests/test_projects.py`, `tests/test_provider_identity.py`.
**Modify:** `apishield/configuration.py`, `repository_graph.py`, `analysis.py`, `comparison.py`, `overview.py`.

**Interfaces:** `ProviderBinding(provider_id, integration_id, base_url, path_prefix)`, `ClientProject(project_id, repository, providers, automation_mode)`, `load_project(project_id) -> ClientProject`, `resolve_provider(call_url, bindings) -> str | None`. Store project metadata under the existing external APIShield data directory, with schema version and atomic writes; leave current IntegrationConfig v1 loading intact.

- [ ] Write tests for migration of an existing integration to one provider; two providers sharing `/payments`; path-prefix matching; unresolved dynamic hosts; provider-only and combined graph filters. Assert historical job IDs and contract hashes remain intact.
- [ ] Run `venv/Scripts/python.exe -m pytest tests/test_projects.py tests/test_provider_identity.py -q` and confirm the new behavior is missing.
- [ ] Add the parent project layer and provider-qualified graph keys. Retain existing integrations as child job targets and maintain current single-integration API compatibility.
- [ ] Rerun the new tests with `tests/test_current_overview.py` and `tests/test_repository_graph.py`; all must pass.
- [ ] Commit `feat: group provider integrations under client projects`.

## Task 4: Connect real monitoring to manual and automatic edit modes

**Create:** `apishield/automation.py`, `tests/test_automation.py`.
**Modify:** `apishield/monitoring.py`, `monitor_state.py`, `dashboard_jobs.py`.

**Interfaces:** `dispatch_change(project_id, change_id) -> WorkflowRecord`, `set_automation_mode(project_id, mode, expected_revision)`, where mode is `manual` or `automatic_edit`. A WorkflowRecord has `workflow_id`, provider change IDs/hashes, source SHA, mode revision, state, job/publication IDs, timestamps and last error. Reuse existing job/activity stores for detailed evidence.

- [ ] Write tests: manual mode detects but makes no model call; automatic mode dispatches once; unchanged polling makes no model call; missing AI/GitHub/repo configuration prevents activation; simultaneous provider changes queue per repository; restart reconciles a persisted dispatch; failed generation does not retry on every poll; disabling mode stops new dispatches.
- [ ] Run `venv/Scripts/python.exe -m pytest tests/test_automation.py -q` and confirm the dispatch tests fail.
- [ ] Connect completed actionable comparisons to the existing AI engine, with durable deduplication and repository-level ownership. Default monitoring interval is 5 minutes for this demo, with explicit Check now; do not reduce global minimums.
- [ ] Rerun new tests with `tests/test_monitoring.py`, `tests/test_monitor_state.py`, and `tests/test_ai_repair_flow.py`. Verify timeouts, connection failures and exhausted generation attempts expose an actionable phase/error and preserve snapshots.
- [ ] Commit `feat: orchestrate monitored updates with explicit automation modes`.

## Task 5: Publish validated updates and track human merge/CI state

**Create:** `apishield/merge_tracking.py`, `tests/test_merge_tracking.py`.
**Modify:** `apishield/publication.py`, `publication_state.py`, `github_cli.py`, `automation.py`.

**Interfaces:** `reconcile_publication(publication_id) -> PublicationRecord`, including exact PR head SHA, merge SHA, base branch, review state and CI result. Existing prepare/publish remains the only publication route; automatic mode invokes it after validation. Initial PRs may remain drafts until the human marks them ready; they are never automatically merged.

- [ ] Write tests for automatic validated publication, manual preview/publish gates, invalid candidates producing no PR, interrupted publication reconciliation, duplicate ticks producing one PR, human-closed unmerged PR producing no deployment, changed main requiring refreshed validation, and CI results belonging to a different SHA being rejected.
- [ ] Run `venv/Scripts/python.exe -m pytest tests/test_merge_tracking.py -q` and confirm new lifecycle assertions fail.
- [ ] Extend the existing publisher and GitHub CLI wrapper with read-only PR/review/merge/check polling. Set a fixed proposal identity and source/contract hash manifest in PR metadata. Require current provider snapshots/source revision before publication; queue remaining provider work until the preceding PR is resolved and refreshed.
- [ ] Run the new tests and existing `tests/test_publication.py`, `tests/test_publication_prepare.py`, `tests/test_github_cli.py`. Verify stale heads never inherit old validation evidence.
- [ ] Commit `feat: track reviewed API updates through GitHub merge`.

## Task 6: Automatically deploy merged client releases on System B

**Create:** `demo/deployment/{agent,release,receipt}.py`, `demo/scripts/{start_system_b,stop_system_b}.ps1`, `tests/test_demo_deployment.py`.

**Interfaces:** `find_deployable_merge(project_config) -> DeploymentCandidate | None`, `deploy(candidate) -> DeploymentReceipt`, `verify_receipt(receipt, workflow) -> bool`. Candidate pins repository, PR/proposal ID, merge SHA, successful CI SHA and provider hashes. Receipt includes deployment ID, status, start/end times, deployed SHA, previous SHA, live provider hashes, health/smoke results and sanitized error.

- [ ] Write tests for an approved merged candidate, unmerged PR refusal, pending/failed CI refusal, SHA/hash mismatch, idempotent polls, rejected unexpected receipt author, interrupted deployment recovery, failed health rollback, and retention of provider databases across restart. Assert no shell deletion/move escapes dedicated release directories.
- [ ] Run `venv/Scripts/python.exe -m pytest tests/test_demo_deployment.py -q`; confirm missing deployment behavior fails.
- [ ] Implement 10-second outbound polling, exact-SHA release preparation, locked release pointer switching and client-only restart. Use private helper config for deployment identity; authenticate locally. Preflight tests use isolated provider fixtures; post-start booking smoke uses a dedicated namespace and idempotency key.
- [ ] Publish `apishield/deployment` status and a sanitized receipt on the associated PR using GitHub's existing status/comment APIs. A polls and validates them before rebuilding deployed-source graphs and accepting affected provider baselines. Preserve unresolved provider changes and historical impact reports.
- [ ] Run the deployment tests plus `tests/test_current_api.py` and graph tests; simulate a deployment failure and prove rollback is recorded as failed compatibility rather than a successful V2 deployment.
- [ ] Commit `feat: deploy verified merged cinema client revisions with rollback`.

## Task 7: Expose provider health, modes, and deployment progress in the UI

**Create:** `apishield/project_api.py`, `frontend/src/components/ProviderOverview.jsx`, `frontend/src/components/DeploymentStatus.jsx`, `frontend/tests/project-workflow.test.js`, `tests/test_project_api.py`.
**Modify:** `dashboard_api.py`, `frontend/src/pages/ApiShield.jsx`, `frontend/src/components/{IntegrationSnapshot,Monitoring,AgentActivity,GitHubPublication,SemanticNetwork}.jsx`, `frontend/src/workspace.js` and their existing CSS/helpers.

**Interfaces:** `GET /api/projects/{id}`, `PATCH /api/projects/{id}/automation` with revision check, `GET /api/projects/{id}/workflows`, `POST /api/projects/{id}/providers/{provider_id}/check`. Mutations use the existing loopback browser guard. Provider/settings responses return public metadata only; preserve existing single-provider routes.

- [ ] Write API/state tests: mode persists server-side; cosmetic localStorage values cannot enable automation; provider errors are independent; a merged PR is shown awaiting deployment; only a verified receipt produces Deployed and verified; rollback keeps attention visible. Add UI tests for provider filtering and manual/automatic action visibility.
- [ ] Run `venv/Scripts/python.exe -m pytest tests/test_project_api.py -q` and `npm --prefix frontend test`; verify new assertions fail before implementation.
- [ ] Apply Impeccable and ui-ux-pro-max when implementing the UI. Replace the cosmetic automatic-check control with real state, add two provider cards and project mode, extend Agent activity through review/merge/deployment, and show current deployed SHA. Preserve stable tabs, bottom-following readable logs, white/blue design and useful failure explanations.
- [ ] Run API tests, frontend tests/build/lint, then inspect both manual and automatic flows at desktop and smaller widths. Verify every successful/failed/pending label corresponds to retained evidence.
- [ ] Commit `feat: show multi-provider monitoring and deployment evidence`.

## Task 8: Prepare both machines and rehearse the complete cycle

**Create:** `demo/scripts/{check_environment,start_system_a,reset_rehearsal}.ps1`, `docs/demo/{setup,github-accounts,rehearsal,troubleshooting}.md`, `tests/test_demo_launchers.py`.

**Interfaces:** Environment report returns command versions, allowed repository URLs, provider reachability, available ports and nonsecret authenticated usernames. A/B configuration is local; public examples contain no fixed personal LAN address or credential. Rehearsal report records real source/merge/deployed SHAs and links.

- [ ] Write launcher tests for missing prerequisites, port conflicts, unreachable B, dirty client checkout and reset scope. Reset refuses unmanaged paths/user changes and never force-pushes or rewrites GitHub history.
- [ ] Run `venv/Scripts/python.exe -m pytest tests/test_demo_launchers.py -q`, implement launch/reset diagnostics, then rerun until passing. Document private-network firewall setup without automatic policy mutation.
- [ ] Run the full offline Python suite and frontend tests/build. Record any skipped live checks explicitly. Keep research datasets/manuscripts unchanged.
- [ ] Rehearse on both actual Windows machines: healthy V1 booking; payment V2 break; manual Ask AI to Update; validated PR; second-account review/merge; automatic exact-SHA deploy; successful booking and cleared current impact.
- [ ] Repeat theatre V2 in automatic mode; verify no human action until PR review. Then exercise simultaneous changes, provider outage, a failed candidate and failed deployment/rollback. Retain actionable failure evidence; do not manufacture a successful AI outcome.
- [ ] Record actual PR links, source/merge/deployment SHAs, provider versions, CI results and timestamps. Commit `docs: record two-machine demo setup and verified rehearsal` only after the report distinguishes completed and unverified checks.

## Inputs needed before the live rehearsal

1. Reviewer's GitHub username/profile URL, plus confirmation they accepted APIGuardTesting collaborator access. The publisher is currently `Surjithk73`.
2. B's private IPv4 address (PowerShell `ipconfig`, active Wi-Fi adapter), and the intended B installation folder.
3. B deployment GitHub username, if different from the reviewer. Local browser/CLI login supplies credentials securely; no passwords, tokens, private keys or one-time codes are needed in chat.

These inputs configure the rehearsal; the implementation can use local test processes and temporary repositories until the machines are available. No additional product-scope choices are outstanding.

## Approval scope

Approval authorizes Tasks 2–8 and their repository changes, tests, and demo setup. Human review/merge remains part of the demonstration. The separate current-project snapshot push was already requested. No application implementation has been performed by creating this plan.
