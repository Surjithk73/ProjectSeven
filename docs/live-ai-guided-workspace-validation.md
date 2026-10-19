# Live AI acceptance in the guided workspace — 13 October 2026

This is a bounded product acceptance follow-up, not the deferred research evaluation. It tests the production engine and guided browser flow at repository commit `845bf3c`, using Google Cloud and `gemini-3.8-flash`. No model substitution, GitHub publication or original-source patch application occurred.

## Actual outcomes

| Check | Outcome |
| --- | --- |
| Browser connection test | Passed in 5 seconds; 16 reported tokens |
| Browser shipping endpoint repair | Validated on attempt 1; configured test and confirmed exact-weight business-rule test passed |
| Exact integer money repair | Validated on attempt 1; configured and independent held-out checks passed |

The browser configured the user's previously supplied service-account JSON in AI settings. Credentials remain in server memory. The browser comparison found the move from `/labels` to `/labels/create`; Generate AI repair called the real model and retained repair job `525ad09376bf47fc8f02215236416a54`. Its patch changed only the endpoint, retaining request data, error handling and returned response. The confirmed requirement test was collected and passed separately; an unconfirmed source-intent suggestion remained unconfirmed. Code change displayed the retained patch, and Tests & rules displayed the actual command evidence.

The shipping source hash before and after was `9D1CFD9C9DABA8D36FAF464ACCB0F133BC67EDA12B0E7454D8A68557EF6F82BC`. Existing untracked fixture files were excluded and reported; no cleanup or original-source edit was performed.

The exact-money follow-up used `research.live_quality --cases money_units --repeats 1` with explicit Cloud credentials and the production engine. Job `34f75d73b7e84bc59d407da8cafeb9b3` completed in 6.53 seconds with one generation call. Its independent checks included one cent, Unicode identity and the exact integer `9007199254740993`, while checking the request destination, payload, invocation count and returned response. Source remained unchanged. That call reported 976 input, 95 candidate and 423 thinking tokens, 1,494 total.

These were three new model requests: one connection test and two repair generations. No provider errors or additional attempts occurred. The browser repair does not retain token usage in its public job report, so no combined token total or billing claim is made.

## Evidence and limits

Money-case results, call record, patch, held-out output and a safe browser-acceptance summary are retained outside Git at `C:/Users/surji/.apishield/live-cloud-2026-10-13-guided-money`. Browser evidence remains in the normal application job store; ignored screenshots are under `.impeccable/review/live-ai/`. Credential contents were not printed or copied to evidence.

The earlier [Cloud validation](cloud-ai-validation.md) recorded success on endpoint, payload nesting, response nesting and refund cases, plus an explicit missing-address diagnostic. Its money case failed on provider timeouts; this follow-up supplies a successful money-case result without rewriting the old evidence. This small synthetic set does not prove reliable repairs across arbitrary applications. Deeper semantic analysis remains pending.

To use AI now: connect your committed Python project and JSON OpenAPI contracts, choose **Check API changes**, then **Generate AI repair** when supported calls are affected. Review **Code change** and **Tests & rules** before downloading/applying a patch or publishing a draft. Restarting the server requires reselecting the credential file in AI settings.
