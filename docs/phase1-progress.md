# SDD ledger — plan: docs/superpowers/plans/2026-10-11-phase1.md

Approved spec: IMPLEMENTATION_PLAN.md Phase 1. Product code starts only after this recorded approval.

Ruling: Existing approved plan serves as design authority; detailed task plan is an execution breakdown, not a new scope approval gate. Cost if wrong: adjust task details.
Ruling: Use an attached worktree overlaid with current project files and an independent clone of nested client history. Original repositories remain unchanged. Cost: eventual handoff must account for two repositories.
Ruling: Use PowerShell and tracked progress ledger instead of Bash-specific skill scripts on this Windows host. Cost: bookkeeping maintained manually.
Ruling: Execute only approved Phase 1; later product phases remain planned. Cost: no hosted customer product in this batch.

## Pre-flight interfaces
| Tasks | Shared contract | Decision |
|---|---|---|
| 1 / 3 | Provider control and logs | Task 1 creates routes; dashboard proxies them |
| 1 / 2 | Client tests and target version | Validator runs complete client suite with target version |
| 2 / 3 | Structured outcome | Dashboard consumes atomic result.json, not stdout |
| 1 / 4 | Reset and provider launch | Offline reset defaults to docstring-based SIG |
| 3 / 4 | Model-free graph build | Business docstrings are explicit labels, not new LLM inference |

Task 1: complete — provider/runtime/OpenAPI aligned, all client workflows covered, offline reset, caller-supplied invoice address.
Task 2: complete — fresh full-file plans, grouped transactional edits, bounded retries, honest tests and optional judge evidence, atomic terminal outcomes.
Task 3: complete — source-hashed offline SIG, relocation/concurrent publication handling, real provider controls, truthful dashboard/UI, repair lock and timeout recovery.
Task 4: complete — dependencies, local launcher, Docker/CI definitions, documentation, integration validation, independent review.

Review: independent reviewer identified provider response mismatch, missing timeout rollback, and relocated graph ownership. Regression tests demonstrated failures before fixes. Reviewer reran 25 relevant tests after fixes and found no new Important issues. Minor graph publication and UI wording findings were also addressed.

Verification: full Python suite 96 passed with one upstream Starlette deprecation warning; frontend presentation tests 3 passed; both production builds passed; both lint commands exit 0 with 19 warnings; Compose config, PowerShell parser, pip check and git diff whitespace check passed. See phase1-validation.md for limits.

Ruling: preserve the attached branch/worktree for continued development; do not merge or publish while original repositories contain unrelated work. No additional integration approval is necessary to leave the reviewable implementation in place.
Ruling: keep auto-heal opt-in and merge disabled; preserve missing judge/CI evidence. Single-file legacy publication creates drafts; the complete multi-file publisher remains Phase 4.
Ruling: Docker daemon is unavailable; configuration validation is evidence of syntax only, not runtime verification. Live model repair quality and research novelty remain unassessed.
