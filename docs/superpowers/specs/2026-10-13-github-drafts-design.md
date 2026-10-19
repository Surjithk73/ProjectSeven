# Reviewable GitHub draft proposals

Status: written design approved by the user; implementation plan prepared for review. No publisher implementation or remote writes have occurred.

## Intended outcome and constraints

A developer reviews a validated local repair and deliberately turns its complete source diff into one GitHub draft pull request, with traceable requirements and test evidence. A company can use the same workflow against a repository the signed-in developer can write. The existing local no-login application, shared engine and original source checkout are preserved. There is no automatic merge, deployment or publication from monitoring/AI generation.

The user selected existing GitHub CLI sign-in and `Surjithk73/APIGuardTesting` for controlled testing. Read-only checks on 13 October confirmed account `Surjithk73`, ADMIN repository permission, an empty repository, no default branch and no pull requests. Testing therefore includes a synthetic shipping fixture on `main`, prepared outside the original repositories. No ProjectSeven source, credentials or customer data is seeded there.

Cloud AI is completed with documented limits. This stage adds publication; deeper impact analysis and external project environments follow separately. Research evaluation, patent work, hosting and early trials remain deferred.

## Approach

Recommended: a focused adapter using the installed `gh` CLI and GitHub Git-data APIs. Construct one tree/commit containing all changed source files, then create a deterministic branch and draft PR. This avoids touching the user's checkout, invoking repository hooks or relying on a source checkout's push credentials. The same validated engine remains responsible for candidate checks.

Alternatives: extending the legacy PyGithub helper would retain its token settings, single-file assumptions and merge capability; a separate clone-and-push workflow would require another credential/hook boundary and temporary Git checkout management. The new browser workflow will not call the legacy demonstration publisher or its merge tool.

## User experience

An integration gains an explicit GitHub target: `owner/repository` and base branch. A guarded local setup action checks CLI availability, signed-in identity, repository visibility/write permission and an existing base branch. Store only target metadata outside source, version it, and show errors without authentication output. No tokens are requested, displayed or saved by APIShield. Empty repositories need an initial base before normal publication.

For a validated repair, **Prepare draft PR** performs local reconstruction/revalidation and remote read-only checks. It shows the target, captured base commit, every changed file, patch preview, validation summary and the exact proposed title/body. This preparation makes no GitHub write and no AI call. A prepared proposal has a server-issued identity tied to target revision, source commit, patch digest and verification evidence.

**Create draft PR** is the explicit write action after the user can inspect that proposal. Display preparing, ready, publishing, published, stale, failed and reconciliation-needed states. Once published, show **Open draft PR** and the repository/base/head/commit details after restart. Repeated clicks return the existing PR instead of creating another. Cancellation may stop local preparation; after remote publication begins, reconcile partial effects rather than promise rollback. No remote branch/PR deletion or automatic merge is included.

The UI retains patch/report downloads. A validated job without a configured target remains usable locally. Failed, cancelled, scan/compare or needs-input jobs cannot publish. A missing source revision, unavailable original commit or stale remote base requires a new repair; the app never guesses a base or silently rebases.

## Source and evidence boundary

Publication starts from a retained validated repair, its pinned source commit and complete patch. Add a validation-time patch digest to new job evidence; older jobs without that digest require regeneration before publication. Verify recorded identity/digest and reject changed artifacts before preparing.

Reconstruct the pinned source in an isolated copy, apply the retained patch as untrusted input, and require the complete diff to contain only the originally allowed, impacted Python source files. Reject path escapes, symlinks, submodules, binaries, added/deleted/renamed files, protected tests/contracts/configuration, no-ops and known secret-file/private-key markers. A changed Python file's contents are visible in the proposed diff; the tool cannot infer whether every application literal is confidential.

Before offering publication, run the existing configured tests and confirmed requirement checks again through the guarded engine with an explicit offline candidate reconstructed from the retained diff. Do not infer again or alter tests to obtain a pass. Retain this verification as a separate linked job, preserving the original result. Its protected-test, environment-stripping, cancellation and finite-budget behavior stays in force.

The selected remote base tip must exactly equal the original job's pinned source commit; repository paths and all edits then refer to that same committed tree. An unrelated repository or advanced base fails preflight even if textual application would appear possible. The app publishes changed source blobs only; it does not upload full contracts, raw command output, local paths, credential material or job directories.

The PR body includes the concrete migration, complete file list, pinned base/patch identity, linked local job IDs, configured-test outcomes, confirmed requirement/check summaries and model/provider metadata where available. State that local tests passed and GitHub CI is unverified until GitHub supplies actual check evidence. Omit invented confidence scores, novelty claims and issue-closing directives derived from untrusted source text.

## Publication, duplicates and interrupted work

Use a durable identity derived from target repository/base, source commit and patch digest; choose a stable `codex/apishield-…` branch from that identity. Save a publication reservation before any GitHub writes and serialize ownership across concurrent local requests/processes. Persist safe target, expected commit/tree/file identities, phase, error/recovery details and eventual PR URL atomically outside source. Never overwrite the repair result to represent publication.

Recheck target revision, artifact digest and remote base immediately before writing; check the base again before creating the PR. Create changed blobs, one tree preserving all other base entries and one commit with the captured base as parent. Create the branch without force-updating an existing ref. An existing branch must match the expected proposal commit/tree; otherwise report a collision and leave it alone. Create the draft with explicit repository/base/head/title/body using a body file; disable interactive prompts and implicit fork/push behavior.

A request may fail after GitHub accepted a write. On explicit retry or restart recovery, query the deterministic branch and matching PR before advancing. Reuse only verified matching remote state; an existing closed/merged PR remains an existing publication and is not recreated automatically. If identity cannot be established, record the uncertain state and offer **Reconcile**, not a blind repeat. Do not reset interrupted publication to an ordinary fresh request.

Checking the remote base cannot freeze it while other developers work. If it advances before a detected checkpoint, stop and record any already-created remote artifacts. If it advances after the final check, the PR retains the captured base evidence and requires normal GitHub review; this is not an atomic lock on the target branch.

## Controller and application interfaces

Keep GitHub commands in a bounded trusted controller adapter, separate from repository/test commands. Use fixed argv, `--hostname github.com` where applicable, explicit repository names, bounded response sizes/timeouts, no shell interpolation and sanitized errors. Use the existing CLI credential store; do not inherit model secrets, automatic endpoint overrides or token environment fallbacks. Read-only setup/preflight commands cannot broaden OAuth permissions or initiate login.

A publication service owns durable proposals and integrates with the existing local service/executor lifecycle. Local browser guards protect setup, prepare, publish and reconcile endpoints. Target edits use optimistic revisions; a late prepare response cannot install a proposal for a newer target. CLI publication uses the same service and explicit target selection rather than another implementation. Job/report APIs expose only safe publication metadata.

## Acceptance and controlled remote test

Offline regressions cover multi-file atomic tree construction, changed patch/digest, allowed-file checks, protected files, offline revalidation failure, wrong/stale base, target-edit races, duplicate requests and process loss before/after each remote effect. Mock gh subprocesses exercise noninteractive argv, bounded execution, safe error handling, stripped model credentials and reconciliation after ambiguous network failures. Normal tests never publish or infer.

Browser desktop/mobile acceptance covers target setup, read-only preview, publishing, duplicates, stale/error states and the durable PR link. Publication must not change the source checkout or hide a previously validated local patch when GitHub is unavailable.

The real controlled test seeds only a small synthetic shipping fixture and its fixed tests/contracts on `main` in the user-selected empty repository. Clone that fixture outside ProjectSeven, create a deterministic offline two-file repair, validate it, preview it, and explicitly publish one draft PR through the finished app. Confirm both changed files, draft status, expected base/head, retained evidence and repeated-action deduplication. Do not merge, close or delete the PR/branch, change repository settings/permissions, or make paid AI calls. Attach the created PR to this chat.

## Delivery and subsequent stages

After written-design approval, write a task-by-task implementation plan and retain the existing native Superpowers execution method. Implement, verify offline/browser/controlled remote behavior, request one fresh whole-change review, correct confirmed material findings and keep the managed branch/worktree. Documentation will distinguish mocked guarantees from observed remote outcomes and the unavoidable remote-base race.

Then proceed to deeper conservative impact analysis and easier project environment setup under their separate designs.
