# Initial live AI repair assessment — 12 October 2026

This is an exploratory assessment of actual Gemini-generated repairs through the production local engine. No supplied candidate patches were used for the live runs. Only synthetic source/contracts were sent to Google; no customer repositories, credentials or real payment transactions were included.

## Outcomes

Across four explicitly separate matrix/follow-up batches: **20 jobs, 28 model requests, nine validated repair patches, ten terminal provider failures and one response-format failure**. All nine generated repair patches passed strengthened held-out checks. All 14 fixture repositories retained unchanged tracked source and tests. These counts are observations, not a population accuracy estimate.

| Batch | Model | Jobs / requests | Accepted outcomes | Other outcomes |
| --- | --- | --- | --- | --- |
| Initial matrix, six cases × two repeats | gemini-3.8-flash | 12 / 12 | 7 verified repairs | 5 provider 503 failures |
| Bounded retry follow-up, four prior outage categories | gemini-3.8-flash | 4 / 8 | 0 | 4 jobs exhausted two requests with 503 |
| Explicit model comparison, money and missing address | gemini-3.5-flash | 2 / 4 | 1 verified money repair | Missing-address job returned a boolean needs_input after a 503; rejected as malformed |
| Typed response follow-up, same two categories | gemini-3.5-flash | 2 / 4 | 1 verified money repair | Missing-address job exhausted both requests with 503 |

The initial positive categories were endpoint migration, nested request payloads, nested response extraction, exact integer cents and refund endpoint semantics. Held-out inputs included a Unicode identifier, one cent and integers beyond binary float's exact range. Refund tests require the refund endpoint rather than the added charge endpoint. Each sample requires exactly one transport call, exact request data and propagation of a varying server response; balance replies are independent of the unused input value.

**Missing-address abstention is not yet verified live after the format correction.** In the one returned output for that category, the model emitted `{"needs_input":true}` without a diagnostic. The engine correctly refused to validate a patch. Later typed-response attempts were blocked by provider failures, so they do not establish a successful abstention. There were no observed generated invoice-address patches to accept or reject.

Two additional CLI preflight jobs preceded the matrix: the original gemini-2.5-flash configuration received 404 for this API project; an explicit gemini-3.8-flash shipping run validated on its first attempt (`3b51f22437a2411c9fe973127ded04a0`). These two requests are outside the 28-request matrix count and had no usage instrumentation.

## Issues found and corrections

1. **Unavailable default for this project.** Listing a model did not guarantee generation access: 2.5 Flash appeared in the model list but actual inference failed. The local integration default is now 3.8 Flash; explicit user selections are preserved. Google documents restricted 2.5 access for newer projects and recommends newer models. [Google model availability guidance](https://ai.google.dev/gemini-api/docs/deprecations/).
2. **Temporary failures bypassed the repair budget.** SDK 429/5xx exceptions previously terminated a job after its first request. Retryable codes now use the existing finite attempt budget, with a pause bounded by one second and remaining job time. SDK request retries remain one; there is no hidden multiplied budget. Real 3.5 money runs recovered from a first-request 503 and passed both configured and held-out tests on the second request. Persistent overload still fails honestly.
3. **Ambiguous abstention output format.** JSON mode alone permitted a boolean needs_input. The generator now supplies a typed response schema and explicitly asks for a nonempty diagnostic string or patch objects with all three required string fields. Engine checks remain strict. The schema was accepted in a real money repair; a live missing-data diagnostic remains unverified because of the later outage.
4. **Weak assessment oracle.** Independent review demonstrated that the original checks could accept a function that returned a hardcoded answer without making an HTTP call. Response values were also too predictable. Regression tests now reject both bypasses, and all seven original saved patches were re-audited offline with exactly-one-call and varying-response checks; all passed. No paid re-generation was needed for that audit.

## Protocol and evidence

The opt-in runner is `research/live_quality.py`. It creates new external fixture repositories, pins Git commits, validates a proposal with configured tests, applies its retained patch to a separate clone and runs held-out checks there. Hidden checks/inputs are outside the source repository and never enter prompts or retry feedback; captured requests were audited for the held-out identifiers and large values. Public test feedback is available to the normal repair loop. Each baseline failed before repair. Invalid evidence paths inside Git repositories are rejected before writes.

Model parameters: temperature 0, google-genai 2.22.0, explicit API key, non-Vertex/non-enterprise mode, ambient proxies disabled, max_attempts 2, command timeout 60 seconds, total job timeout 240 seconds and model request timeout at most 60 seconds. No silent model fallback occurred. Batches use different models/protocol revisions and times; they cannot establish model superiority or a causal improvement rate.

Initial generation/engine code came from `e8de532`; later cohorts used the explicitly documented retry and typed-contract working changes. Later results store dirty-state status, production source hashes, harness hash, call references, actual returned model version, raw synthetic prompts/responses, generation configuration and SDK token usage. The initial batch predates those extra provenance fields; its raw calls, fixture commits/contracts and original public tests remain retained. The oracle strengthening was post-hoc and is disclosed rather than presented as a preregistered benchmark.

Local evidence directories under `C:/Users/surji/AppData/Local/Temp/`:

- `apishield-live-quality-20261012-v1`: results.json, raw calls, jobs, patches, verification clones and strengthened_audit.json.
- `apishield-live-quality-20261012-v2`: retry follow-up, including both failed calls per job.
- `apishield-live-quality-20261012-model-comparison`: money recovery and rejected boolean diagnostic.
- `apishield-live-quality-20261012-typed-response`: accepted schema/money repair and remaining service failures.

Reported token totals for returned responses in these batches: **7,377 prompt, 896 candidate output and 7,640 thinking tokens**. Failed requests supplied no usage, and preflights were unmetered; these are partial usage observations, not a billing statement. The assessment does not estimate charges.

## Regression verification and limits

New regressions cover default/explicit model selection, 429/503 recovery and finite exhaustion, typed response configuration, no-request/ignored-response oracle bypasses and external evidence paths. Harness subprocesses also use the engine's minimal environment so Git/verification processes do not inherit model credentials; a regression demonstrated and then rejected inherited credentials. Each defect was observed failing before its correction.

Final full offline verification: `python -B -m pytest -q` — **215 passed, 1 POSIX-only skip, 1 dependency deprecation warning**, 125.56 seconds. The six harness regressions passed separately. A final non-live endpoint run prepared its external fixture and confirmed the broken baseline without inference. The browser frontend was rebuilt and the local app restarted with the corrected engine.

The small hand-authored fixtures test a supported direct Python subset with mocked provider transport. No unsafe validated patch was observed, but this is not proof of universal semantic preservation, coverage or production readiness. Gemini availability was poor during this session: 18 of the 28 measured requests returned 503. More synthetic/real migrations, repeated controlled runs, baseline/ablation comparisons and successful live missing-information cases are still needed for research conclusions. No literature novelty or patentability claim follows from these results.
