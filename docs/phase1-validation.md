# Phase 1 implementation and validation

The approved Phase 1 foundation is implemented in the attached `codex/phase1-foundation` worktree. This is a repeatable development demo, not yet a customer-ready hosted product.

## Delivered behavior

- NexusPay serves version-specific typed contracts and exports the same contracts as OpenAPI fixtures. All eight client workflows have executable checks.
- Money remains integer cents. Refunds use the refund endpoint. Invoices preserve billing period and accept real caller address data. Analytics preserves actual provider outcomes.
- Reset restores V1 service source and builds SIG from explicit docstrings without inference. Source hashes trigger graph refresh, including removal of the last HTTP call and checkout relocation.
- Repair planning uses current complete files. Application rejects ambiguous, overlapping, invalid and ineffective candidates. Retries restore the same original base, and failed repairs restore bytes across client files.
- Complete client tests determine validation. Optional judge scores can be unavailable and cannot substitute for passing tests. Results are written atomically and the dashboard consumes those results.
- Provider switching talks to the actual provider. A repair lock prevents overlapping changes. Timeout recovery terminates descendants before restoring the parent snapshot; uncertain process cleanup retains the lock for manual recovery.
- UI distinguishes failed, needs-input, no-change and validated outcomes. Low scores remain low. Automatic repair is opt-in; merging is disabled.
- Setup includes pinned dependencies, environment example, fixed ports, a Windows launcher, development Compose definitions, and CI.
- The legacy single-file GitHub helper creates drafts and reports missing CI honestly. Complete multi-file publication remains Phase 4.

## Evidence

Final full-suite command, run with the existing workspace Python environment:

```text
python -B -m pytest -p no:cacheprovider -q --tb=short
96 passed, 1 warning in 19.86s
```

The full-loop integration uses the real native oasdiff binary, actual LangGraph nodes, real client pytest validation and deterministic candidate fixtures. V1 clients pass, V2 initially breaks, a correct multi-file candidate validates, and an incorrect cents conversion is rejected through three attempts with byte-exact restoration. Generators and revisions are replaced by fixtures, so this does not measure model quality. CI installs the pinned native Linux oasdiff binary for these checks; locally these two integration tests skip if no suitable binary is available.

An actual subprocess/descendant timeout test passed on Windows: the descendant was stopped before a delayed file mutation. A real-provider TestClient bridge verifies dashboard version controls rather than only mocked response shapes. Graph relocation and simultaneous publication checks passed.

Frontend presentation tests: 3 passed. Both frontend production builds passed. Both lint commands exited 0, with 6 APIShield warnings and 13 SwiftPay warnings. These warnings are not a clean lint result. One Python warning is an upstream Starlette/AnyIO deprecation.

Compose configuration, PowerShell launcher parsing, CI YAML parsing, pip dependency consistency, and Git whitespace checks passed. The independent reviewer reran 25 relevant tests after the reported Important issues were fixed and found no new Important findings.

## Remaining limits

Docker engine was stopped, so image builds and container runtime were not exercised. The launcher was parsed but its five-service startup was not exercised. Browser layout was not visually inspected. Tests validate selected workflow semantics, not arbitrary integrations or all possible model patches. Live Gemini repair quality, research novelty, and patent eligibility were not established. No GitHub publication or merge was performed. Durable isolated jobs, broader requirements, complete reviewed PR publication, evaluation experiments and hosting remain later phases in IMPLEMENTATION_PLAN.md.

The original project repositories were preserved. Root source and nested client history are retained separately; the nested client changes are committed as `9d34871` on `codex/phase1-foundation`.
