# APIShield artifact and reproducibility appendix

Status on 15 October 2026: qualification package plus observed live inference diagnostics, not a completed model benchmark or an awarded artifact badge. See REVIEW_STATUS.md for current execution limits and reproduction commands. ARTIFACT_APPENDIX.md and runs/qualification_verified preserve the earlier authored-fixture qualification. New gemini_bank014_observed run directories contain actual provider requests, responses and failures; generated candidates have not been container-evaluated. Neither evidence category substantiates the synthetic manuscript's numerical tables.

## 1. Experimental implementation and CLI

Repository HEAD observed: 80e7bbe0c01b58fa6615098c1bc56c6534a830eb. The working tree is dirty and that commit does not contain this new artifact. Each run captures a source_manifest.json of actual file SHA-256 values. No new commit, public archive, DOI or badge was created.

Implementation paths are under C:/Users/surji/ProjectSeven/benchmarks:

- harness/prepare_artifact.py materializes four actual fixtures, contracts, public suites, hidden suites and golden patches.
- harness/run_ablation.py implements the B1–B6 treatment gates and emits raw JSON evidence and a phase ledger.
- runners/candidate_worker.py executes the candidate's build_request interface.
- runners/evaluation.py maintains the controller/candidate boundary.
- adapters/model_backend.py contains explicit Google Cloud and llama.cpp adapters. No adapter falls back to another provider.
- harness/aggregate_metrics.py uses pandas and scipy.stats for metrics, Wilson intervals, paired case bootstrap and Cliff's delta.

The standalone harness does not import dashboard_api or frontend code. Live Google access reuses the production controller's credential/deadline client, not the UI. Fixture mode never imports or invokes the model adapter's generate method.

From the existing ProjectSeven checkout, these exact PowerShell commands reproduce the trusted offline fixtures in a fresh output directory:

```powershell
Set-Location C:/Users/surji/ProjectSeven
venv/Scripts/python.exe -B benchmarks/harness/prepare_artifact.py
venv/Scripts/python.exe -B benchmarks/harness/run_ablation.py --mode fixture --configuration all --task all --repetition 1 --boundary trusted-fixtures --output C:/Users/surji/ProjectSeven/benchmarks/runs/reproduction_01
benchmarks/.venv/Scripts/python.exe -B benchmarks/harness/aggregate_metrics.py --runs C:/Users/surji/ProjectSeven/benchmarks/runs/reproduction_01 --output C:/Users/surji/ProjectSeven/benchmarks/analysis/reproduction_01
```

For a clean installation, create the analysis environment with python -m venv benchmarks/.venv, then install benchmarks/requirements-analysis.txt. The live adapter additionally needs the project's backend dependencies and requirements-live.txt. Python used for qualification: 3.13.3. Existing output directories are refused to preserve evidence.

Configurations are exact JSON in configurations.json. Structural graph is on in B3–B6; semantic clustering in B4/B6; intent inference and generated checks in B5/B6; test feedback in B2–B6. Hidden-oracle evaluation is always enabled. It is an evaluator, not privileged generation context. B5/B6 have a separate enable_generated_checks flag so the independent evaluator is not confused with AI-generated acceptance checks.

Fixture mode exports real treatment-specific prompt contexts, but semantic groups and inferred rules are explicitly authored fixture metadata. The selected candidates intentionally exercise syntax failure, visible-but-incorrect output, abstention and success. This is instrumentation qualification, not a measurement of whether a graph improves model repair.

Live mode requires --mode live --execute-live --boundary docker and an existing image@sha256 digest. Google diagnostic runs additionally require --allow-unpinned-provider until an immutable release is verified. Docker was installed but its Linux daemon was unavailable during preparation. No Docker isolation execution is claimed and no live run was attempted. A supplied image is inspected before any model request.

## 2. Task manifest and physical oracle boundary

tasks_manifest.json and tasks_manifest.schema.json contain four complete records: TASK-BANK-014, TASK-BANK-015, TASK-SHIP-029 and TASK-PAY-008. Every referenced path exists. Public source/docs/tests are under tasks/TASK-ID/public; hidden oracle source, hidden inputs and golden patches are under evaluator_private/TASK-ID. Golden patches are checked with git apply and evaluated independently.

Prompt context is built from a positive allowlist: client.py, old/new documents, optionally public-test source, structural facts, semantic-stage response and inferred-intent-stage response. It is never built by recursively dumping a repository or task manifest. Private paths, oracle source, hidden results and golden patches are not copied into the candidate workspace or prompts.

The Docker candidate has only a read-only /work mount containing the candidate/generated checks and a read-only generic /runner.py mount. It has no host-project, private-oracle, model-credential or Docker-socket mount. Network access is disabled; filesystem is read-only except a bounded /tmp; capabilities are dropped; a non-root user, memory/CPU/PID limits and no-new-privileges are selected. Hidden inputs are sent only as concrete JSON test values. Assertions and expected results execute in the trusted controller outside the candidate container. Candidate outputs return through JSON. A model has no tool/filesystem interface.

The hidden evaluator is called only after the final candidate-selection loop. Its results are retained for the researcher and are never inserted into visible feedback or followed by another model call. The prompt-export tests confirm that private paths and reference-patch names do not appear in fixture prompts.

Trusted-fixtures mode uses native isolated Python processes only for the bundled authored candidates. It is not an OS security boundary and cannot be selected for live model-generated candidates. Docker-mode code has not been exercised on this host. The scaffold is not certified for adversarial repositories: additional output-volume, container lifecycle, source-exfiltration and hostile-runtime security testing is needed before such inputs are admitted. The four fixtures validate request construction and key preservation, not actual distributed banking state or duplicate-payment prevention under network races.

## 3. Original raw records

runs/qualification_verified contains 24 actual local qualification traces plus exported prompts, candidate records, patches, syntax diagnostics and public/hidden execution outputs. Six full representative traces are B1_TASK-BANK-014_rep1.json through B6_TASK-BANK-014_rep1.json. Each has the original 56-column record plus explicit aliases, phase records, boolean invariant maps and provenance.

The fixture traces have requested_model and resolved_model_version set to JSON null, token counts zero, and record_kind fixture_replay because no model was requested. Null here means not observed, not a slot populated with a fabricated identifier. Syntax errors and abstentions have null test exit codes when tests did not execute. Their invariant maps are empty, rather than falsely declaring unexecuted checks failed.

B1 is a genuine syntax-error execution record. B2 passes public tests but fails exact minor-unit preservation. B3 violates identity/destination. B4 is a scripted abstention. B5 violates key preservation. B6 passes the fixture's public and hidden checks. These candidates were authored in fixture_candidates, not produced by Gemini or Llama. Selection of these outcomes is intentional and supplies no performance ranking.

## 4. Model provenance

profiles/gemini.json records the current configured model ID gemini-3.8-flash, global endpoint and google-genai 2.22.0. It does not claim an immutable model snapshot: immutable_snapshot_verified is false and resolved_model_version is null until observed. Parameters are temperature 0.1, top_p 0.95, seed 42, max output 4096 and LOW reasoning. SDK content retries are disabled by the shared client; the research transport loop permits three retries at 1/2/4 seconds for 429/500/502/503/504. Three repair attempts are separate from transport retries. HTTP response metadata and usage are retained for any future live call.

The example gemini-1.5-pro-002 is a real historical release but was retired on 24 September 2025. It is not selected as a runnable current backend. Lifecycle source: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions .

The exact available quantized repository is bartowski/Meta-Llama-3.1-70B-Instruct-GGUF, revision 83fb6e83d0a8aada42d499259bc929d922e9a558. The published file is Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf, size 42,520,398,400 bytes, published LFS SHA-256 f775c87029be95fb41df9e2882e6e938b73121c30ffc235ac6b6b880add49aa5. Published metadata was fetched from https://huggingface.co/api/models/bartowski/Meta-Llama-3.1-70B-Instruct-GGUF?blobs=true . This is a published fingerprint, not a locally verified download. No weight file was downloaded, no engine build was measured and no GPU deployment was observed. The requested meta-llama/Meta-Llama-3.1-70B-Instruct-Q4_K_M name must not be substituted for this actual repository/file provenance.

profiles/llama_cpp.json supplies a concrete local weight path and llama-server command targeting two RTX A6000 48GB GPUs as a planning configuration. GGUF Q4_K_M is not AWQ. The local adapter refuses a missing or mismatched weight and an unrecorded engine version. Future operators must record actual hardware and engine builds; planned hardware cannot be reported as measured hardware. Command reference: https://github.com/ggml-org/llama.cpp/tree/master/tools/server .

## 5. Resource and billing accounting

runs/qualification_verified/resource_ledger.csv is measured local phase timing. Detection, graph, intent, inference, public evaluation, hidden evaluation and overhead reconcile to monotonic elapsed time. A zero inference duration and zero API charge reflect no inference calls, not free use of a proprietary service. CPU energy, GPU wattage and invoices were not measured and remain absent rather than invented.

profiles/rate_card.json records Google Cloud's published global introductory gemini-3.8-flash rates observed on 15 October 2026: USD 0.75 per million input tokens, 0.075 per million cached input tokens and 3.75 per million output/reasoning tokens, through 31 December 2026. Source: https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing . Cached input is a subset of input; reasoning is added to candidate output exactly once. Successful response usage is costed as ((input-cached)*0.75 + cached*0.075 + (candidate-output+reasoning)*3.75)/1,000,000. The official page lists no input/output charge for non-200 responses. Unknown transport outcomes require billing reconciliation; estimates are not invoices.

For a separately labelled planning scenario, energy_kWh = watts/1000 × GPU_active_seconds/3600 and electricity_USD = energy_kWh × tariff_USD_per_kWh. The profile's 600 W and USD 0.20/kWh are explicit assumptions for a proposed two-GPU target, not telemetry or official cloud billing. At 120 GPU-active seconds this scenario is 0.020000 kWh and USD 0.004000 electricity, excluding idle power, host power and capital costs. Actual GPU-active time is not available for these native fixture runs, so the scenario must not be inserted as measured ledger cost.

The aggregation pipeline joins ledger and traces on run_id and checks time/token reconciliation. Its output is analysis/qualification_verified/aggregate_metrics.csv and metrics.json. These are qualification summaries, not replacements for docs/academic-synthetic-reference tables and not a 3,600-run empirical dataset.

## 6. Statistical pipeline and classification rubric

aggregate_metrics.py reads and validates the 56 original columns, derives micro precision/recall from TP/FP/FN, reports public/hidden/delivered success separately, calculates Wilson intervals using scipy.stats.norm, calculates a case-preserving bootstrap and reports descriptive Cliff's delta plus a paired B6–B1 bootstrap contrast. Fixture and live records cannot be pooled. Repeated-task runs are retained together; a full study additionally needs the predeclared family-level hierarchy. Four deliberately selected fixtures do not support generalization or confirmatory significance claims.

Classification precedence:

- INFRASTRUCTURE_ERROR: provider, Docker or harness failure; never counted as appropriate model abstention.
- ABSTAIN/REFUSED: explicit abstention with no candidate; no hidden success is invented.
- SYNTAX_ERROR: candidate fails Python parsing before execution.
- PASS: public and hidden checks pass and enabled generated checks pass.
- PLAUSIBLE_BUT_INCORRECT: public checks and enabled generated checks pass, but hidden checks fail.
- TEST_FAILURE: remaining candidate/test failures, including failed public checks or rejected generated checks.

The two extra classes are necessary: the four requested labels alone cannot faithfully represent public-test failures and infrastructure outages.

## Validation and remaining archival gates

Qualification ran all six configurations over all four fixtures, generated 24 traces and exercised the statistical pipeline. Regression checks cover classification, common hidden evaluation, golden patch application, prompt/oracle separation and refusal of live native execution. These checks do not certify Docker isolation or live backend compatibility.

Before archival as an empirical-study artifact, obtain actual model/snapshot provenance, run and audit the Docker boundary, freeze an actual artifact revision/archive digest, qualify the complete benchmark, collect real model responses and patches, reconcile actual billing/telemetry and regenerate study results. Deposit in a durable repository and seek the venue's evaluation. Packaging alone cannot award Artifacts Evaluated, Artifacts Available or Results Validated badges. ACM policy: https://www.acm.org/publications/policies/artifact-review-and-badging-current .
