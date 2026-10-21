# APIShield — local integration repair engine

For the current **CinemaFlow / IMAX / GPay** demonstration on another Windows laptop, use [the fresh-Windows setup guide](docs/demo/NEW-WINDOWS-LAPTOP.md). Clone the `feature/cinemaflow-multi-provider` branch for this version. The host runs all services; a phone or another laptop needs only its browser.

## Use the browser app

The current app is in `C:\Users\surji\ProjectSeven`. Double-click **start_app.bat** to build and open **http://127.0.0.1:8002**. No sign-in is required.

Choose a repository in the sidebar. **API endpoints** shows only currently consumed endpoints; **Semantic graph** explores the current code. **Check for API Changes** compares active documentation with the accepted contract. In **Banking demo**, switching the provider to V2 introduces the example changes. Repair generation uses AI; review a validated proposal, then choose **Apply repair** to update working files without a commit. Historical reports preserve their original evidence.

**Settings → AI connection** uses Google Cloud service-account JSON only. A managed private copy lives outside the project at `%USERPROFILE%/.apishield/credentials/service-account.json` and loads automatically after restart. **Test connection** makes a small live request; **Remove connection** deletes the managed copy, without revoking the Google account. API-key setup and environment-key fallback are removed. See [current workflow](docs/current-api-ai-repair-walkthrough.md) and [Cloud setup](docs/cloud-ai-setup.md).

The [initial live AI assessment](docs/live-ai-quality-2026-10-12.md) verified nine synthetic repairs with independent checks; provider outages blocked ten of twenty jobs. The subsequent [Cloud acceptance run](docs/cloud-ai-validation.md) independently verified four repairs and a reviewed missing-address diagnostic; the money-units case remained blocked by provider timeouts. Treat generated repairs as proposals for review.

The launcher requires Git, Python 3.11+, Node/npm and native oasdiff (see prerequisites). It uses the existing environment where available and installs declared dependencies when missing. The app binds to loopback and runs trusted local repository code. Hosted scheduling, accounts, GitHub App publication and research experiments remain later roadmap work. The legacy payment demonstration is available separately under `/demo` using its existing demo launcher.

See [browser validation](docs/browser-workflow-validation.md) for verified behavior and limits.

## Business requirements

For a browser-connected integration, use **Business requirements → Add rule**. Describe the behavior, enter the exact source file/function and link committed pytest references such as `tests/test_parcel.py::test_shipping_preserves_package_and_weight`. Save the draft, review it, then choose **Confirm rule**. Editing a definition or changing its repository/source/test context clears confirmation. Source intent from a selected scan is an unconfirmed suggestion you can review and adopt.

During a repair, APIShield discovers the selected tests before generation and runs their checks separately from ordinary configured validation. A relevant confirmed rule with no check, an unresolved affected scope, or an unavailable test needs input. Skips, empty checks, errors and failed checks cannot establish a passed requirement. The shipping example includes a confirmed identity/weight rule and works offline.

Run reports retain the exact rule set/hash, operation/source/test relationships and individual check evidence. Past runs are unchanged when you edit current rules. Passing linked tests supports those checks; it does not prove that their assertions fully express a written rule. See [requirements usage](docs/requirements-workflow.md) and [verification](docs/requirements-validation.md).

Phase 2 adds an installable CLI for a supplied Python Git repository: scan its API calls, compare two OpenAPI contracts, and test a repair in a disposable copy. Your original repository remains unchanged. Successful repairs produce a patch and a durable report for review. See [the local workflow](docs/local-workflow.md) and [the shipping example](examples/shipping/README.md).

The SwiftPay dashboard demonstration below remains available. Its original mutable repair controls are separate from the new isolated `/api/jobs` endpoints.

For the standalone CLI, install from this checkout into your Python 3.11+ environment:

```text
python -m pip install .
apishield --help
```

Install your integration's test dependencies in that environment as well. Comparison needs native `oasdiff`, described below.

APIShield compares versioned NexusPay contracts, maps changes to SwiftPay business workflows, and validates candidate client repairs. Phase 1 provides a local demonstration with offline tests. A complete reviewable multi-file GitHub PR flow belongs to Phase 4; hosted operation belongs to Phase 6.

## Prerequisites

- Python 3.11 and Node.js 22 (including npm).
- Git; Docker Desktop with its Linux engine for the optional Compose setup.
- Native `oasdiff` for live contract comparison outside Docker. The Docker image includes the official Linux v1.11.7 binary. Offline pytest needs no model key, live provider, or GitHub credentials. The demo-cycle integration tests use a real oasdiff binary; they skip when it is unavailable locally. CI installs the pinned Linux binary before running the suite.

From the repository root, create the environment and install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
cd frontend
npm ci
cd ..\swiftpay_frontend
npm ci
cd ..
```

On Linux/macOS, use `python3 -m venv venv` and `venv/bin/python` for the equivalent commands. Dependencies are pinned directly in requirements.txt and by each npm lockfile.

For native oasdiff, download the matching archive and checksum list from the [official v1.11.7 release](https://github.com/oasdiff/oasdiff/releases/tag/v1.11.7), verify its SHA-256 against that list, extract it, and set `OASDIFF_BIN` to the executable's absolute path or put `oasdiff` on PATH. A Windows executable cannot run in a Linux container. The Python Dockerfile copies `/usr/bin/oasdiff` from the official `tufin/oasdiff:v1.11.7` image pinned to its registry digest; its path is documented in the [upstream Dockerfile](https://github.com/oasdiff/oasdiff/blob/v1.11.7/Dockerfile).

## Run locally

On Windows run `start_demo.bat`. It invokes start_demo.ps1, checks dependencies and ports, restores V1 source and its graph offline, and starts background services with logs in `.demo-logs`. An existing environment can be reused explicitly:

```powershell
.\start_demo.ps1 -Python C:\path\to\venv\Scripts\python.exe
```

The launcher records process IDs in `.demo-logs/process-ids.txt`; stopping the launcher window does not stop those background processes. Stop the recorded processes and their child processes before restarting. The explicit manual commands below are also useful when you want terminal-managed processes.

```text
python reset.py --no-provider-switch
python -m uvicorn mock_provider.main:app --host 127.0.0.1 --port 8001
python -m uvicorn dashboard_api:app --host 127.0.0.1 --port 8002
python -m uvicorn client_app.server:app --host 127.0.0.1 --port 8003
```

Use the venv interpreter for each Python command, and run each server in a separate terminal from the repository root. In two more terminals, run `npm run dev` from `frontend` and `swiftpay_frontend`. Vite uses fixed ports and fails if a port is occupied.

| Service | URL |
| --- | --- |
| NexusPay canonical provider | http://localhost:8001 |
| APIShield dashboard API | http://localhost:8002 |
| SwiftPay BFF | http://localhost:8003 |
| APIShield browser UI | http://localhost:5173 |
| SwiftPay browser UI | http://localhost:5174 |

The provider owns V1/V2/V3 and the controls `GET /api/version`, `POST /api/version`, `GET /api/raw_spec`, and `GET /api/provider/logs`. To introduce V2 contract changes:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/version -ContentType application/json -Body '{"version":"v2"}'
```

V1 clients use integer cents and `/refund`. V2/V3 require `{value, currency}` amounts, `/refunds/create`, a real invoice billing-address object, and analytics response unwrapping. Switch to V3 using the same control. Re-run `python reset.py` to restore V1 clients and deterministic graph metadata; it also requests V1 from a running provider. Without a running provider, start it with `API_VERSION=v1`. Reset overwrites the demo client service files, so save any candidate repair before resetting.

## Optional Compose setup

```text
docker compose config --quiet
docker compose build
docker compose run --rm --no-deps dashboard python reset.py --no-provider-switch
docker compose up
```

Compose runs one shared Python image for provider, dashboard and BFF, plus two Vite development images. Browser URLs remain localhost; service-to-service URLs use `mock_provider:8001` and `swiftpay_bff:8003`. Bind mounts share `client_app`, `sig_engine`, and `agent`, so locally repaired source and structured evidence remain visible to the BFF and dashboard. These are development mounts: reset and repair change files in your checkout. `docker compose down` stops the services. No service is hosted or published by this setup.

## Model and publication settings

Configure the managed Google Cloud JSON account in Settings for model inference. `GEMINI_MODEL` defaults to `gemini-3.8-flash`; `POLL_INTERVAL_SECONDS` defaults to 10. Reset builds the graph deterministically by default; `reset.py --infer-with-llm` explicitly enables inference. Models are not called by offline validation and no model behavior is asserted by those tests.

Automatic repair is off at startup and must be enabled explicitly in the dashboard. Repairs require the full affected client test suite to pass; failed candidates restore the original files. IPS is a separate optional model judgment: an unavailable or malformed score is shown as missing evidence and never fabricated. Structured outcomes are `validated`, `failed`, `no_change`, `needs_input`, and `pr_opened`. Auto-merge is disabled.

GitHub publication is optional and requires explicit action plus `GITHUB_TOKEN` and `GITHUB_REPO`. Phase 1 retains a legacy single-file publication helper that opens drafts; a validated multi-file repair reports `needs_input` instead of publishing a partial repair. Phase 4 will provide the complete multi-file reviewable PR flow. Credentials use environment variables before local .env values. Compose does not forward GitHub credentials by default. Offline tests do not publish or call GitHub.

The dashboard stops the demo repair process tree and restores its own client snapshot when a repair times out. If process cleanup fails, it retains the repair lock and reports `needs_input`; stop those processes before restarting the dashboard. This compatibility demonstration uses in-memory recovery; use the Phase 2 CLI or `/api/jobs` endpoints for disposable workspaces and durable reports.

## Validate

```text
python -m pytest -q
cd frontend
npm test
npm run build
npm run lint
cd ../swiftpay_frontend
npm run build
npm run lint
cd ..
docker compose config --quiet
```

Use the venv interpreter. The root CI runs the full Python suite, both frontend builds and lint checks, frontend presentation tests, and Compose syntax validation. Tests cover provider contracts, transactional repair rejection, graph freshness and structured dashboard evidence. Compose syntax validation does not establish a working container build or runtime; those require a running Docker Linux engine. The Vite large-chunk build advisory is a performance warning, not a passing functional test.
