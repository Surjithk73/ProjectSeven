# Browser workflow ledger

Base: e264b43, attached isolated worktree codex/phase1-foundation.

Ruling: User explicitly requested complete implementation and testing, so execute the concrete design/plan without another approval handoff. Existing approved roadmap supplies product intent; the latest request prioritizes browser usability. Cost if wrong: reversible workflow adjustments.
Ruling: The user confirmed the local browser app and explicitly excluded authentication; public deployment remains separate. Cost if wrong: hosting is a follow-up implementation.
Ruling: After the user requested a UI/UX revamp, replace the demo-first screen with the migration review desk, keeping a restrained white/slate/violet family and native text. Impeccable seed 1a384b48 selected grounded direction 6; implementation is code-led without raster assets. Cost if wrong: reversible visual changes.
Ruling: Use existing React/Lucide/CSS and filesystem job storage rather than adding a UI framework/database. Cost if wrong: additional components/storage can be introduced when concrete requirements exceed these tools.

Task 1: complete — onboarding and engine/report queue fix commit 6da8201, plus regression-driven immutable updates and session-key validation changes in the final commit. Initial acceptance RED 5 failed; original onboarding/adapter GREEN 15 passed. Expanded pre-review GREEN 17 passed; full suite includes nine browser acceptance tests.
Task 2: complete — real workspace, form/settings/report components, history, selection guards, responsive CSS. Initial frontend RED missing helper; GREEN 6 tests; review regressions expanded final GREEN to 8. Final build and lint exit 0; no warnings in new workspace. Impeccable design disposition ship after six desktop/mobile/form/settings captures.
Task 3: complete — start_app.bat/ps1 and stop_app.ps1, built static serving and usage docs. Actual launcher startup/shutdown process-tree checks passed; direct app ran real jobs in the browser and retained records over restart. Full suite 205 passed, 1 POSIX-only skipped, 1 dependency warning in96.94seconds. See docs/browser-workflow-validation.md.

Final: fixed stale report/patch selection — selection generation regression RED→GREEN, frontend8/8.
Final: fixed Windows dependency probe — empty environment launcher regression RED→GREEN, full205passed/1skip.
Final: fixed corrupt job history render — minimal failed-record regression RED→GREEN, frontend8/8.
Final: fixed model-key validation input echo — invalid key response regression RED→GREEN, full205passed/1skip.
Final: Ruling: reviewer set aside broader scanner semantics, hosted/job-auth redesign, automatic oasdiff installation and cross-process registry writers — current local app uses the verified engine, one loopback server and installed native tool. Hosted/multi-server requirements are later roadmap work; cost if wrong: those deployment modes require additional implementation, not current verification claims.

No new deferred minor review findings. Existing legacy demo lint warnings remain outside the revamped workspace. Preserve attached worktree/branch, original checkout and nested client repository; no merge, push, publishing or deployment.
