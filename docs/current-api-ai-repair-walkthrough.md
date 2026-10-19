# Current API workflow

Open http://127.0.0.1:8002. The managed app was restarted after this change and the banking provider was restored to V1.

1. Select banking-example in the sidebar.
2. Check for API Changes is always the primary dashboard action. With the provider on V1, its V1 documentation matches the accepted baseline: no changes and no affected calls.
3. API endpoints opens the current documented endpoints and consuming calls. Semantic graph opens the current repository graph. Working edits are included without a Git commit.
4. Open Banking demo and switch Provider API to V2. This changes the provider/documentation, not the client adapter or accepted baseline.
5. Return to APIShield and Check for API Changes. The check compares captured active documentation with the accepted contract and highlights affected code. Repeated checks do not silently accept V2.
6. Generate AI repair requests Gemini with source, API documents and the semantic graph. Gemini infers intent and generates separate missing checks. Existing repository tests are reused. Generated checks must fail on incompatible original code and actually pass after the proposed repair; skipped/empty/error-only execution does not validate a fix.
7. A validated repair exposes the dark Code changes view. Review, then Apply repair. Apply writes current working files and newly generated tests without a Git commit or branch change. Stale source/documents/configuration are refused.
8. Apply retains original bytes and a recovery manifest under `%USERPROFILE%/.apishield/jobs/<job-id>/local-backup` and `local-apply.json`. Interrupted prepared writes are reconciled on retry, with user edits/deletions protected. Do not remove these records until you no longer need recovery.
9. A successfully applied banking adapter becomes the actual demo client. APIShield accepts that captured V2 contract and opens a fresh current graph. Further V2/V2 checks show no new changes. Historical reports retain their original evidence and highlights.

Existing repos can use local/uploaded OpenAPI documentation, or a configured documentation URL under Monitoring. A static uploaded file is not a live provider feed; update that document or connect the URL. New setup requires current documentation; observed documentation is optional and initially defaults to unchanged.

## Current Cloud AI access

On 2026-10-14, the restarted application automatically loaded its privately managed service-account JSON. Its live `gemini-3.8-flash` connection test returned `APIShield connection works` in 5.24 seconds (10 input, 6 output tokens). A real banking current-overview request also completed automatic AI graph interpretation. This verifies connection and graph generation; it does not establish a new end-to-end repair acceptance result.

API endpoint browsing displays one current contract pane and consumed endpoints without comparison badges. Comparison reports retain before/after evidence. Normal graph groups use blue, teal, yellow, mint and purple; red is reserved for detected impact. Settings no longer accepts API keys. The managed JSON loads automatically after restart and remains outside the project/Git.

## Verified behavior

- Actual running HTTP app: V1 reports zero changed operations/affected calls; V2 reports four changed operations and three affected calls. Provider restored to V1 afterwards.
- Controlled automated model-response regression: V1 -> V2 -> validated patch -> uncommitted Apply -> functioning banking calls -> neutral current graph -> unchanged V2/V2.
- New focused backend suite: 18 tests passed after review fixes, including concurrent graph request deduplication/credential capture and interrupted Apply recovery.
- Broader existing backend selection: 144 passed, 1 skipped. Frontend: 58 passed; build and lint completed, with existing lint warnings.
- Fresh visual browser verification is unavailable under this session's browser restriction. Source/bundle/HTTP checks are not a rendered visual approval.

## Scope and limits

Automatic inference is labelled AI-generated, not manually confirmed business truth. Repository/test commands execute trusted code in bounded temporary workspaces with controller credentials excluded; this is not an operating-system sandbox. Generated tests cannot replace existing tests or hooks. Repair editing currently supports localized Python source; the static graph's bounded Python/JavaScript coverage and unresolved-call notes remain applicable. Model context is bounded to 128 KiB; graph interpretation is limited to 120 nodes. Research evaluation, patent framing and hosting remain deferred.
