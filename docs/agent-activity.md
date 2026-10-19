# Agent activity and API documentation flow

The user selected an Agent activity tab inside repair results, opened automatically on a new repair. The original archived AgentPipeline supplied the stage-navigation reference; its obsolete MCP/IPS and automatic-healing claims were not copied into the current engine.

## Documentation input

Connections currently accept uploaded old/new JSON OpenAPI contracts. With a configured monitoring source URL, checks fetch that JSON OpenAPI document and compare it against the accepted contract; scheduled monitoring runs while the local app is running and monitoring is enabled. Without a URL, checks use the saved uploaded target contract. The banking example obtains the currently active V1/V2 OpenAPI contract directly from BankingDemo. Arbitrary documentation webpages are not crawled or discovered automatically.

## Actual execution progress

The existing engine now persists activity transitions in events.jsonl before preparation, source/contract analysis, Gemini intent/check inference, generated-test baseline execution, patch generation, temporary patch application, validation and review readiness. Patch retries retain their real attempt numbers and return the current stage from validation to repair. No stage completion is driven by a cosmetic timeout. Applying the repair is a separate explicit action; the activity projection reads the stored application status.

GET /api/jobs/{id}/activity reads a bounded 512 KiB tail, returns at most 200 completed JSON-line events, rejects a symlink and redacts output again before returning it. Partial trailing JSON is ignored while a worker is appending. Full retained evidence is not rewritten or deleted. Logs show operational events and command stdout/stderr, not model private reasoning or service-account contents.

The Agent activity tab polls at two-second intervals while active/running, pauses when hidden, stops after terminal status and ignores responses after selection changes. Execution time uses recorded start/finish timestamps and remains separate from human review time. Commands can be expanded for output, with a 12,000-character UI display cap. Failures, cancellation, missing-input outcomes and retries remain explicit. Old runs keep their genuine existing logs; unrecorded stage transitions are not fabricated. Cancellation and code-review actions reuse existing guarded actions.

## Verification and scope

New backend tests cover persisted progress, redaction, partial lines, bounded output and missing jobs. The browser AI repair-flow regression verifies stage ordering through generated baseline, candidate application and passing validation. Frontend projection tests cover retry backtracking, terminal failure, review/apply separation and missing legacy phase evidence. Frontend build and 63 tests pass; lint retains six incumbent warnings. The mechanical design detector found no issues in the new component/styles. Fresh rendered browser verification remains unavailable under the prior browser-access restriction.

No credentials, paper datasets, publication archives or original saved application files were changed. This adds observability to the existing repair process; it does not change its acceptance or Apply policy.

## Change notice, chronological log and generated-check failure (2026-10-15)

The completed comparison now begins with a compact API change notice containing changed/added/removed endpoint counts, affected source-call count, a short endpoint list and the primary Ask AI to update action. The old bottom-of-page Prepare a tested fix / Generate AI repair block was removed. The action remains gated on localized impact and an available model connection.

Execution logs now render in persisted chronological order, append at the bottom and follow new entries while the reader remains near the bottom. Scrolling upward pauses following; Jump to latest resumes it. Explicit scoped foreground colors override inherited summary/link colors, with larger log text on the dark surface. Failure details include classification, failing test, source location, exception, consequence and next action.

Actual failed run b1db37d04bd347d784afc1bf512c64eb failed because tests/apishield_generated/test_bankclient_v2.py:29 referenced call_args[1][json], where json was an undefined variable rather than the intended string key. The original incompatible client's endpoint assertion failed earlier, masking that latent check defect during baseline qualification. After the candidate corrected the endpoint, the NameError became reachable. All three candidate attempts reused the same invalid generated check.

Generated checks now undergo symbol-table name validation before execution. The exact retained check is rejected with Generated check references undefined name: json. The existing bounded regeneration loop receives that diagnostic and regenerates checks before candidate patching. Names in imports, parameters, closures and comprehensions remain supported. No test assertion or expected value is silently rewritten, and model patch generation remains unable to edit tests. Pytest JUnit failures now retain named-test messages, and engine errors include that diagnostic instead of only the generic validation failure. Historical failure explanations are derived from retained command output without rewriting historical evidence.

Verification: 49 intent/activity/requirements tests passed before the last parameterized regression; final intent/activity tests passed 11 cases including automatic regeneration of an undefined-name check. The engine/AI-flow suite passed 51 tests with one skip. All 65 frontend tests passed; production build passed; lint retained six incumbent warnings after unused-local cleanup. The mechanical detector found no issues in the changed components/styles. The actual historical run was diagnosed as a generated_check_error with the NameError, failing test and line 29.

Automatic approval review rejected the attempted local server restart with blocked by policy and no more specific reason. No alternate restart was attempted and no new live AI repair verification is claimed. Backend changes require a manual restart. Browser visual verification remains unavailable under the earlier access restriction. The built frontend can be served by the existing server independently of backend reload.

## Behavior inference provider deadline recovery (2026-10-15)

Run b08960f0bb3b4d10b08e0109543a4109 completed source scanning and contract comparison, then received Google's HTTP 504 DEADLINE_EXCEEDED during behavior inference. No candidate was generated and no validation test was run. Intent inference previously used a hard-coded default 60-second request deadline, ignored the job's configured 120-second command budget, and did not recover transient provider errors.

The engine now passes the configured request timeout and a shared stage deadline capped at twice that timeout and the remaining overall job budget. With the reported configuration, each connection has at most 120 seconds and the whole inference stage at most 240 seconds, still inside the 600-second job limit. One retry is permitted for request timeouts and Google 429/500/502/503/504 responses. The retry waits one second, gets a fresh deadline-bounded transport, and checks cancellation and the remaining job budget. Authentication/permission and non-transient errors are not retried. Content regeneration remains independently limited to two returned responses and uses the same stage deadline; test assertions and acceptance criteria are unchanged. Successful response usage remains retained, while provider failures without usage are not assigned fabricated token counts.

Actual retry messages appear in the intent stage's persisted execution log. Exhaustion stops with a concise IntentServiceError. Historical 504 errors also receive a provider-failure explanation through the activity API, and the current-stage UI prefers that explanation over raw SDK exception JSON. Failed runs still cannot apply working files.

Regression coverage includes 504 recovery, persistent 503 exhaustion, no 403 retry, cancellation before retry, no retry after deadline, engine budget/callback wiring, and historical provider-failure explanations. A read-only live check against the failed run's retained banking source/contracts succeeded in 11.26 seconds, returning three inferred rules and one generated check file accepted by static validation. This was actual inference using the private managed service account, not a simulated response; it did not execute tests or generate/apply a candidate. The script and redacted result are in reports/intent-timeout-verification-2026-10-15/. The live provider did not fail during this check; recovery from a 504 was verified with injected SDK errors rather than claimed as an observed provider retry.

No server restart was attempted for this change because the earlier restart action was rejected by automatic approval review. The edited backend must be activated with a manual restart; the isolated live check ran directly against the edited Python module.

Final verification: targeted backend suites passed 136 tests with one existing skip; 66 frontend tests and the production build passed. Lint completed with the same six incumbent warnings. No full live candidate-generation/validation run or browser-rendered verification is claimed for this timeout change.

## Persistent Apply confirmation (2026-10-15)

The previous Apply handler opened a newly generated current-overview job, replacing the repair result and losing the visible outcome. Apply now keeps the selected repair and tab, confirms the persisted application response immediately, and refreshes that same result for rebuilt graph evidence. A persistent Changes applied successfully notice appears above the result tabs, receives focus/scroll on the success transition, reports the updated-file count and retained recovery copy, and offers the updated graph and (for banking-example) banking app. The Apply button shows Applying changes while pending. Applied patch headings and review copy use past tense. Claims refer to recorded validation rather than guaranteeing all application behavior.

A failed Apply never produces the notice. If Apply succeeds but graph/result refresh fails, success remains visible and the action error identifies a refresh problem. Older polls cannot overwrite an applied result with pre-Apply evidence; selecting a different result still works normally. Persisted application status restores the notice when reopening the repair. No backend, acceptance policy, original working files, or application data was changed by this UI implementation.

Verification: 71 frontend tests and the production build passed, including five Apply flow/state regressions. The design detector found no issues in the changed UI targets; lint retained the six incumbent warnings. Browser-rendered verification remains unavailable under the earlier access restriction. These frontend changes need a browser refresh, not a backend restart.
