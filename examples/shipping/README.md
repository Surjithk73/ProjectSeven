# Shipping example

This small integration creates a shipping label while preserving package identity and integer gram weight. V1 posts to `/labels`; V2 requires `/labels/create`. Its test checks the upgraded endpoint and unchanged payload, using a mocked HTTP transport.

Copy this directory outside the APIShield checkout and initialize it as its own Git repository. From that copied directory:

```text
git init
git add src tests
git commit -m "Shipping integration V1"
python -m pip install httpx pytest
apishield scan --config integration.json
apishield compare --config integration.json
apishield repair --config integration.json --candidate candidate.json
```

Install APIShield first following the root README, and make native `oasdiff` available. Git must have your usual commit identity configured. The example's contracts and candidate are external inputs; only `src` and `tests` need to be committed. The deliberately old source fails the V2 expectation until the proposed endpoint edit is tested in the disposable job.

The offline candidate changes only the endpoint. APIShield runs the test in an isolated copy and keeps a patch on success. It does not alter this example's original source. Use the job ID printed in the result with `apishield report JOB_ID`, then review and apply the retained patch as described in `docs/local-workflow.md`.
