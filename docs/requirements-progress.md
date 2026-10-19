# Explicit requirements implementation ledger

Base: 6b38c49. Approved spec and plan: docs/superpowers/specs/2026-10-12-explicit-requirements-design.md and docs/superpowers/plans/2026-10-13-explicit-requirements.md. The user approved implementation on 13 October 2026; native execution stays in the existing isolated worktree.

Preflight: existing versioned config snapshots, protected source/tests, bounded subprocess runner and immutable browser registry cover the plan's shared interfaces. Python/pytest, React/Lucide/CSS and stdlib suffice. Original checkout and nested client_app remain untouched. No inference or Cloud migration in this phase.

Task 1: declaration/scanner/config cohort RED 19 failed → GREEN 56 passed. Strict declarations, canonical hashes, stable call identities, declared test/scope links and unconfirmed source-intent suggestions implemented.

Task 2: acceptance/XML cohort RED 15 failed → GREEN 34 passed. Real wrong-unit and refund-to-charge candidates passed weak ordinary suites but failed requirement checks. Missing files/scopes/checks stop before inference, skips/xfails cannot pass, and original source remains unchanged. Timeout status regression RED 1 → GREEN in the 99-test combined cohort.

Task 3: endpoint cohort RED 3 failed → combined GREEN 99 passed, 1 POSIX skip. Snapshot/legacy-example follow-ups GREEN 3 passed. Immutable updates, explicit two-step confirmation, read-only ownership and persistence implemented. A Windows transient report-read defect reproduced RED 1 → GREEN through bounded PermissionError retries.

Task 4: frontend initial RED 2 → GREEN 10; readable relationship mapping RED 1 → GREEN 11. Real browser example job a3862c4c3b5e4ddc924768dbf5551bec validated with one actual requirement check. Browser draft creation, invalid-selector recovery without input loss, confirmation and edit invalidation were exercised. Full pre-review suite: 257 passed, 1 POSIX skip, 1 dependency warning in 207.17 seconds.

Final review: one fresh gpt-6-astra reviewer inspected the entire working change, ran 23 focused checks and reproduced missing-selector and repository-context defects offline. Review artifact: .superpowers/requirements-review.md. No second review is planned; one consolidated regression-driven fix pass follows.

Final: fixed missing test functions/classes reaching generation — two regressions RED→GREEN; actual bounded pytest collection runs after setup and before inference.
Final: fixed pending saves accepting newer edits — frontend regression RED→GREEN, definition updates frozen and every form/Add control disabled during saves.
Final: fixed repository changes retaining confirmation and accepting stale editors — API regression RED→GREEN; source/test-directory changes clear confirmation, full config edit token replaces declaration-only optimistic concurrency.
Final: fixed collection timeout outcome remaining pending — existing deadline regression RED→GREEN after applying final-state handling to collection as well as test execution.
Final: fixed scan text implying test execution — copy regression RED→GREEN; empty outcomes now say no explicit requirement checks ran.

Ruling: use a full integration edit token for browser concurrency in addition to the canonical requirements hash — review reproduced stale editors after repository changes even with unchanged rule text — cost if wrong: clients must adopt the new edit token; only newly introduced endpoints are affected.
Ruling: treat the review's scan-copy Minor as an evidence-truthfulness defect and fix it in the consolidated pass — scans do not run configured tests and must not imply otherwise — cost if wrong: only clearer UI wording.
Final: Ruling: process/OS isolation against malicious repository code remains excluded — this is the approved trusted-local workflow, with existing integrity/credential/process controls — cost if wrong: hostile repositories require a separate isolation implementation before use.
Final: Ruling: semantic sufficiency of developer-authored tests remains the developer's responsibility — declared links and passing tests do not prove prose or universal behavior — cost if wrong: insufficient tests can miss semantic errors; UI/docs retain this limitation.
Final: Ruling: field/transitive analysis, hosting and live model quality remain deferred — this increment implements function/operation-scoped constraints as approved — cost if wrong: these capabilities require later work and cannot be advertised as completed.

Final regression suite, responsive/browser acceptance and delivery evidence are recorded in docs/requirements-validation.md after execution. No deferred minor review findings remain.

Final: full offline suite 260 passed, 1 POSIX skip, 1 dependency warning in 446.79 seconds; frontend 13 passed; build and lint exit 0 (six existing legacy warnings). Actual browser re-tested final example with successful test discovery and requirement outcomes. Original fixture src/tests Git-clean and retained patch apply-check passed.
Final: mobile long-test-summary overflow reproduced at scroll/client 396/375 → corrected to 375/375. Mobile editor also 375/375. Real pending PUT showed all five editable fields disabled; confirmation PUT disabled Add rule as well. Restart retained the browser declaration and old run history. Tasks 1–4 complete; see validation report for exact artifacts and limits.
Backend/API/test implementation committed as c2eb4b9. Real browser source-intent adoption also saved origin source_intent, confirmed false and an empty check list; no inferred statement became an acceptance gate.

Native adaptation: use PowerShell and a durable Markdown ledger instead of Unix-only plan helper scripts; tests and commits supply the same evidence. Preserve the attached worktree rather than deleting it at completion.
