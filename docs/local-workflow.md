# Local workflow

APIShield runs on demand. Developers can run it before upgrading a provider API, or invoke it from a CI job. It does not require a continuously running laptop process. Hosted scheduling and GitHub publication are later phases.

Install into a Python 3.11+ environment with `python -m pip install .`. The console command is `apishield`; `python -m apishield` has the same interface. Contract comparison also requires the native `oasdiff` executable described in the root README. Put it on PATH or set `OASDIFF_BIN` to its absolute path.

An integration JSON file identifies the exact Git repository root, committed ref, source directories, two JSON OpenAPI files, commands and budgets. Relative paths resolve from the configuration file. Start with `examples/shipping/integration.json`. Commands are argument arrays rather than shell strings. Run APIShield using the environment containing your integration's test dependencies.

```text
apishield scan --config /path/to/integration.json
apishield compare --config /path/to/integration.json
apishield repair --config /path/to/integration.json
apishield report JOB_ID
apishield cancel JOB_ID
```

For a reproducible offline proposal, add `--candidate /path/to/candidate.json` to repair. This never falls back to inference. Live generation requires an explicitly exported `GEMINI_API_KEY`; the CLI does not read the integration's `.env`. The local engine defaults to `gemini-3.8-flash`; an explicit integration `model` is preserved. Temporary provider failures consume the existing finite attempt budget; persistent failures remain failed. Live responses use a typed patch/diagnostic contract. See [initial live assessment](live-ai-quality-2026-10-12.md) for measured results and provider-availability limits. Offline tests alone do not establish model repair quality.

Each command creates a job under `~/.apishield/jobs` by default. Override with `--jobs-dir /path/to/jobs` consistently for execution, report and cancel. This directory must be outside the source repository. Jobs retain configuration, commit and contract hashes, events, command evidence and a final JSON result; their disposable source workspace is removed when execution ends. A validated job also retains `candidate.patch`.

Only committed source at the pinned ref is analyzed. Dirty or untracked changes are excluded and reported. Commit intended changes before running. Secret files, symlinks and embedded repositories are excluded or rejected. Source analysis currently recognizes direct `requests`/`httpx` calls with resolvable URLs; wrapper clients and dynamic URLs yield coverage limitations. A successful test run supports the configured behavior checks, not universal semantic correctness or a research novelty claim.

Review a validated patch before applying it:

```text
git apply --check /path/to/jobs/JOB_ID/candidate.patch
git apply /path/to/jobs/JOB_ID/candidate.patch
```

Statuses distinguish `completed` scan/comparison, `validated` repair, `no_change`, `needs_input`, `failed` and `cancelled`. Exit codes are 0 for success, 1 for failure, 2 for missing input/configuration errors and 130 for cancellation. A repair without configured tests cannot be labeled validated. Candidate edits cannot target tests, contracts or files outside configured source paths.

Configured setup and test commands execute trusted repository code on the host. A disposable copy is not a security sandbox. Commands receive a minimal environment plus explicitly configured non-secret values; controller model and GitHub credentials are not forwarded. Default budgets are three attempts, 120 seconds per command, 600 seconds per job and 64 KiB captured command output.

Install dependencies in an external environment. Setup and test commands cannot add or change repository files, including test hooks and configuration; ordinary Python/pytest caches are excluded from integrity checks. The `python` and `python3` command aliases use the interpreter running APIShield, so that environment should contain your test dependencies.

## Dashboard API

Set `APISHIELD_INTEGRATIONS` to a JSON object mapping trusted integration names to absolute configuration paths, and optionally set `APISHIELD_JOBS_DIR`. Then run the existing dashboard server. Only the server's allowlist can choose repositories and commands; request bodies cannot provide them.

```text
GET  /api/integrations
POST /api/jobs                  {"integration":"shipping","operation":"scan"}
GET  /api/jobs
GET  /api/jobs/JOB_ID
POST /api/jobs/JOB_ID/cancel
GET  /api/jobs/JOB_ID/patch
```

Jobs execute in the background using the same engine as the CLI. Reports survive server restart. Shutdown requests cancellation; jobs left by a dead dashboard process are marked interrupted when a new service starts. These local endpoints have no tenant authentication and should be bound to loopback. The default browser workspace supports onboarding, job/patch review and explicit business requirements; the Phase 1 demo remains separate under `/demo`.

Integration config version 1 also supports optional `requirements`. See [requirements usage](requirements-workflow.md) for the declaration schema, selected pytest checks, snapshot evidence and local browser API. Existing configurations without rules retain their ordinary test-validation behavior.
