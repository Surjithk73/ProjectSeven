# Explicit requirements verification — 13 October 2026

The approved function-scoped requirements increment is implemented in the shared CLI/service engine and local browser workspace. No Cloud migration, live inference, customer-code testing, external deployment or GitHub publication occurred in this phase.

## Delivered behavior

- Optional strict requirement declarations in config version 1; old integrations remain compatible.
- Canonical rule hashes and versioned source/operation/requirement/test relationships. Line insertions preserve call identities; unresolved scope/URL evidence is reported explicitly.
- Source intent appears only as an unconfirmed suggestion. Developers save drafts and explicitly confirm unchanged definitions; edits invalidate confirmation.
- Relevant confirmed rules require committed, collectable selected tests. Missing functions/classes/files, missing checks and unresolved affected scopes return needs_input before generation.
- Bounded pytest discovery and per-rule validation use the existing protected workspace, process ownership, integrity and deadline controls. Actual passing JUnit records are required; skips, xfails, errors, failures and empty checks cannot establish success.
- Browser-owned rules publish immutable configuration versions. Repository/source/test-context changes invalidate confirmation; full-context edit tokens reject stale writers. Server-managed/example integrations are read-only. Historical records remain unchanged.
- The shipping example contains a real identity/weight rule. Existing installed examples refresh their config safely while preserving original source and prior records.
- Readable rule/source/operation/test relationships and independent command evidence appear in reports. Green check labels require actual passing command evidence; scan reports never imply test execution.

## Automated evidence

| Verification | Observed result |
| --- | --- |
| Initial declaration/graph regressions | RED 19 failed → GREEN declaration/runtime cohort 56 passed |
| Initial enforcement/JUnit regressions | RED 15 failed → GREEN 34 passed |
| Browser requirement endpoints | RED 3 failed → GREEN combined cohort 99 passed, 1 POSIX skip |
| Immutable historical snapshot / old-example refresh follow-ups | 3 passed |
| Full suite before final review | 257 passed, 1 POSIX skip, 1 dependency warning; 207.17 seconds |
| Final reviewer regressions: missing selectors, repository context and discovery deadline | RED failures reproduced → GREEN 4 passed |
| Final full offline Python suite | **260 passed, 1 POSIX-only skip, 1 dependency warning; 446.79 seconds** |
| Final frontend behavior suite | **13 passed** |
| Frontend production build | Passed; main JS 373.74 kB / 116.30 kB gzip, CSS 51.62 kB / 10.81 kB gzip |
| Frontend lint | Exit 0; six existing legacy demo warnings, no new requirements/workspace warnings |

Real engine transactions verify correct endpoint migration; exact value and refund semantics reject candidates that pass deliberately weak ordinary suites. Parameterized requirement checks run all cases. Missing/untracked tests, bad selectors, skipped/xfailing checks and deadlines cannot create a requirement-validated patch. Original source and protected targets remain unchanged. Ordinary jobs without requirements still work.

The independent reviewer inspected the whole working change, independently ran 23 focused tests and reproduced two backend gaps without inference. Three Important findings were fixed in one regression-driven pass: complete selector discovery, pending-save input loss and source-context confirmation/concurrency. The scan-copy finding was fixed as an evidence-truthfulness issue. The author's tests verify the fixes; no second independent review is claimed. Review artifact: `.superpowers/requirements-review.md`.

A Windows report-reader race observed during real API testing was reproduced using a transient PermissionError and fixed with bounded read retries. Malformed evidence still returns an honest failure after retries; this does not hide persistent corruption.

## Real browser acceptance

The application was rebuilt and restarted through its actual launcher. Browser acceptance exercised:

- Shipping example repair, first job `a3862c4c3b5e4ddc924768dbf5551bec`, then final-selector-discovery job **`5d102d04a89b47b5b6b82c726e6788af`**. Both validated with actual selected requirement checks; the latter retained successful discovery evidence before candidate validation.
- Browser-owned `shipping-browser-check`: add a draft, reject `--help` as a test selector while retaining input, correct and save, explicitly confirm, edit text and observe renewed draft status, then reload after actual server restart and verify persistence.
- During a real pending draft PUT, all five source/rule/check form fields and the save/close controls were disabled. During a pending confirmation PUT, Add rule, confirm, edit and remove were disabled. The final unchanged saved rule was confirmed successfully.
- Requirement outcomes distinguish declarations from Checks passed; the report shows the pinned source operation and declared test relationship.
- A real scan of the browser-owned integration offered its source-intent comment as a suggestion. Review suggestion prefilled the scoped draft; saving retained `origin=source_intent`, `confirmed=false` and no invented check references. The scan correctly said no explicit requirement checks ran.
- Desktop 1440 × 1000 and mobile 390 × 844 layouts. A long selected-test summary initially overflowed on mobile; wrapping corrected the document from scroll width 396/client width 375 to **375/375**, with no horizontal overflow. The mobile editor also measured **375/375**.

The final example report records status validated, requirement passed and discovery exit zero. `git status --porcelain -- src tests` on the example repository was empty. Its retained patch independently passed `git apply --check`. No original source patch was applied.

Screenshot evidence is retained under `.superpowers/requirements-ui/`, including desktop repair, mobile editor and final mobile/desktop result captures. These are local delivery artifacts rather than publication figures.

## Boundaries and next milestones

This is a usable requirement workflow, not complete semantic analysis or a paper result. Test links are developer declarations; passing checks cannot prove that their assertions cover all prose or all possible behavior. Function/operation relationships remain limited to the supported direct Python requests/httpx subset. Field-flow/transitive analysis, controlled benchmark baselines/ablations, literature/prior-art assessment, hosted workers/monitoring and GitHub proposals are still pending. A disposable checkout is not an OS sandbox; use trusted local repositories.

Cloud provider selection and live model quality testing remain deferred at the user's request. No academic novelty, patentability or universal repair-quality claim follows from this implementation.
