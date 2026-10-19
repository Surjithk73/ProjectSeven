# APIShield: two-machine, multi-provider movie-booking demo

Status: proposed design for user review; application implementation has not started.

## Agreed outcome

Two Windows computers on the same Wi-Fi/LAN demonstrate a genuine API migration. System A runs APIShield. System B runs a movie-booking client, a simulated theatre API, a simulated GPay-style payment API, and an update helper. There are no real payments and no official Google Pay integration.

The developer changes a provider from V1 to V2. The existing client visibly fails at the affected operation. APIShield fetches the changed OpenAPI document, identifies impacted client code, asks the configured AI connection to propose an update, validates it, and publishes a GitHub PR. A separate person reviews and merges it. System B automatically deploys that exact merged revision and demonstrates successful booking again.

Source repositories:

- `https://github.com/Surjithk73/ProjectSeven`: APIShield, existing examples, documentation, and demo tooling.
- `https://github.com/Surjithk73/APIGuardTesting`: the independently deployed movie-booking client and its public tests/CI.

Keep the existing APIGuardTesting history and shipping fixture. Introduce the client under `movie_booking/` on a normal branch; do not replace history or force-push. Keep existing banking functionality available as an example, with movie booking becoming the primary demonstration.

## Operating modes

Monitoring enabled and automation mode are separate settings. Manual mode is the default.

| Stage | Manual mode | Automatic edit mode |
|---|---|---|
| Periodic contract fetching | Runs when monitoring is enabled | Runs when monitoring is enabled |
| Compare and display changes | Automatic after a changed contract is fetched | Automatic after a changed contract is fetched |
| Generate and validate AI update | User selects Ask AI to Update | Starts automatically for a new actionable change |
| Publish validated PR | User previews and publishes | Publishes automatically after validation |
| Review and merge | Human | Human |
| Deploy merged client | Automatic on System B | Automatic on System B |

Automatic mode never merges a PR. It requires an explicitly configured target repository, enabled providers, a working AI connection, and a working GitHub publishing identity before activation. Turning it off stops new automatic dispatches; cancellation of an already running job remains explicit. No repeated paid generation on every polling tick: a failed job requires Retry, or a genuinely new contract/source revision.

## Network and process boundaries

| System | Service | Proposed port | Access |
|---|---|---|---|
| A | APIShield UI/backend | 8002 | Loopback browser, as today |
| B | Movie-booking client | 8100 | B browser; A may read health only |
| B | Theatre provider | 8101 | Explicitly configured LAN address |
| B | Payment provider | 8102 | Explicitly configured LAN address |
| B | Deployment helper | No inbound port | Outbound GitHub polling |

Ports are configurable. Setup checks availability and reports conflicts. Windows Firewall instructions restrict provider ports to the private LAN; do not silently change machine firewall policy. System A uses B's IPv4 address, not `127.0.0.1`, in provider URLs. No webhook tunnel or self-hosted GitHub Actions runner is required.

Keep APIShield's existing loopback origin/host/peer policy. Trusted LAN contract fetching is an explicit per-provider configuration, using the existing bounded fetcher and redirect/DNS protections. Credentials remain outside repositories and candidate workspaces. The client process uses real HTTP against independent provider processes; no in-process MockTransport is used in the live demonstration.

## Movie-booking experience and controlled breaks

Use the working name **CinemaFlow**. The client has movie/showtime browsing, theatre and seat selection, a booking summary with total, a simulated payment action, and confirmation/history. Provider controls are separate tabs/pages, visibly marked Theatre provider and Payment provider, with independent V1/V2 switches. Show active provider versions and client deployment revision.

Use SQLite for provider state; retain it across client deployments. Keep API contracts versioned and return the currently active contract at `/openapi.json`. Provider admin switches are loopback-only on B; A only needs their read APIs/contracts. No prewritten V2 client adapter, known replacement patch, or fallback compatibility translation may silently hide a break.

First supported scenarios:

1. Payment V2 changes the create-payment body from a scalar minor-unit amount to a nested money object and changes the confirmation response shape. Currency remains INR and the integer amount must remain in paise, without multiplication or division during migration.
2. Theatre V2 changes seat availability/hold response nesting and the booking-confirmation request shape. Showtime, theatre, seat, and hold identities must remain intact.
3. Both providers change while a PR is in flight. Retain both events; serialize updates for the client repository. Revalidate remaining work against the latest merged/deployed client revision before generating the next PR.

Tests cover exact monetary amounts, payment idempotency, seat uniqueness, expired holds, declined payments, and the rule that a booking cannot be confirmed without successful payment. Demo admin resets affect only the dedicated demo state and require a deliberate Reset action. Starting services does not reset a provider switched to V2 during a rehearsal. A separate Reset rehearsal command explicitly restores V1 state and a known client baseline; remote Git history is never rewritten.

## Multi-provider data and graph model

Add a project record for the client repository with provider children. Each provider retains its own contract URL, accepted snapshot, observed snapshot, poll interval, error state, and history. Existing single-provider integrations migrate into a project with one child without losing IDs or evidence.

Graph/API identity includes `provider_id`, HTTP method, and normalized path; match calls using the configured origin plus path prefix. Identical paths on different hosts must remain distinct. Unresolved/dynamic calls are marked unresolved rather than assigned to a guessed provider. Show one combined client graph with provider filters and a per-provider endpoint inventory.

Retain detection history separately from the current deployed graph. A proposed or locally passing patch does not make the live client healthy. After verified deployment, rebuild the current graph using the deployed commit and accepted provider snapshots. Remove resolved impact highlights there; historical comparison graphs continue to show their original evidence. Keep other providers' unresolved changes highlighted.

## Workflow state and deployment

Durable states: `observed`, `analyzing`, `awaiting_request`, `generating`, `validating`, `awaiting_publication`, `pr_open`, `merged`, `deploying`, `verified`, `failed`, `superseded`. Retain phase, timestamps, provider versions, source/patch/merge/deployed SHAs, validation evidence, PR URL, and actionable failures. Derive UI labels from evidence; do not show fixed/healthy after detection alone.

Use the existing temporary-workspace repair engine, AI-generated intent/checks, and guarded publication/reconciliation service. Add repository-level scheduling so jobs cannot overwrite one another. Deduplicate by project, provider contract hashes, source commit, and mode revision. Persist claims before side effects; reconcile after restart instead of creating duplicate PRs.

System B polls GitHub every 10 seconds for registered APIShield PRs merged into the configured `main` branch, using the repository API and proposal identity. Polling never deploys an unmerged PR or an arbitrary branch head. Require successful client CI for the exact merge revision before deployment. Associate merge SHA with the published proposal and its contract hashes, checking that live providers still match; if they changed again, report a stale candidate and require a new analysis.

Fetch the exact merged commit into a new release directory, build/install using the committed lockfiles, run preflight tests, then restart only the client. Keep the previous release for rollback. A health check plus an isolated booking smoke test verifies the new release. Use a dedicated smoke-test namespace so verification cannot book a user's seats or charge twice. Failure restores the previous client release and records deployment failure; it does not report the prior release as compatible with V2.

No inbound deployment callback is needed. The helper posts a commit status on the exact merge SHA (`apishield/deployment`) and a sanitized JSON receipt on the existing PR using its own local GitHub identity. APIShield polls that evidence and verifies proposal identity, SHA, contract hashes, and smoke result before accepting the new baseline. Evidence from another commit or deployment identity is rejected. The helper requires a configured allowed status/comment author; this is a trusted demo integration, not a cryptographically attested deployment service.

## User interface scope

- Project overview: CinemaFlow integration snapshot, both provider cards, real monitoring state, manual/automatic edit mode, last check, provider versions, and Check now.
- Provider settings: contract URLs, explicit LAN-source permission, intervals (minimum 5 minutes), pause/resume, and connection diagnostics. Check now supports immediate rehearsal without shortening the scheduler's minimum interval.
- Agent activity: existing timeline extended through PR publication, human-review wait, merge, deployment, verification, or rollback; chronological bottom-following logs and readable failures.
- GitHub panel: real PR URL, current review/merge state, CI evidence, and deployed revision. No fake success or decorative automatic-check state.
- Endpoint/semantic views remain available before any migration and allow filtering by provider. Keep white backgrounds and the established professional blue theme.

## Setup inputs and release gates

Publisher account `Surjithk73` is already authenticated locally and has admin access to both repositories. Before the two-machine rehearsal, collect the reviewer's GitHub username/profile URL and confirm accepted collaborator access to APIGuardTesting; collect B's private IPv4 address and the deployment GitHub username if different. Authenticate locally using GitHub CLI's browser login, never by sending credentials in chat. Review credentials stay out of AI prompts.

Implementation completion requires offline tests, real cross-machine contract fetches, one successful live AI-generated PR, a human merge, automatic deployment of its exact SHA, and successful booking after both supported migrations. Record any rehearsal step not yet executed as unverified. The academic benchmark and manuscript are outside this feature's scope; this demo is not evidence that a research evaluation has run.
