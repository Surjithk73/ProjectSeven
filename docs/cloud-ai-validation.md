# Cloud AI delivery validation — 13 October 2026

This is bounded engineering acceptance, not the deferred research evaluation. The supplied service account used project `gen-lang-client-0604700095`, global Google Cloud, Gemini `gemini-3.8-flash` and google-genai 2.22.0. No key fallback, model substitution or Cloud account changes occurred.

## Browser connection and workflow

The actual Settings flow configured the supplied JSON without inference. **Test connection** succeeded: `APIShield connection works`, 6.16 seconds, 10 input/6 output/16 total tokens. This verifies application access separately from repair quality. Only one paid application test ran.

Malformed JSON/type rejection, Clear, reconfiguration, safe project/model summary, cleared file input and configured-versus-tested states were exercised. Desktop (1440 px) and mobile (390 px) layouts were inspected. An isolated port 8003 fixture replaced `model_client` with a non-network mock; its browser repair queued and cancelled with final job `86d4412b…` cancelled, while tracked source stayed unchanged. The fixture never called Google.

## Live repair acceptance

One repeat of six existing scenarios used the production engine, at most two attempts per case and a hard 12-call ceiling. Generation output was capped at 4096 tokens/call; SDK content retries were disabled. Eight generation calls ran; no success was rerun and no failed case received extra attempts.

| Case | Engine result | Calls | Independent behavior | Original source |
|---|---|---:|---|---|
| Endpoint move | Validated | 1 | Passed | Unchanged |
| Payload nesting | Validated after first HTTP 504 | 2 | Passed | Unchanged |
| Response nesting | Validated | 1 | Passed | Unchanged |
| Exact money units | Failed: two HTTP 504 responses | 2 | Not reached | Unchanged |
| Refund semantics | Validated | 1 | Passed | Unchanged |
| Missing billing address | Needs input | 1 | Explicit diagnostic; no invented address/patch | Unchanged |

The four validated repairs passed configured tests and held-out checks, including actual API invocation and returned response behavior. The missing-address diagnostic was explicitly reviewed: the API requires street/city/postal code but the function does not receive them and intent forbids defaults. This run does not establish correct money-unit repair. After review, the runner now marks generated abstentions as awaiting explicit diagnostic review (`accepted: null`); unrelated preflight results with no model call are not accepted. The old retained result remains unchanged, and its actual address diagnostic was reviewed directly.

Five generation responses reported 4,553 input, 409 candidate-output and 2,835 thinking tokens: **7,797 total**. Three HTTP 504 calls reported no usage; their possible billing is unknown. Including the browser test, observed reported usage is **7,813 tokens** across nine requests. These counts are not a billing receipt.

Evidence is outside Git at `C:/Users/surji/.apishield/live-cloud-2026-10-13-delivery`: results, per-call synthetic prompts/configs/responses/usage, jobs, patches and held-out outputs. The batch process started at `ab38949`; its final result records repository HEAD `7f4403e`, which advanced during the run, alongside production and harness hashes. Credential JSON, OAuth assertions/tokens and authentication headers are excluded. That transport-only correction applies the deadline explicitly to TLS and writes; the running process retained its previously imported transport. Offline regressions cover the final transport; live inference was not repeated for it or the subsequent review fixes.

## Offline verification and limits

Connection tests cover invalid credentials/destinations, explicit provider overrides, no ADC, authentication budget/cancellation, slow protocol framing, response limits, redirects and closure. Session/API tests cover private job capture, replacement/Clear, restart reset, local guards, streaming caps, stale tests and stripped subprocess environments. CLI/harness tests cover explicit flags, safe failure records, restored instrumentation and refusal of a thirteenth content call. Normal tests never call Google.

Final verification: **360 Python tests passed, 1 platform skip, 1 existing dependency warning**; **22 frontend tests passed**, production build passed, and lint reported only six existing warnings. `git diff --check` passed. An earlier full run hit an existing 150 ms Git fixture-preparation timing failure under concurrent load; the unchanged test passed in isolation and the quiet full suites passed.

One fresh independent reviewer identified OAuth internal backoff outside the deadline and overly broad abstention acceptance. Both were reproduced with failing offline tests, corrected in one fix pass, and followed by the green full suite above. OAuth non-200 responses now raise a safe nonretryable authentication error before library backoff; engine-owned attempt budgets remain unchanged. The runner now requires explicit diagnostic review for generated abstentions. Provenance wording was corrected to distinguish process-start commit from the later recorded HEAD. No second review or extra paid inference was performed.

These synthetic repairs require human review; the small run does not establish production reliability or semantic completeness. Google service failures remain material. GitHub drafts, deeper analysis and easier environment setup are subsequent stages.
