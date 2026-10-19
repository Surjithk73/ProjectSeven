# Phase 2: reusable local engine

Authority: IMPLEMENTATION_PLAN.md Phase 2 and the user's instruction to implement that phase. Success means an unfamiliar Python repository yields a local impact report and independently tested patch without changing the source checkout. No publishing, hosted execution or new research claim is included.

The selected approach is a small Python package with explicit configuration, disposable commit-pinned Git snapshots and filesystem-backed job records. Reusing mutable demo globals would keep the tool SwiftPay-specific; introducing the hosted database/container system now would exceed Phase 2. CLI and dashboard job endpoints call the same package. Existing Phase 1 demo controls remain compatibility routes and are identified as a mutable demo.

## Configuration

JSON configuration is version 1. `repository` is a local Git repository path (resolved relative to the config file), `ref` defaults to HEAD, `code_paths` lists relative source directories, `base_spec` and `target_spec` name local JSON OpenAPI files relative to the config file, and `setup_commands`/`test_commands` are lists of argv arrays. `environment` permits explicit non-secret repository settings. Defaults: max_attempts=3, command_timeout_seconds=120, job_timeout_seconds=600, output_limit_bytes=65536, model=gemini-2.5-flash, use_intent=true. No shell string execution, dotenv loading from the target repository or automatic dependency installation. This release supports local Git sources; remote GitHub connection remains an adapter concern in Phase 4.

Reject unknown config keys, invalid/non-finite budgets, traversal/absolute code paths, missing specs, commands with no executable and secret-like environment names. Record a resolved source commit, contract SHA256 hashes and effective budgets in job evidence. Dirty/untracked source changes are excluded and explicitly reported.

## Jobs and execution

Each scan/compare/repair job has a unique directory under a user-selected job root, immutable config/contract snapshots, `events.jsonl`, atomic `result.json`, and optional `candidate.patch`. Export the pinned Git tree into a disposable job workspace, rejecting symlinks, submodule entries and path escapes, and excluding dotenv/private-key files. The source checkout is never edited. Artifacts are outside the supplied source repository. Retain reports after cleaning disposable source, including on failure/cancellation.

Run setup/tests with a minimal OS environment and explicit non-secret settings. Controller model credentials are not forwarded to repository processes. They are used only by an explicit Gemini generator. Local commands are trusted user-configured code and can access the host; this is source isolation, not a security sandbox. Hosted execution requires Phase 6 containers.

Command execution observes per-command and total budgets, caps captured output, stops process descendants on timeout/cancellation and redacts credential-like logs. Cancellation is a persistent request checked between stages and while commands run; CLI Ctrl+C requests cancellation. Model requests have bounded request timeouts; cancellation during inference completes after that bounded request returns. A job interrupted by process loss is reported as interrupted rather than falsely validated.

## Engine

Scan supports direct httpx/requests GET/POST calls and statically resolvable URL constants, assignments and literal f-string paths. Record method, normalized endpoint, file, function, source line and explicit intent label. Dynamic expressions, wrappers or unsupported syntax receive coverage limitations; do not guess a payment endpoint. Comparison uses an explicitly resolved native oasdiff executable against copied specs with a bounded process and strict JSON evidence.

Repair localizes only changed operations. A generator receives current complete source, copied schemas, diff and optional intent, all framed as untrusted data. Offline candidate JSON can be supplied explicitly for reproducibility. Plans contain relative file, exact unique old snippet and replacement, or needs_input. Reject changes outside configured Python source, tests/config/specs, ambiguous/overlapping matches, no-ops and invalid Python. Each attempt restores the same committed base before applying grouped candidates. Run all configured tests, and verify commands did not modify protected repository files or silently rewrite the candidate. Only passing tests with intact checks permit `validated`; no tests yields `needs_input`. Failed/cancelled attempts produce no validated patch.

Reports preserve scan coverage, comparison evidence, validation stdout/stderr/exit/timing, attempts, source revision and terminal status: completed (scan/compare), no_change, needs_input, failed, validated, cancelled. A validated patch is a review artifact and is never applied to the original checkout.

## CLI and dashboard

Commands: `python -m apishield scan|compare|repair --config PATH --jobs-dir PATH`; repair accepts `--candidate PATH` for explicit offline fixtures or uses Gemini with controller credentials. `report JOB_ID --jobs-dir PATH` returns persisted evidence; `cancel JOB_ID --jobs-dir PATH` writes a cancellation request. Provide an installable `apishield` console command. Success exits 0; failure 1; needs_input 2; cancelled 130; malformed CLI/config 2. JSON output is machine-readable.

Dashboard accepts only server-configured integration names/path allowlist, never arbitrary posted command configuration. POST /api/jobs queues a job, GET /api/jobs/{id} reports it, and POST /api/jobs/{id}/cancel requests cancellation. These invoke the exact CLI engine and retain evidence across dashboard restarts. The existing demo trigger is not relabeled as an isolated job. New endpoints remain local development functionality, not hosted authentication.

## Validation

Use a second Git fixture with a shipment endpoint migration and real pytest tests. Assert exact values, source hash stability, pinned revision despite dirty source, reviewed patch applicability, rejected incorrect candidate, cancellation diagnostics, symlink/traversal rejection, unchanged tests and secret-free subprocess environment. No live inference or external publication is needed. Retain the complete Phase 1 suite and frontend build checks.
