# Google Cloud AI setup and repair acceptance

Status: implemented and verified, including independent review corrections. See `docs/cloud-ai-validation.md` for actual outcomes and limits.

## Purpose and current evidence

The user has resumed AI setup/testing and asked to complete GitHub draft PRs, deeper supported impact analysis and easier project setup. This first subsystem lets the existing local app use the supplied Google Cloud service-account JSON for Gemini 3.8 Flash, then verifies actual repair quality through the existing guarded engine. GitHub publication, analysis expansion and test environments follow as separate subsystems; this design does not drop them from the requested scope.

The credential-only preflight already succeeded: project `gen-lang-client-0604700095`, model `gemini-3.8-flash`, global Google Cloud GenerateContent endpoint, HTTP 200, response `APIShield connection works`, 2.2 seconds and 16 total tokens. This proves generation access, not correct repairs or application integration. The previously supplied API keys failed separately; do not reuse them or describe them as fixed.

Keep the no-authentication local browser experience and existing worktree. Research evaluation, patent work, hosting and early trials remain deferred. No Cloud billing, roles, API permissions, or GitHub remote contents change in this subsystem.

## Approach

**Recommended: extend the existing Google SDK adapter with an explicit Cloud connection.** The installed SDK already accepts credentials/project/location and supports the existing typed candidate schema, bounded retry settings and response metadata. Reuse it, the repair engine and the synthetic acceptance runner; add a focused connection module and browser settings rather than another repair engine.

The alternative is a separate raw REST generator using the successful preflight. It would duplicate schema/response handling and instrumentation that the SDK already provides. Do not introduce a provider framework, database or hosted credential service for one additional Google route.

## Local setup experience

In the existing Settings view, choose **Google Cloud service account** or the existing **Gemini Developer API** mode. Switching providers is explicit; ambient SDK flags or key format cannot silently select a different endpoint.

For Cloud, select the JSON file from this computer. The browser sends it only to the guarded local application endpoint. Show the project, global location, `gemini-3.8-flash` default and a **Test connection** action. Never render private keys, access tokens or the full JSON after submission. A successful connection test shows the actual model response/status and safe usage/latency; authentication, permissions, billing, model access and transient errors show distinct recovery messages.

Keep credentials in controller memory for the app session. Do not copy the file into the source repository, job storage, registry, patch, GitHub branch or logs. Restart requires selecting credentials again. **Clear connection** removes the session selection for future requests; it does not revoke the Cloud credential. Existing job cancellation remains the way to stop an active repair.

Retain the current Developer API key workflow, with explicit provider selection and no automatic fallback. Existing model choices in integration configurations remain explicit; the selected/default model for this Cloud delivery and all live acceptance calls is Gemini 3.8 Flash. Unsupported model access fails visibly rather than substituting another model.

The browser's model-ready indication, Generate AI repair control, monitoring's explicit Request repair action and CLI/live runner must use the same connection readiness logic. Updating a setting cannot silently switch an already-created repair to a different provider midway through retries. Historical job evidence records safe provider/project/location/model metadata, without credentials.

## Credential and request boundary

Accept only a service-account object with the required project/client-email/private-key fields, a supported HTTPS Google OAuth token endpoint and a bounded JSON size of 64 KiB. Treat every other file field as data, never instructions. Validate project identifiers and credential structure before any outbound request. No user-supplied arbitrary OAuth URL, delegated subject, custom token audience, proxy destination or API base URL is supported.

The controller performs authentication and generation. OAuth refresh and model calls share the request's remaining deadline; a credential refresh cannot extend the engine's overall job budget. Disable ambient proxies for both transports and SDK internal content retries; the engine's finite retry budget remains authoritative. Keep the typed `patches`/diagnostic-string `needs_input` contract and existing untrusted-source instructions.

Only safe configuration metadata goes into the job context/evidence. Private credential objects remain separate from source/contracts/prompts. Repository setup, pytest, Git snapshot commands and independent validation subprocesses continue receiving the existing stripped environment. Neither credential JSON nor its path is added to integration files or subprocess settings. Trusted repository commands still run locally; this is not an OS sandbox or a hosted secret-isolation claim.

Provider failures must not serialize tokens, signed assertions or private-key material. Model error records preserve safe status/reason and recovery advice. Clear session fields after failed setup and test that malformed credential submissions do not echo their input in validation errors. Replacing/clearing a connection must not corrupt a running job's retained evidence.

## Actual repair testing

Extend the existing opt-in synthetic acceptance runner to use the same explicit Cloud connection as the app. Keep held-out behavioral checks outside the source repository and out of generator prompts/retry feedback. Do not modify tests to make a model proposal pass.

First run offline regressions and the browser connection test. Then run one live pass covering six existing synthetic behaviors: endpoint migration, nested request payloads, nested response extraction, exact numeric units/values, refund semantics and missing-required-information abstention. Use one repeat and at most two attempts per case: **maximum 12 generation calls** for this acceptance batch, plus at most one tiny application connection check. Maximum output is 4096 tokens per generation call. Stop instead of silently rerunning successes or expanding the batch.

Retain source hashes, engine/model metadata, call counts, safe usage/latency, actual statuses, test evidence, candidate patches and independent behavioral-check results. A case is accepted only when the original source is unchanged and either its validated patch passes held-out checks, or its missing-information case returns the expected diagnostic. A configured-test pass without held-out correctness is reported separately.

Transient service failures, incorrect candidates or missing information are legitimate outcomes to report. Fix actual implementation/fixture defects with focused regression checks, but do not lower the oracle, cherry-pick cases or call the product fully validated when cases remain unresolved. These are engineering acceptance results, not a formal research experiment or novelty claim.

## Offline and browser completion checks

- Both provider routes are explicit, with no environment-triggered fallback; no normal pytest test calls Google.
- Valid Cloud setup, malformed JSON/type/endpoint/key errors, clearing/replacing credentials, session restart and safe diagnostics work without credential echoes or persistence.
- Authentication/generation timeout, cancellation boundaries, temporary failures and finite retries retain truthful job states and provider metadata.
- Repository/test subprocess environments, prompts, serialized configs/reports and patches contain no controller credentials or credential path.
- The existing offline example, Developer API tests, requirement checks, immutable snapshots and monitoring workflows remain compatible.
- Real browser Settings setup/test/clear/error flows and explicit Cloud repair controls work at desktop/mobile widths without adding login.
- A bounded live run records all six selected outcomes, including failures, and verifies source integrity and independent behavior.

## Following delivery order

1. **This subsystem:** Cloud connection and actual repair acceptance.
2. **GitHub drafts:** use the existing CLI sign-in and user-selected `Surjithk73/APIGuardTesting`. It is still empty; the next design includes a synthetic `main` fixture base. Publish only validated source patches with evidence, stale-base protection and deduplication; no merge.
3. **Deeper supported impact analysis:** request/response field observations and conservative resolvable helper/caller links, with explicit unresolved coverage.
4. **Easier project setup:** external per-integration Python environments, controlled dependency preparation, progress/errors and the correct test interpreter, without changing original repositories.

Each subsequent subsystem uses the current shared engine and local browser workflow and receives its own written spec/implementation plan before implementation.
