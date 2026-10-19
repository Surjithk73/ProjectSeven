# Local monitoring validation — 13 October 2026

Status: implementation, browser acceptance and verification completed. One independent review found four Important issues; all were corrected in one fix pass with regression tests and a green final suite. No second review is claimed.

The implementation continues in the existing isolated worktree. Original ProjectSeven/client_app files were not used as edit targets. No AI generation, GitHub publication, hosting or paid request was performed in this increment.

## Automated evidence

- Fetch tests: 23 passed, including real loopback HTTP, DNS destination policy/pinning, redirect loop/metadata rejection, streamed/declared size limits, invalid JSON, idle delays and trickled status/header/chunk-size bytes under the absolute deadline.
- Backend monitor/adapter/setup checks: 72 passed, with the existing Starlette dependency deprecation warning.
- Shared engine/runtime/requirements regression batch: 171 passed, 1 existing platform skip, 1 dependency warning.
- Frontend: 18 Node tests passed; production build passed; lint has the 6 existing legacy warnings and no new monitoring warning.
- Pre-review full Python suite: 308 passed, 1 existing platform skip, 1 dependency warning in 332.26 seconds. A subsequent test-only check with a real second process also passed, confirming durable claim exclusion across processes.
- Post-review targeted backend checks: 80 passed; the additional shutdown-reservation regression and all eight focused review boundary cases passed.
- Final post-fix full Python suite: **317 passed, 1 existing platform skip, 1 dependency warning in 182.53 seconds**. Frontend: **18 passed**, production build passed and no new lint warnings.
- No offline tests require Gemini or GitHub credentials. Explicit repair routing uses a fake key and a captured submission, without model generation.

## Actual browser acceptance

Controlled integration: `monitor-browser-check`, using the existing synthetic shipping Git repository and a temporary loopback contract fixture on port 8013. The fixture's response variants are synthetic and not production-provider observations.

1. Connected the repository/contracts through the browser, configured the URL, trusted-local opt-in, default 60-minute interval and first-download baseline.
2. Initialization and unchanged checks created no alert/job. A formatting-only response also created no change.
3. A target contract moving POST `/labels` to `/labels/create` created one comparison job, `7a2c6957…`; its real engine report showed one affected call, `src/parcel.py:create_label`.
4. Repeating that response reused the change/job. Paused monitoring still allowed an explicit manual check.
5. Accepted the downloaded target using the explicit confirmation copy. The UI displayed acknowledgment, without claiming code repair or test validation.
6. Explicit rescan produced a second comparison, `448f8f1a…`, retaining the earlier job identity.
7. Invalid JSON displayed a recoverable failure while retaining the previous successful observation and accepted baseline. A valid response recovered successfully.
8. Resume re-enabled scheduling. A three-second delayed response completed after switching to `shipping-browser-check`; its state did not appear in the other integration. The delayed fixture intentionally returned the old base contract, producing a legitimate reverse comparison `2dcdf735…` against the accepted target.
9. Restarted through the existing stop/start launchers. Monitoring settings, enabled schedule, accepted baseline and both change records survived. Paused the fixture integration after verifying recovery.
10. At 390×844, edited the form, rejected HTTP without local opt-in while retaining the input, cancelled the edit, and ran a manual check. Confirmed 44px controls and no horizontal overflow: document width 375px within the 390px viewport (scrollbar accounts for the difference).
11. Desktop/mobile inspection revealed initially understated controls; one CSS fix batch added the consistent button treatment. The confirmation round showed usable controls and visible keyboard focus. Viewport override was reset.

Screenshots: `.superpowers/monitoring-ui/final-desktop.png` and `final-mobile.png`. These files are local acceptance artifacts, not claims about hosted availability.

## Independent review and correction

One fresh gpt-6-astra reviewer inspected the monitoring change and surrounding interfaces, read-only. It found four Important issues and no Critical or Minor findings. All four were accepted and corrected in one fix pass; no second independent review is claimed.

- The original inactivity timeout could be defeated by trickling HTTP protocol bytes. Reproduced with failing header/chunk-size tests; every underlying response read now receives the remaining absolute deadline.
- Job creation could precede durable association with its change. Reproduced by terminating a real subprocess after construction; reservations now persist the identity before construction, recovery materializes missing failed evidence without allocating another identity, and changed configurations discard stale reservations. Covered process loss before/after construction and before dispatch, plus graceful shutdown during reservation.
- Polling could update an edit's optimistic revision while retaining old inputs. Added a draft-revision regression and verified the real browser: a second local client changed interval 60→61; after polling, the old draft save returned conflict, retained its input and left 61/revision 6 unchanged. Explicit reload recovered; the fixture interval was restored to 60 and paused.
- Preparation failures could leave an overdue schedule and no error. A failing scheduled configuration test now passes: attempt/error state is recorded before loading configuration, the accepted baseline survives, and retry follows the interval rather than every scheduler tick.

The reviewer set aside live Gemini generation and GitHub publication because they are deferred in this scope. That decision stands; those capabilities still need later live acceptance, and no current live validation is implied.

## Decisions carried from execution

- Used standard-library `http.client` with pinned sockets instead of httpx: preserves TLS hostname verification and enforces a remaining deadline on reads without relying on transport internals. Cost if wrong: replace the focused fetch implementation.
- Added a dedicated explicit rescan endpoint/control: supports new committed code analysis without defeating automatic contract deduplication, and retains prior job IDs. Cost if wrong: one extra local endpoint/control to maintain.

The broader product still needs the separate GitHub CLI draft-PR workflow, deeper supported impact analysis and per-integration environment setup. AI integration/live testing, formal research evaluation, patent work, hosting and early trials remain deferred.
