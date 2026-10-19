# Live repair assessment

This opt-in runner uses the production engine with synthetic Python integrations. It retains raw model calls, proposals and independent verification evidence outside the source repository. Normal pytest does not make paid model requests.

To prepare fixtures and check broken baselines without inference:

```powershell
python -B -m research.live_quality --output C:/Temp/apishield-quality-new
```

To run a deliberately bounded paid assessment, export `GEMINI_API_KEY` in the controller environment and explicitly add `--live`:

```powershell
python -B -m research.live_quality --live --model gemini-3.8-flash --repeats 1 --cases endpoint money_units --output C:/Temp/apishield-quality-live-new
```

Output must be a new directory outside Git repositories. There are at most two model requests per case/repetition; six cases are available and repeats are limited to three. Provider retries consume that same budget. No silent model fallback or dotenv loading occurs. Child commands receive a minimal environment without controller model credentials.

Configured tests gate engine validation. Held-out checks then verify retained patches in separate clones, including exact request counts, paths, data and varying server replies. The missing-address case should return a diagnostic rather than invent data. A successful test is evidence for this fixture, not proof of arbitrary business correctness.

See [the October 12 assessment](../docs/live-ai-quality-2026-10-12.md) for actual results, limitations, protocol changes and retained artifact locations. Compare cohorts only with their model, code hashes, generation configuration and time in view; the first assessment was exploratory rather than a preregistered controlled benchmark.
