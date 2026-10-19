# CinemaFlow implementation verification — 2026-10-19

## Delivered scope

The implementation is on `feature/cinemaflow-multi-provider` in ProjectSeven. The existing main snapshot remains at `7e69ad7d1ffe98165dc03e99d002648785c78767`. Independent theatre/payment providers, the CinemaFlow client, multi-provider project identity, manual/automatic orchestration, GitHub proposal tracking, managed deployment/rollback, provider-aware UI and Windows launch/setup/reset tools are implemented.

The initial V1 client setup is draft PR [APIGuardTesting #2](https://github.com/Surjithk73/APIGuardTesting/pull/2), head `c471361338413061d99549363f5a7f82d9cecd6a`. Both `cinema-client` checks passed on that head. No PR was merged and no collaborator invitation was sent. Existing shipping files/history remain in that repository. AI candidates used for qualification were applied only to temporary copies, not committed into this V1 baseline.

## Verification evidence

| Check | Observed outcome |
|---|---|
| Full offline Python regression suite, after reviewer fixes | 521 passed, 1 skipped; 590.51 seconds; one existing Starlette/AnyIO deprecation warning |
| Final frontend tests | 81 passed |
| Frontend production build | Passed |
| Frontend lint | No errors; six existing warnings in legacy components |
| Final targeted HTTP/project/API/launcher tests | 11 passed after the last launcher changes |
| PowerShell scripts | Parsed successfully with the PowerShell AST parser |
| Nondefault-port runtime | Three real HTTP services started on allocated ports, isolated booking passed, owner stopped all managed children |
| Live managed Google connection | `gemini-3.8-flash`, successful response, 10 prompt and 6 completion tokens, 3.74 seconds |
| Live payment-only V2 migration | Actual Gemini candidate validated on attempt 1; real HTTP browse/seats/booking/amount/idempotency/smoke verification passed |
| Live combined-provider V2 migration | Actual Gemini candidate validated on attempt 2; the same real HTTP verification passed with both providers V2 |
| Browser verification | CinemaFlow V1 booking, booked-seat state, provider overview, desktop/smaller-width layout inspected; final preview retained in the report folder |

The final HTTP smoke test uses the deployment helper's 25-second allowance. An earlier concurrent verification run exceeded its original 10-second test timeout; an isolated rerun passed, followed by the final green targeted run. This is recorded as a test deadline adjustment, not evidence that provider calls always complete within a fixed latency.

Detailed live candidate/attempt records and diffs: [qualification report](../../reports/demo-verification-2026-10-19/README.md). Some model usage fields are redacted by the existing retained-event sanitizer; no replacement counts were invented. These are implementation qualification checks, not the academic 120-task benchmark or a completed two-machine rehearsal.

## Fresh review and corrections

A fresh read-only whole-branch review identified six lifecycle issues. Each received a failing regression followed by a passing correction:

1. Reconcile interrupted GitHub publication rather than leaving the workflow indefinitely awaiting publication.
2. Refresh clean source after a merged-but-failed deployment before generating the next update.
3. Recheck retained provider snapshots/workflow freshness at publication side-effect boundaries.
4. Verify show browsing and seat availability as well as booking in deployment smoke checks.
5. Do not resurrect a superseded workflow when a provider contract combination recurs.
6. Retain authenticated failed deployment receipts and rollback/error evidence without accepting their provider baselines.

## Implementation decisions

- Direct execution uses a feature branch in the current checkout, as requested; it does not replace main.
- Explicit file/provider HTTP-receiver bindings extend the conservative scanner. Unattributed origins remain unresolved rather than being assigned to a provider by path alone.
- Provider SQLite state is external to client releases. Reset touches only managed payment/theatre databases; source resets use a new clean baseline and forward GitHub commit/PR rather than destructive Git history changes.
- Configurable service ports retain 8100/8101/8102 defaults. In deployment mode B's private JSON is authoritative; use matching provider ports in A's registration.
- Open Sans is self-hosted under its OFL license to match the requested theme. Contrast and small text found in the one-pass design detector were corrected; the cinema screen arc and the requested font are intentional design choices.
- APIShield's original port-8002 process and banking runtime were not restarted by this work. A separate local preview was used for UI checks.

## Pending physical rehearsal and account setup

Follow [setup.md](setup.md) and [rehearsal.md](rehearsal.md). Still required:

1. Add/accept `techASH5` collaborator access at the end, as requested; authenticate the deployment identity locally on B.
2. Human review/merge of the initial CinemaFlow setup PR, then a clean checkout of its merged baseline on A.
3. B's actual private IPv4 address and installation folder; Private-profile LAN firewall setup and reachability checks.
4. Real two-machine manual cycle: break payment V2, generate/validate, publish, second-account review/merge, exact-SHA deployment, booking verification and cleared current impact.
5. Real automatic theatre-V2 cycle and simultaneous-change/outage/failed-deployment rehearsal. The deployment state machine has regression coverage; this document does not claim it has already deployed to the second computer.

Research datasets, manuscripts and publication results were not changed by this implementation.
