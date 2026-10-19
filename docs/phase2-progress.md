# SDD ledger — plan: docs/superpowers/plans/2026-10-11-phase2.md

Base root commit: 90c4fcc. Existing attached worktree/branch reused; nested client repository is not a Phase 2 edit target.

Ruling: The approved architecture and latest explicit implementation instruction authorize Phase 2. Detailed spec/plan capture implementation choices rather than introduce another approval gate. Cost if wrong: reversible scope/UX adjustments.
Ruling: Restrict this local phase to local Git repositories; remote GitHub retrieval belongs with the authorized adapter in Phase 4. Cost: user clones a repository first.
Ruling: Retain the Phase 1 mutable demo and add separate allowlisted dashboard jobs sharing the CLI engine. Cost: two clearly labeled local workflows until product UI migration.
Ruling: Continue the existing attached worktree and PowerShell ledger adaptation. Cost: branch still named phase1-foundation and manual bookkeeping.

Pre-flight: Task 1 owns configuration/store/runtime; Task 2 consumes exact named interfaces and owns engine modules; Task 3 consumes run_job/store and owns adapters. No shared implementation files. Config/job defaults agree across tasks; protected tests and original source never become patch targets. Existing demo globals are not engine dependencies.

Task 1: approved — commits 463a924, 4bcfa3c and b65411d; 36 focused runtime tests pass. Review fixed cross-process cancellation publication, preserved original contract snapshots and bounded Windows reader-contention retries.
Task 2: approved — commits b3fc45b, 316815b and ef79c9d. Independent specification and quality reviews passed after regressions for lexical scopes, late HTTP import rebinding, executable permissions, CRLF context, terminal deadlines and queued worker-loss recovery. Final engine coverage: 47 passed and one POSIX-only case skipped within the integrated suite.
Task 3: complete, scoped and whole-branch reviews approved — CLI and allowlisted dashboard jobs share the engine; all 16 adapter tests pass within the final suite. Installation, shipping example, CI and local workflow documentation are delivered. No unresolved Critical or Important review findings remain.

Ruling: Root adapter scaffolding and documentation proceeded while the single Task 1 implementation agent ran; no second implementation subagent was dispatched until Task 1 review passed. Cost: adapter acceptance remains RED until its engine dependency exists.

Final verification: full suite 195 passed, 1 POSIX-only skip, 1 dependency warning in 183.75 seconds. Frontend 3 tests and both builds passed; Compose configuration passed. The final wheel installed in a fresh external environment completed shipping scan, compare, offline repair and report; git apply --check, unchanged original source and workspace cleanup all passed. See docs/phase2-validation.md for evidence, review corrections and platform/product limits.

Completion ruling: retain the existing attached worktree/branch without merging, pushing or publishing. The original dirty checkout and nested client repository remain untouched. Research evaluation and later roadmap phases are not claimed complete.
