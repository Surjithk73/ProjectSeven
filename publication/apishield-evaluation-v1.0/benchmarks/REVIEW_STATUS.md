# APIShield execution and artifact status — 15 October 2026

This supplement distinguishes actual observations from unavailable measurements. The academic report remains a protocol. The separate synthetic reference manuscript is illustrative and is not validated by these diagnostic runs.

## Active backends

Google documents `gemini-3.8-flash` as GA, released 2 September 2026. The published versions list contains that ID, without a separately addressable immutable snapshot. The profile retains `immutable_snapshot_verified: false`. Each actual response's modelVersion is retained. Do not relabel the ID as an immutable checkpoint. Fixed quotas are unsupported for this model; project usage-tier RPM/TPM have not been retrieved. A single sequential caller and one-second minimum interval are client limits, not provider quotas.

Sources checked: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash and https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions . Request/response JSON schemas describe the benchmark's text-only REST envelope. Actual SDK envelopes and usage metadata are retained in each evidence directory.

The llama.cpp profile pins the published GGUF repository revision and weight fingerprint, requests context 8192, eight threads, 99 GPU layers, Q4_K_M weights and f16 KV cache. These flags describe a deployment request; they do not establish successful offloading. No local engine build or downloaded weights have been verified.

## Actual inference records

`C:/Users/surji/ProjectSeven/benchmarks/runs/gemini_bank014_observed_20261015/` retains the first actual B1–B6 request pass. `C:/Users/surji/ProjectSeven/benchmarks/runs/gemini_bank014_observed_20261015_rep2/` retains the second pass. Both retain provider failures. Successful responses contain actual prompt, cached, candidate-output and reasoning token counters. Zero cached tokens is a valid measurement; token counts are never inflated to satisfy a nonzero-cache assumption. Transport failures do not establish token use or a zero invoice.

Generation-only execution makes no public or hidden test claim. Candidate code is parsed, stored and diffed; it is never imported or run on the host. `t_eval_ms=0` means evaluation was not executed. Visible and hidden exit codes remain null. The first diagnostic pass predates a timing correction: failed call duration is present in model_calls.json and total/overhead time, but may not be assigned to its model phase. The second pass times failed model stages using finally blocks. First-pass cost estimates on unknown transport outcomes are lower-bound known-token estimates, not complete bills. These retained diagnostic limitations are not silently rewritten.

The third pass, `C:/Users/surji/ProjectSeven/benchmarks/runs/gemini_bank014_observed_20261015_sdk/`, uses the standard google-genai HTTP transport instead of the application's custom deadline transport. The same managed JSON service account, requested model and generation parameters are retained. This is a recorded transport diagnostic, not an independent randomized replication. Original failures remain in the first two directories. Response-only inspection does not establish why the previous transport timed out; no production network fix is claimed.

The four authored qualification tasks provide instrumentation checks. They do not substitute for the planned 120-task corpus, model replication, or 3,600-run evaluation. The structural graph here is a small Python AST representation, and the contracts are deliberately minimal; full repository migration findings cannot be inferred from this sample.

## Container boundary

Docker CLI and Compose are installed. Engine connection failed; background desktop startup did not produce an available Linux engine during preparation. Compose configuration validation is separate from container execution verification. No OS sandbox test or Docker image build is claimed without retained execution evidence.

`benchmarks/docker/build.ps1` resolves the Python base tag to an actual registry digest before building. Dockerfile-specific context allowlisting sends only worker files to the daemon. The resulting local content-addressed image ID is written to `benchmarks/provenance/container_image.json` after a successful build; no made-up image digest is supplied.

Candidates, public judges and hidden judges run in separate ephemeral non-root containers. All use network none, a read-only root, dropped capabilities, no-new-privileges, 512 MiB memory and swap ceiling, one CPU, 64 PIDs and a 64 MiB noexec tmpfs. Controller execution additionally bounds stdout/stderr and wall time and removes named containers after timeout. The hidden judge imports only its own trusted oracle and receives serialized candidate outputs. It never mounts or imports candidate Python. Hidden results are evaluated only after the final candidate and never enter the model retry loop. Candidate containers do see hidden input vectors during final execution; hidden assertion code and reference patches remain unavailable to them.

After Docker is running:

```powershell
Set-Location C:/Users/surji/ProjectSeven
./benchmarks/docker/build.ps1
$imageRecord = Get-Content benchmarks/provenance/container_image.json -Raw | ConvertFrom-Json
venv/Scripts/python.exe -B benchmarks/docker/verify_sandbox.py --image $imageRecord.image_id
venv/Scripts/python.exe -B benchmarks/harness/run_ablation.py --mode live --execute-live --allow-unpinned-provider --boundary docker --image $imageRecord.image_id --task TASK-BANK-014 --configuration all --output benchmarks/runs/bank014_container_01
```

The explicit unpinned-provider flag labels this a diagnostic provider run. A study requiring immutable serving weights must resolve that provider limitation before confirmatory deployment.

## Hardware and accounting

The observed machine reports Intel Iris Xe Graphics, display driver 31.0.101.4255, 16 logical CPUs and 8,190,832,640 bytes of system RAM. Win32 AdapterRAM is a reported display-adapter value, not a measured dedicated CUDA VRAM budget. There is no nvidia-smi, nvcc or llama-server available on PATH. No NVIDIA wattage, CUDA version, inference VRAM peak or decoding speed is claimed.

`collect_telemetry.py` records available NVIDIA samples around a supplied inference command and integrates total GPU board power using trapezoidal integration clipped to each run's timestamps. It links the telemetry profile into the ledger. Electricity and amortization rates must be supplied from the operator's actual assumptions. Missing values remain empty. Board energy excludes CPU/system power; cloud energy is not observed. Decoder throughput is read from llama.cpp timing metadata, rather than equating API tokens divided by total latency with decoding speed. Session-wide samples are never arbitrarily divided among runs.

## Commit and archive identity

The checkout has substantial unrelated application edits and user files. Existing HEAD is `80e7bbe0c01b58fa6615098c1bc56c6534a830eb`; it is not the revision containing this artifact. No broad staging or new commit was performed. A clean working-tree anchor cannot be asserted in this checkout. The payload manifest identifies exact working-file bytes independently of HEAD.

The following are reviewable staging commands and a proposed commit message. Review the staged diff before committing; a benchmark-only commit will not make unrelated application edits disappear. Do not include private credentials, model weights or virtual environments.

```powershell
Set-Location C:/Users/surji/ProjectSeven
git add -- benchmarks docs/academic-evaluation-report.md docs/academic-run-record-template.csv
git diff --cached --check
git diff --cached --stat
git commit -m "research: add observed model diagnostics and isolated evaluation tooling"
git rev-parse HEAD
git status --porcelain
```

After scope review, rebuild the review archive from the intended committed checkout and retain its newly generated checksum sidecars. The archive and manifest are not included in their own checksums. Internal payload hashes verify every member; an external manifest verifies the archive, report and metrics without circular hashing. Matching bytes establish provenance consistency, not empirical correctness or artifact badging.

## Observed third-pass inference measurements

All rows requested and returned gemini-3.8-flash. Completion includes provider-reported reasoning tokens. Each row produced a candidate diff; evaluation was not executed.

| Configuration | Prompt tokens | Cached tokens | Completion + reasoning tokens | Wall seconds | API estimate USD |
|---|---:|---:|---:|---:|---:|
| B1 | 365 | 0 | 1006 | 19.648 | 0.00404625 |
| B2 | 435 | 0 | 46 | 34.469 | 0.00049875 |
| B3 | 472 | 0 | 46 | 12.436 | 0.00052650 |
| B4 | 1108 | 0 | 316 | 75.771 | 0.00201600 |
| B5 | 1069 | 0 | 183 | 13.155 | 0.00148800 |
| B6 | 1957 | 0 | 523 | 22.529 | 0.00342900 |

The six candidates have identical patch content in this diagnostic pass. This small, under-specified request-builder task does not establish a benefit from any ablation. No correctness rates, hidden-invariant outcomes, cost per correct repair or statistical model comparisons can be estimated from these unevaluated candidates.

Each run directory also contains source_snapshot_status.json and source_snapshot copies whose bytes were checked against the original run's recorded SHA-256 values before copying. The third pass recovered 83 matching source files, including its actual harness, adapter and model profile. Two non-execution files changed afterward: the package builder and generated hardware telemetry output. Earlier diagnostic passes list their additional source drift explicitly. Their missing historical bytes are not claimed recovered. The current profile's resolved_model_version was subsequently populated from the retained response; the matched profile snapshot preserves the exact configuration used at execution.
