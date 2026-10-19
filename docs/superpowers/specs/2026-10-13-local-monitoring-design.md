# Local contract monitoring

Status: written design and implementation plan approved; monitoring implemented and verified. See docs/local-monitoring-validation.md for tests, browser evidence and review corrections.

## Intent and boundaries

The user requested the remaining product capabilities, excluding research evaluation, patent work, hosting and early trials, and subsequently deferred AI integration/live testing. This first independent implementation makes the existing local browser app check approved OpenAPI sources periodically and expose relevant changes without manual contract uploads on every check.

Preserve the local, no-sign-in workflow and existing engine, requirement checks and original source integrity. Monitoring operates while the app/computer is running; it is not a hosted service. A timer creates scan/comparison evidence only. AI repairs and GitHub publication require explicit user actions initially, so enabling monitoring does not authorize recurring paid inference or automatic remote writes.

## Approaches

1. **Persisted local schedules inside the existing service — recommended.** Reuse job execution, registry storage and browser reporting. No external scheduler, database or service account is needed; clearly explain that the app must remain running.
2. **CI-only scheduled checks.** Useful later, but would require repository/workflow authorization and moves monitoring out of the current browser app.
3. **Hosted scheduler/workers.** Explicitly excluded by the user.

## Setup and baseline

Add a Monitoring section for the selected integration: source URL, check interval, explicit local/private-network-source opt-in, Enable/Pause, Check now and current state. Default interval is 60 minutes, with a minimum of 5 minutes for automatic schedules. A manual check can run immediately but cannot overlap another check of that integration.

The user chooses the initial baseline explicitly:

- **Use the saved current contract:** the uploaded base contract is the developer-declared compatible version. The first download is compared against it and can reveal a pre-existing change.
- **Start monitoring from the first download:** fetch and validate the remote contract, retain it as the initial baseline, and record initialization without inventing a change alert.

The UI explains the distinction. Never silently treat an initialization snapshot as a breaking change. Once established, do not advance the accepted baseline merely because a changed contract was fetched or a comparison completed. **Accept as baseline** explicitly promotes a retained snapshot; acceptance acknowledges monitoring state and does not claim code was repaired. Existing current/target contract uploads and prior jobs remain immutable.

Browser-connected integrations may configure monitoring. Server-managed integrations can be configured through trusted server configuration and are read-only in the browser. The shipping example can use a controlled local fixture server in acceptance tests; the shipped demonstration must not depend on a public API changing.

## Fetching

Use bounded HTTP fetching through the existing HTTP dependency: timeout 15 seconds, maximum 2 MiB response body and no ambient proxies, browser cookies or controller model/GitHub credentials. Require a JSON OpenAPI object and a nonempty versioned snapshot; YAML support is outside this increment.

URLs must use HTTPS by default, have no embedded user/password and not put secret-named credentials in query parameters. HTTP/private/local sources require an explicit trusted-local opt-in and clearly show the destination. Reject unspecified, multicast and link-local/metadata destinations even with that opt-in. Validate resolved destinations and redirects against the approved source policy; unsupported destination/pinning behavior must fail honestly rather than claim hardened hosted fetching. Do not fetch arbitrary additional URLs referenced inside downloaded contracts.

HTTP errors, unavailable DNS, timeouts, oversized responses and invalid contracts become monitor failures with recoverable diagnostics. Keep the last accepted baseline and previous successful observations. Apply capped retries only to subsequent scheduled/manual checks; do not create a hidden burst of HTTP retries.

## State and snapshot identity

Persist monitor configuration/state outside Git under the existing job root. Records contain integration identity, source configuration revision, enabled/paused state, interval, accepted baseline hash, last observation hash, next due time, last attempt/result and the associated job/change references. Retain immutable downloaded JSON snapshots with original and canonical-content hashes, fetch time and source URL with safe diagnostics.

Canonical JSON hashing ignores whitespace/object-key order, so formatting-only responses do not create change events. Do not erase semantic changes by sorting arrays or deleting fields. The change identity combines integration, accepted baseline hash and observed hash. Repeated observations reuse that change record; after explicit baseline acceptance, the new baseline establishes a new comparison identity.

Changed repository code may need a rescan even when the contract hash is unchanged. Keep source revision in job evidence and support explicit rescans; scheduling must not claim it analyzes dirty/uncommitted changes. Broader event-driven GitHub webhooks are outside this local increment.

## Scheduling and execution

Use one local scheduling loop owned by the existing service lifecycle and existing bounded job executor. Persist next-due times; serialize check ownership per integration and prevent Check now from racing a scheduled check. Fetch and execute commands outside registry/state locks, then publish results only if the source configuration revision is still current. A stale in-flight fetch must not overwrite a newly edited source or accepted baseline.

On startup, retain schedules and last evidence. Missed intervals coalesce into at most one due check per integration; no catch-up burst. Interrupted work is recorded and eligible for a later retry rather than silently resumed halfway. On shutdown, stop scheduling, request cancellation for owned jobs and preserve terminal diagnostics. Existing command/job deadlines and process cleanup remain authoritative.

An unchanged valid contract produces a successful observation without a repair job. A new semantic snapshot creates one comparison job through the shared engine using retained baseline/target contracts and a pinned source revision. Show changed operations, affected calls, requirement relationships and coverage limitations using existing reports. Irrelevant changes remain recorded and do not trigger AI repair or PR creation.

## Browser workflow

Preserve the current white/slate/violet migration review desk. Add a compact monitoring setup/status section and a Changes view or list within the selected integration. Show source, baseline, interval, last check, next check, state and recovery action before internal IDs/hashes.

States: not configured, initializing, scheduled, checking, paused and failed. Offer labeled URL/interval/baseline controls, explicit local-source opt-in, visible keyboard focus, loading/errors, retry and Pause. Long URLs wrap on mobile; failed initialization retains setup input. Monitor edits use optimistic configuration revisions, like the requirements editor, and do not change historical jobs.

Change records let users open comparison evidence, request a repair explicitly, and accept a fetched version as baseline with clear consequences. Draft PR publication will be a later adapter action on a validated job, never part of this timer.

## Offline completion checks

- Controlled HTTP fixtures demonstrate initialization, meaningful changes, formatting-only changes, no change, invalid JSON/OpenAPI, oversized bodies, timeouts, redirects and source-policy rejection.
- Repeated checks create one change/job for the same baseline/target, with original repository and old records unchanged.
- Manual/scheduled overlap, source edits during fetch, baseline acceptance during fetch, process loss, shutdown and restart retain coherent state without duplicate work or stale publication.
- Requirement-scoped comparison evidence is visible; no timer invokes candidate generation or GitHub publication.
- Real browser enable/pause/check-now/baseline-acceptance/error-recovery flows work at desktop/mobile sizes.
- Normal regression tests need no Gemini key, public changing contract, GitHub credential or paid model request.

## Next subsystem dependencies

Provider connection/live repair is deferred at the user's request. The user selected GitHub CLI and `Surjithk73/APIGuardTesting` for controlled draft-PR testing; that repository is empty, so its later subsystem design includes an initial synthetic fixture/base branch. Deeper supported field/caller analysis and per-integration environment setup follow as separate designs/implementations against this same engine. None of these dependencies blocks offline monitoring or turns it into a hosting or formal research project.
