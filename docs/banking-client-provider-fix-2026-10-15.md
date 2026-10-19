# Banking client/provider and AI repair fixes — 2026-10-15

The banking demo at `/banking` now separates the client application and API provider into keyboard-accessible tabs. The saved SwiftPay dashboard under `.project-backups/original-2026-10-14/swiftpay_frontend` informed the account and transaction composition. The backup was not modified. The client has actual adapter-backed balance reads, transfers and refunds, account panels, transaction history, loading/empty/error states and responsive layouts. An incompatible balance response shows unavailable balances rather than bypassing the client through the provider state endpoint. Provider controls, active OpenAPI operations and the migration guide live in the provider tab. The old supplied-repair instructions were removed.

Google transport previously selected only the first resolved IP address. A local probe observed an OAuth IPv6 TLS timeout while IPv4 succeeded; connectivity is intermittent, so that probe does not establish the sole cause of every historical timeout. The transport now attempts other validated addresses after TCP/TLS failures, with a five-second connection-attempt budget within the existing absolute deadline. It preserves hostname certificate verification, DNS address policy, response limits and redirect rejection. No HTTP request is replayed after it has been sent.

An additional live repair exposed rejection of AI-generated checks. The generator had explicitly suggested pytest monkeypatch even though the validator rejects setattr calls. Instructions now request unittest.mock.patch and state the forbidden operations. One regeneration with validation feedback is permitted within the original inference deadline. Rejected checks are never written or executed; validation restrictions remain unchanged. Redaction applies to both initial and regeneration context, and per-generation usage is retained.

## Verification

- Targeted backend suite: 40 passed (model transport, AI intent, browser repair flow and banking demo).
- Subsequent model transport/intent suite: 34 passed before the final redaction regression assertion; see final task output for the latest run.
- Frontend: 59 passed; production build passed; lint reported six incumbent warnings and no new errors.
- Impeccable mechanical detector: no findings on Banking.jsx and banking.css.
- Live Google service-account connection succeeded through the production transport.
- Isolated live AI repair: reports/banking-repair-verification-2026-10-15/53012bcc7d2845d7953e01c5d7d97205/result.json. Status validated, one repair attempt, three AI-inferred rules, three generated validation tests passed. The candidate was not applied to the user's working files.
- Executing that actual model candidate against BankingDemo V2 passed balance reads, a 1,234-cent transfer preserving destination, refund restoration and duplicate refund rejection.
- The running server was restarted with updated backend code; `/banking` and its built bundle returned HTTP 200. Existing demo had no transactions and its V2 provider setting was restored.

Fresh rendered desktop/mobile review remains unavailable under the existing browser-access restriction. Build and source checks do not establish visual approval. No publication archive or saved original version was changed.

## Repeatable startup (2026-10-15)

Both `start_demo.ps1` (via `start_demo.bat`) and `start_app.ps1` (via `start_app.bat`) now call `tools/reset_banking_demo.ps1` after launching the dashboard. The helper waits for readiness and invokes the existing local banking reset endpoint. This restores the registered demo's working `src/bankclient.py` from the shipped V1 fixture, V1 provider state, the accepted API baseline, $1,250 checking / $3,000 savings, and empty history. The existing transfer input remains $25. No fabricated balance is displayed when V2 is incompatible with V1 code; resetting restores a working initial client instead. Historical evidence and other repositories are retained.

The helper was exercised against the running app: provider V1, active contract 1.0.0, expected funded balances and successful client balance read were confirmed. Startup regression tests mock an initial readiness failure before successful reset; the reset endpoint regression covers changed working source, an accepted V2 baseline and repeated resets.

## Applied-repair graph refresh (2026-10-15)

Reopening an applied repair from history previously rendered that repair's pre-migration graph snapshot. The job response now includes a separately identified current graph report for applied repairs. The graph component receives that current report, including its job ID, source graph and community/AI metadata, so graph generation and inspection operate on the current source snapshot. Reviewed patch, original impact and validation evidence remain unchanged in retained records. A validated but unapplied proposal continues to show affected working code. Current graph generation retains ordinary change analysis, so this does not globally erase impact flags for subsequent breaking changes.

Verification: a regression first failed when the applied repair response lacked current graph evidence. It now checks affected nodes before Apply, updated source hash and `/refunds/create` after Apply, zero stale impact in the current graph, and retained original impact on disk. Three current-API integration tests passed. All 60 frontend tests passed; production build passed; lint retained six incumbent warnings. The running app was restarted with the updated backend and the new bundle served successfully; banking remained at V1 with no transactions.
