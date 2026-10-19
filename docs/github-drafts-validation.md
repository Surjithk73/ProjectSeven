# GitHub draft acceptance — 13 October 2026

Observed real publication: [Surjithk73/APIGuardTesting draft PR #1](https://github.com/Surjithk73/APIGuardTesting/pull/1).

The approved empty repository was initialized with only a synthetic shipping fixture: README, two API clients, an empty Python package initializer, independent tests, and two API contracts. The create-only README bootstrap was followed by a non-force `main` advance to the complete fixture. No ProjectSeven/customer files, credentials, repository settings or permissions were published or changed.

| Observation | Result |
|---|---|
| Original fixture tests | Both failed on the old routes |
| Offline two-file repair | Validated; two independent tests passed |
| Captured remote base | `3219602578dea64f8a912dc80ec1d2aea57cc615` |
| Retained repair | `d2d449eceb534b15bac879a1656d10e3` |
| Offline revalidation | `df073bb6f43e42a7b9b800de0c181e71`, validated |
| Patch SHA256 | `b043b96991b98a87cf1b553d1f288fbd4af5311386ff266da1fbe6b1a1fd2298` |
| Proposal | `3fb5262890b7cddeb48f606d7dcbd8e66a5135a0039fd99b106cf8232be88f20` |
| Head | `codex/apishield-3fb5262890b7cddeb48f606d` |
| Published commit | `274b1e774b5c1962a307bc063292c9219c104b85` |
| PR | #1, open, draft true, base `main` |
| Remote diff | Exactly `src/cancel.py` and `src/create.py`, one line replaced in each |
| Duplicate publish | Same PR number/URL; repository contains one PR |
| Restart | Target/proposal/link/head/commit restored |
| Source preservation | All seven source files identical; clone remains clean |
| Paid AI calls in this stage | Zero |

The fixed tests check exact parcel identity, integer gram weight, exact cancellation identity, routes and response values. No explicit requirement declarations were selected for this controlled job; the preview and body say so. GitHub CI was not verified. The PR remains a draft; no merge, close, branch deletion or force update was performed.

Desktop/mobile browser checks used the real frontend. A mocked-GitHub round exercised target save, prepare, complete patch/body preview, explicit publication and restored link. The controlled real round exercised repository connection, target access check, full two-file preview, explicit draft publication, desktop/mobile publication display and application restart. At 390px, document width and scroll width were both 390px. Target/base/patch/evidence races, collisions, cancellation, duplicate requests, interrupted local jobs and lost remote responses are covered by offline regressions; destructive remote failure injection was not performed.

Retained local evidence: `C:/Users/surji/.apishield/github-draft-2026-10-13` contains baseline output, synthetic seed manifest, source hashes, original patch, repair result, remote base/PR metadata and duplicate-publication response. Browser screenshots and test logs are in this plan's ignored Superpowers workspace. Credentials are not included.

Publication checks cannot freeze GitHub while other developers update branches. It stops at the next detected stale checkpoint and preserves partial effects for explicit reconciliation. GitHub CLI errors are sanitized and bounded; authentication remains the existing local CLI credential store.

Final verification after the review fixes: the full Python suite passed **426 tests**, with one POSIX-only skip and one upstream Starlette deprecation warning (347.63 seconds). Frontend tests passed **27/27**; the production build succeeded; lint exited successfully with the same six pre-existing demo warnings. `git diff --check` passed.

The single independent final review identified three Important issues and no Critical/Minor findings. Five regression cases reproduced all three before fixes: approval revision replacement during reservation, mutation of either verification contract snapshot, and recovery of a closed/merged PR after head deletion and base advancement. The coordinator now revalidates approval under ownership, hashes/checks both contract snapshots, and searches retained matching PRs independently of branch existence. The focused 33-test publication/API/CLI suite passed after this one fix pass. No second review or remote failure injection was performed.

## Implementation decisions

- Reserve the optional verification job ID before creating the job, enabling interrupted-preparation cleanup. Cost if wrong: a small compatible API/test extension.
- Use separate target and proposal-preview revisions, so new preparation invalidates an older approval even when the target is unchanged. Cost if wrong: one extra API/UI/test revision field.
- Bootstrap the empty controlled repository with a create-only README, then advance `main` without force. Cost if wrong: one extra synthetic bootstrap commit. Normal publication never advances base branches.
- Reuse the resumed 87-test regression result after the interrupted Task 3 helper instead of rerunning an already-green suite. Cost if wrong: helper output is replaced by the retained equivalent command log.
- Keep guarded routes in `publication_api.py`, separate from lifecycle coordination. Cost if wrong: one additional small module.

No final-review findings were deferred or declined to judge. The original dirty repositories and the managed development branch/worktree are preserved. The plan's temporary review files are retained because automatic approval review previously rejected recursive cleanup; that rejection was not bypassed.
