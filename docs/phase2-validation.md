# Phase 2 validation and handoff

Phase 2 is complete: a standalone local Python integration engine, an installable CLI and allowlisted dashboard job endpoints. The approved design and implementation plan are under `docs/superpowers/`. Work remains on the attached `codex/phase1-foundation` branch; the original ProjectSeven checkout and nested client repository were not edited or merged into.

## Delivered behavior

- `apishield scan`, `compare`, `repair`, `report` and `cancel` share durable job storage and the same reusable engine used by dashboard jobs.
- Each execution exports a pinned Git commit into a disposable workspace. Dirty source changes are excluded and reported. Original source files are never automatically patched.
- Conservative Python analysis locates direct requests/httpx calls and reports unsupported scopes, wrappers and unresolved bindings. Native oasdiff compares supplied JSON contracts.
- Repair proposals can edit only relevant configured source, with protected tests/contracts, bounded commands, cancellation and process-loss recovery. All configured tests and independent integrity checks must pass before a patch is retained as validated.
- Reports retain revision, contract hashes, comparison, attempts and command evidence after source workspace cleanup. An unfamiliar shipping example demonstrates an endpoint migration with preserved package identity and gram weight.

## Final verification

Environment: Windows, Python 3.13.3, Node 26.5.0. Final production engine revision: `ef79c9d`, plus the reviewed CLI/dashboard/package adapter files committed with this report. Credentials were empty during offline integration checks.

| Check | Observed result |
| --- | --- |
| `python -B -m pytest -q` | **195 passed, 1 skipped, 1 warning in 183.75 seconds** |
| Frontend `npm run test -- --run` | **3 passed** |
| `npm run build` in frontend and swiftpay_frontend | Both passed |
| `docker compose config --quiet` | Passed |
| Standard isolated `pip wheel . --no-deps` | Built `apishield_local-0.2.0-py3-none-any.whl` |
| Fresh external environment, installed console command | Help, scan, compare, offline repair and report passed |
| Shipping repair artifact | `git apply --check` passed; original source bytes and tracked files unchanged; workspaces removed |
| Independent reviews | Runtime, engine specification, engine quality, adapters and whole Phase 2 approved; no unresolved Critical or Important findings |

The skipped regression checks POSIX executable permissions. Windows exercised the cross-platform permission-restoration regression. The warning is Starlette's dependency deprecation for an AnyIO alias. Linux CI is configured, but a remote CI run was not performed here. Frontend checks occurred before the final Python-only review fixes; no frontend files changed afterward.

The final installed-wheel smoke ran outside the checkout without PYTHONPATH, importing the engine from the fresh environment's site-packages. The wheel SHA-256 was `b6685cddf9173117fec5611484c4153ca9d6a1ba993fdc8d410a30610276950c`. Retained local smoke job IDs: scan `503afd6c5a0b45b68dda520f1f9b360e`, compare `e37ad2f6083540778def4dba1d850eb6`, repair `a465ce15228240de873fb90fbad7643a`. These are development evidence, not required application configuration.

## Review corrections

Regression-driven fixes cover cancellation/publication races, contract snapshot integrity, bounded Windows atomic-write contention, Python method lexical scopes and late HTTP import reassignment, source permission preservation, exact CRLF generation context, terminal deadline enforcement and queued worker-loss recovery. Adapter regressions cover allocated-job failure cleanup, dead dashboard owner cleanup and valid JSON output on ASCII terminals with Unicode paths.

A prior integrated run exposed a functional fixture's 10-second subprocess budget under host load. Its report correctly recorded a timeout rather than success. The functional fixture now allows 30 seconds per command and 120 seconds per job; dedicated strict timeout/deadline regressions retain their explicit budgets. The final serial suite above passed against the frozen code.

## Limits and next use

Run the tool on demand before an API upgrade, or invoke it from CI; a continuously running developer laptop process is unnecessary. Follow `docs/local-workflow.md` and `examples/shipping/README.md` for installation, configuration and patch review.

This phase executes trusted repository commands on the local host; disposable copies are not a security sandbox. Analysis coverage is partial, and configured tests determine behavioral evidence. Live Gemini transport and model repair quality were not exercised; provider boundary options were verified offline. Docker runtime services were not started. Dashboard job endpoints are local and have no tenant authentication; the existing browser UI still presents the Phase 1 demo. Hosted scheduling, GitHub publication and product job screens remain later phases.

Commit pinning, contract hashes and attempt evidence provide a reproducible foundation for research experiments. Offline tests establish implementation behavior, not empirical superiority or patent novelty. Research evaluation still needs datasets, baselines, metrics and ablations as later project work.
