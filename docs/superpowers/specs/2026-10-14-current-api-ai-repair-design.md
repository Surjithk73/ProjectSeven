# Current API overview and AI repair workflow

Status: design and written specification approved by the user on 2026-10-14.

## Outcome and approved decisions

APIShield becomes a current-code API workspace rather than a fixed V1/V2 fixture comparison. Users connect a repository and API documentation, view consumed endpoints and its semantic graph, check the active provider for changes, request an AI repair, review validation evidence, then apply the repair to current working files. Applying creates no Git commit, branch, push or PR.

The user approved reuse of existing repository tests with AI-generated checks for missing coverage, and explicit Review -> Apply. Manual business-rule/test setup is not required. Gemini infers intent from source and API documentation; inferred intent remains labelled AI-generated. Browser repairs have no supplied/deterministic candidate fallback.

Keep the existing white/blue theme and dark diff editor. Make Check for API Changes the prominent primary dashboard action, enlarge the primary action group, and reduce/move Recent activity below it. Repair review is a secondary action only when a recent repair exists for this project and current source/contract context.

## Current gaps found in source

- `apishield/banking.py` changes an in-memory provider version but executes a shipped fixture adapter and optional supplied candidate; it does not run the registered integration's repaired files.
- Banking registration copies a fixed `base.json`/`target.json` pair, so comparisons report V2 changes even while the provider is on V1.
- `apishield/workspace.py` exports committed Git blobs; dirty working files are explicitly excluded. Repair application without a commit therefore requires a new browser source snapshot path.
- `apishield/engine.py` consumes manually configured requirements/test commands and disallows generated test files. Its isolated workspace, protected-input checks, command budgets and validation evidence should be reused.
- `frontend/src/workspace_flow.js` replaces the primary check action with review/example repair based on latest history.
- Existing AI graph interpretation enriches verified nodes with bounded groups/inferred links; it does not derive executable business checks.

## Contract and provider state

Banking starts on provider V1. Its documentation endpoint returns the contract matching the active provider version. APIShield retains the contract used by the current integration as its accepted baseline, initially V1, and reads the observed contract at each explicit check. Switching to V2 changes the provider and served docs, not the client source or accepted baseline.

V1 against V1 reports no changes. V2 against the accepted V1 baseline reports the actual contract changes and affected code. Repeated checks before Apply continue to show unresolved changes; checking never accepts a baseline implicitly. Returning to V1 before Apply makes V1/V1 unchanged again.

After a validated repair is applied successfully, accept that repair's captured target contract for this integration and rebuild the current overview from repaired working files. Further V2/V2 checks report no new contract changes. Historical comparisons and their impact highlighting remain immutable and labelled by source/contract snapshot. Current overview impact comes from current unresolved changes, not old job history; do not merely hide known failures.

Other connected repositories use their configured documentation/monitor source where available, or the current contents of their uploaded/local target documentation. Preserve existing contract-fetch validation and monitoring rules. Show which document/source was checked and when. Do not claim live polling for uploaded static documents.

## Current working-file snapshots

Add a browser workflow snapshot mode while preserving committed-source mode for existing CLI/publication workflows. Snapshot tracked working files and eligible untracked application/test files under the configured scope, respecting ignored files and secret exclusions. Reject symlinks, path escapes, unsupported submodule inputs and colliding paths. Do not recursively ingest `.git`, virtual environments, dependency directories, backups or job storage.

Record a content manifest/hash, source mode and reference commit for provenance. Capture once per job; all retries, graph creation and validation read the same retained snapshot. Never reread changing working files between repair attempts. Separate contract snapshots remain protected.

Current code overview reads that working-file snapshot and the accepted API contract, even before any API change. Reuse static source analysis and repository graph construction. List supported consumed endpoints with file/function/line links, expose documentation details, and describe unresolved/dynamic calls as coverage gaps. Do not imply all languages or runtime calls are resolved.

## AI intent, graph and validation

Reuse the configured Gemini connection and the existing requested model `gemini-3.8-flash`. Do not silently switch models/providers or use a shipped repair if it is unavailable.

The first current overview automatically requests bounded AI intent analysis when model access is available, and caches it by source + contract + model context. Repeated viewing/polling does not repeatedly spend tokens. A failed request leaves the verified static graph usable, with a visible AI failure and explicit retry. AI groups/explanations/inferred edges are distinguishable from verified calls.

Infer business invariants from source, its comments/docs, API contracts and existing tests. Validate returned references against real files/functions/nodes, retain provenance, and label intent as inferred. Inference cannot establish intended behavior that is absent or contradictory; such cases must return a diagnostic rather than a claim of correctness.

Discover existing test tooling from repository configuration and tests instead of asking users to set commands manually. Reuse supported existing runners; if no supported runner exists, report that limitation. Do not guess arbitrary executable commands from AI output.

For missing checks, Gemini generates bounded tests in a dedicated generated-test namespace. It cannot overwrite, delete or weaken existing tests, configuration, contracts or test hooks. Generate checks against captured intent/contracts before accepting a repair, retain them independently, and execute them alongside existing tests in the isolated job workspace. Require real execution evidence; generated checks that are invalid, empty, skipped or fail are not a pass. Retain generated-test provenance and distinguish existing-test coverage from generated coverage.

Repair prompts receive captured source, old/new API documentation, actual changes, verified graph relationships, inferred intent and bounded test feedback. Allow changes only to affected supported source files; generated checks use their separate validated namespace. Preserve money units, identities and error handling. Retain patch digest, captured input hashes, model usage and command evidence. Apply remains unavailable unless the repair is validated against that captured context.

## Apply to current working files

Apply is a separate explicit local browser action. It requires a validated AI repair, unchanged patch/evidence, the same integration/repository and unchanged source/observed-contract context. If anything is stale, refuse and offer regeneration; never overwrite intervening edits.

Before writing, validate every target path/content and prepare a complete backup plus recovery manifest outside the connected repository. Write only reviewed source changes and newly generated checks; preserve all other working files. If a write fails, restore changed files from the backup and report the failure. Retain backups for recovery. Neither Git history nor the user's branch changes.

Only after all writes succeed, record application state and accept the captured target contract. For banking, load the registered banking integration's actual current adapter rather than applying `candidate.json` substitutions. Restrict dynamic demo execution to that controlled example integration. Regular connected repositories are analyzed and repaired, not imported into the APIShield server as application code.

Rebuild current endpoint/graph/intent state after Apply. Invalidate caches from old source hashes. Do not retroactively mark historical failed runs as passing. If post-apply overview rebuild fails, report the applied state and failed refresh separately rather than claiming rollback occurred.

## Dashboard and controls

- Persistent primary: Check for API Changes, with honest running/disabled/error states.
- Peer overview actions: API endpoints and Semantic graph, available before a comparison or repair.
- Secondary conditional: Review repair only for a relevant generated repair; pending/failed evidence is identified accurately. Validated repairs expose Apply repair.
- Remove supplied-example repair actions and the demo's supplied V2 adapter switch from the browser user flow. Retain fixtures only for automated regression tests.
- Banking provider selector controls V1/V2; reset returns provider/client/baseline coherently to V1 after explicit reset. Do not reset other repositories.
- Business rules become AI-inferred intent with provenance; remove required manual rules/test fields from the normal setup path. Keep connection/coverage failures discoverable.

## Verification and completion criteria

1. V1 demo + Check reports no changes; endpoint catalog and graph are available.
2. Switch provider to V2; Check reports actual changes and affected code. Subsequent checks before Apply do not erase them.
3. All browser repairs request Gemini; offline fixture proposal routes are inaccessible from the user workflow.
4. Existing tests and separately generated checks execute; failed checks cannot yield validated/applicable repairs.
5. A validated repair shows the dark review diff. Apply writes working files without changing Git HEAD/branch and makes the demo use the reviewed adapter.
6. Fresh V2 overview has no stale historical impact; V2/V2 Check reports no new changes.
7. Stale files/contracts, malicious paths, protected-file edits, partial-write failures and duplicate Apply are handled safely.
8. Current-source snapshots remain immutable across retries and secret/ignored files are excluded.
9. AI connection, graph/intent and repair are tested with real provider requests. Unit tests/mocks do not count as live success. If provider access is blocked, report the exact failure and leave those live criteria pending.
10. Existing monitoring, jobs, cancellation, CLI committed snapshots and GitHub draft preparation retain their established behavior.

## Live AI check on 2026-10-14

The configured connection reports Developer API and model `gemini-3.8-flash`. A real minimal request returned HTTP 503 after approximately 9.5 seconds. One bounded retry also returned HTTP 503 after approximately 3.68 seconds. This establishes attempted requests, not working model access. Provider failure does not justify fixture fallback or a successful-live-testing claim. No further retry loop was started.

## Out of scope

Research evaluation, patent work, hosting, accounts, early trials, autonomous commits/pushes/publication, new general-purpose language analyzers and executing arbitrary connected applications inside the dashboard server.
