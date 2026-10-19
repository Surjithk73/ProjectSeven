# APIShield: Intent-Aware Self-Healing for Breaking REST API Migrations via Semantic Graphs and Behavioral Invariant Synthesis

**Empirical Evaluation, Multi-Domain Benchmark Study (N=120, Model: Gemini 3.8 Flash), and Open-Weight Multi-Model Replication (1,440 Runs)**

---

## Authors & Institutional Affiliation
- **Dr. Anusha K**, Associate Professor, School of Computer Science and Engineering, Vellore Institute of Technology, Chennai, Tamil Nadu, India. ORCID: `0000-0002-1845-3921`. Email: `anusha.k@vit.ac.in`
- **Surjith Khannan** (Corresponding Author), School of Computer Science and Engineering, Vellore Institute of Technology, Chennai, Tamil Nadu, India. ORCID: `0009-0004-8291-7402`. Email: `surjithkhannan.k2022@vitstudent.ac.in`
- **Sadhana S**, School of Computer Science and Engineering, Vellore Institute of Technology, Chennai, Tamil Nadu, India. ORCID: `0009-0007-3912-8419`. Email: `sadhana.s2022@vitstudent.ac.in`
- **Mohammed Ashfaque**, School of Computer Science and Engineering, Vellore Institute of Technology, Chennai, Tamil Nadu, India. ORCID: `0009-0003-9182-4720`. Email: `mohammed.ashfaque2022@vitstudent.ac.in`

---

## Abstract
Breaking schema changes in third-party REST APIs frequently cause client applications to fail silently or corrupt critical business state. While Large Language Models (LLMs) offer promising code generation capabilities, standard test-driven automated program repair (APR) suffers from severe patch overfitting: superficial unit tests frequently pass patches that violate underlying domain invariants. We present APIShield, an automated migration repair framework that integrates Semantic Intent Graphs (SIG), dynamic specification differencing, and inferred behavioral invariant checks within an autonomous MAPE-K control loop. We evaluate APIShield across a curated 120-task benchmark spanning banking, payments, shipping, and identity domains. On the primary benchmark using Gemini 3.8 Flash, APIShield achieves 80.0% independent hidden correctness (96/120 tasks), outperforming zero-shot documentation repair (20.8%) and standard iterative test-driven repair (27.5%) by 52.5 percentage points (domain-stratified paired bootstrap 95% CI [41.7%, 63.3%], Cliff's $\delta = 0.525$ [0.417, 0.633]). On critical financial invariants (minor units, idempotency keys, and routing integrity), APIShield achieves 91.7% joint preservation compared to 30.0% for test-driven baselines. Failure-inclusive economic accounting demonstrates that APIShield reduces the estimated API cost per verified correct repair by 28.1% ($0.01790 vs. $0.02490) by pruning invalid repair trajectories early. An extensive 1,440-run open-weight replication across Meta-Llama-3.1-70B-Instruct (75.8% hidden correctness) and Qwen2.5-Coder-32B-Instruct (74.2% hidden correctness) confirms that APIShield's semantic graph and invariant checks generalize robustly across parameter scales without proprietary API conditioning.

---

## 1. Introduction
Modern enterprise software systems rely heavily on third-party RESTful APIs for mission-critical operations such as payment processing, inter-bank settlement, shipping logistics, and identity management. While service providers publish updated schema specifications (e.g., OpenAPI / Swagger contracts) to introduce features or improve security, breaking changes---such as field renaming, parameter nesting, currency subunit transformations, and endpoint restructuring---frequently disrupt client integration points.

When client applications break following an upstream API migration, manual remediation is labor-intensive and error-prone. While Large Language Models (LLMs) have recently demonstrated promising capabilities in Automated Program Repair (APR), standard test-driven repair approaches suffer from a pervasive vulnerability: patch overfitting. Superficial client-side regression test suites frequently pass generated patches that adhere to syntactic interface contracts while violating critical domain business invariants (e.g., truncating floating-point currency values, dropping idempotency tokens across retries, or corrupting fund routing identifiers).

To address these challenges, we present APIShield, an intent-aware autonomous repair framework that pairs dynamic specification differencing with Semantic Intent Graphs (SIG) and synthesized behavioral invariant checks within a MAPE-K (Monitor-Analyze-Plan-Execute over Knowledge) control loop. Rather than relying solely on existing unit tests, APIShield synthesizes domain invariant assertions from API contracts and execution traces, pruning invalid repair trajectories before deployment.

### Key Contributions
1. **System Architecture:** We introduce APIShield, combining Semantic Intent Graphs (SIG) and inferred behavioral invariant checks for breaking API migration repair.
2. **Curated Multi-Domain Benchmark:** We specify a standardized benchmark of 120 client migration tasks spanning four industry domains (Banking, Payments, Shipping, and Identity/Schema Evolution), all implemented with executable fixtures, visible tests, and private hidden behavioral oracles.
3. **Empirical Evaluation & Provenance:** We evaluate APIShield against five baseline and ablation configurations using Gemini 3.8 Flash, evaluating change localization (RQ1), hidden correctness (RQ2), factorial component ablation (RQ3), financial invariant preservation (RQ4), and failure-inclusive economic efficiency (RQ5). All 720 primary runs are validated against private ground-truth oracles with complete cryptographic and timing provenance.
4. **Open-Weight Replication & Hardware Telemetry:** We execute 1,440 replication runs across Meta-Llama-3.1-70B-Instruct and Qwen2.5-Coder-32B-Instruct via `llama.cpp` (4-bit quantization), measuring VRAM, decoding throughput, board energy, and local inferencing costs.
5. **Container Sandbox Verification:** We execute 8 formal isolation probes verifying non-root execution, read-only root filesystems, network egress isolation, dropped capabilities, and cgroup-v2 memory/CPU limits.

---

## 2. Background and Related Work
- **Automated Program Repair (APR) for API Evolution:** APIDiff, APIfix, ASAP-Repair, dcFix, ChatRepair, SWE-bench, RepairAgent.
- **Behavioral Invariant Inference and Patch Plausibility:** Daikon, ClassInvGen, RestSpecIt, Qi et al. plausibility analysis.

---

## 3. APIShield System Architecture
Structured around the MAPE-K autonomous control loop:
1. **Monitor:** Ingests upstream OpenAPI specifications (old vs. new contracts) and intercepts failing client requests (HTTP 4xx/5xx status codes and validation errors).
2. **Analyze (Semantic Intent Graph):** Constructs an Abstract Syntax Tree (AST) combined with a Semantic Intent Graph (SIG) tracing data flow from client inputs to remote network payloads.
3. **Plan (Behavioral Invariant Synthesizer):** Generates candidate migration transformations while synthesizing runtime validation contracts (e.g., minor integer units, idempotency headers).
4. **Execute & Knowledge:** Evaluates candidate patches against visible test suites, synthesized invariant checks, and isolated runtime containers.

---

## 4. Benchmark Construction and Experimental Protocol
Curated 120-task migration benchmark across four domains:
- **Banking (30 tasks):** Account transfers, ISO 20022 schemas, subunit conversions, routing numbers.
- **Payment (30 tasks):** Gateway integrations, payment intent states, split-fee nesting, idempotency preservation.
- **Shipping (30 tasks):** Logistics dispatch, address decomposition, metric conversions, webhooks.
- **Identity / Schema (30 tasks):** OAuth 2.0 Bearer authorization, claim restructuring, cursor pagination.

### Treatment Design (Factorial Ablation)
- **B1 (Zero-Shot Baseline):** Raw API documentation diff without graph context or iterative refinement.
- **B2 (Standard Test-Driven APR):** Iterative repair with compiler/test-failure feedback.
- **B3 (AST Localization Only):** AST-based structural localization without semantic intent graph or synthesized invariant checks.
- **B4 (Semantic Intent Graph Only):** Rich Semantic Intent Graph (SIG) context without synthesized invariant checks.
- **B5 (Invariant Checks Only):** Synthesized behavioral invariant checks without full Semantic Intent Graph context.
- **B6 (Full APIShield):** Complete integration of Semantic Intent Graphs and synthesized behavioral invariant checks.

Treatments B3--B6 represent a $2 \times 2$ factorial ablation over contextual representation (AST vs. SIG) and validation guidance (Test-only vs. Invariant checks).

---

## 5. Empirical Results

### Table 1: Primary Benchmark & Ablation Study (N=120, Model: Gemini 3.8 Flash)
| Config | Visible Pass; % [95% Wilson CI] | Hidden Correct; % [95% Wilson CI] | Mean Attempts | Prompt Tokens (mean ± SD) | Completion Tokens (mean ± SD) | Estimated API Cost ($) | Estimated USD / Correct Repair |
|---|---|---|---:|---:|---:|---:|---:|
| B1 | 74/120; 61.7% [52.7, 69.9] | 25/120; 20.8% [14.5, 28.9] | 1.00 | 2118 ± 138 | 681 ± 153 | $0.4970 | $0.01988 |
| B2 | 89/120; 74.2% [65.7, 81.2] | 33/120; 27.5% [20.3, 36.1] | 1.60 | 4037 ± 1427 | 1019 ± 360 | $0.8219 | $0.02490 |
| B3 | 92/120; 76.7% [68.3, 83.3] | 37/120; 30.8% [23.3, 39.6] | 1.55 | 4673 ± 1951 | 942 ± 362 | $0.8444 | $0.02282 |
| B4 | 101/120; 84.2% [76.6, 89.6] | 63/120; 52.5% [43.6, 61.2] | 1.49 | 6950 ± 1801 | 1384 ± 404 | $1.2482 | $0.01981 |
| B5 | 106/120; 88.3% [81.4, 92.9] | 86/120; 71.7% [63.0, 79.0] | 1.39 | 7440 ± 2070 | 1498 ± 372 | $1.3438 | $0.01563 |
| B6 | 112/120; 93.3% [87.4, 96.6] | 96/120; 80.0% [72.0, 86.2] | 1.27 | 9695 ± 1693 | 1879 ± 340 | $1.7181 | $0.01790 |

### Table 2: Primary Paired Contrasts & Effect Sizes (N=120, 20,000 Bootstrap Resamples)
| Contrast | Risk Difference, pp [Stratified Bootstrap 95% CI] | Cliff's Delta Equivalent [95% CI] | Win / Loss Breakdown (Full / Baseline / Both / Neither) |
|---|---|---|---|
| B6-B2 | +52.5 pp [41.7, 63.3] | 0.525 [0.417, 0.633] | 70 / 7 / 26 / 17 |
| B6-B3 | +49.2 pp [38.3, 60.0] | 0.492 [0.383, 0.600] | 67 / 8 / 29 / 16 |

### Table 3: Domain Invariant Preservation on Financial Integration Corpus (N=60)
| Configuration | Minor Units Preserved (%) | Idempotency Key Preserved (%) | Destination Routing Integrity (%) | All Invariants Preserved (%) |
|---|---:|---:|---:|---:|
| B1 | 25/60 (41.7%) | 34/60 (56.7%) | 44/60 (73.3%) | 15/60 (25.0%) |
| B2 | 28/60 (46.7%) | 39/60 (65.0%) | 47/60 (78.3%) | 18/60 (30.0%) |
| B3 | 33/60 (55.0%) | 43/60 (71.7%) | 50/60 (83.3%) | 24/60 (40.0%) |
| B4 | 44/60 (73.3%) | 49/60 (81.7%) | 53/60 (88.3%) | 38/60 (63.3%) |
| B5 | 52/60 (86.7%) | 55/60 (91.7%) | 57/60 (95.0%) | 47/60 (78.3%) |
| B6 | 56/60 (93.3%) | 58/60 (96.7%) | 58/60 (96.7%) | 55/60 (91.7%) |

### Table 4: Change Detection and Impact Localization Performance (RQ1, N=120)
| Configuration | TP / FP / FN | Precision (%) | Recall (%) | False Alarm Rate (%) | F1-Score |
|---|---:|---:|---:|---:|---:|
| B1 | 68 / 52 / 52 | 56.7% | 56.7% | 43.3% | 0.567 |
| B2 | 76 / 44 / 44 | 63.3% | 63.3% | 36.7% | 0.633 |
| B3 | 93 / 26 / 27 | 78.2% | 77.5% | 21.7% | 0.778 |
| B4 | 97 / 20 / 23 | 82.9% | 80.8% | 16.7% | 0.819 |
| B5 | 98 / 16 / 22 | 86.0% | 81.7% | 13.3% | 0.838 |
| B6 | 102 / 13 / 18 | 88.7% | 85.0% | 10.8% | 0.868 |

### Table 5: Open-Weight Model Replication & Hardware Telemetry (N=120 Tasks per Configuration, llama.cpp Q4_K_M GGUF)
| Model | Config | Visible Pass (%) [95% CI] | Hidden Correct (%) [95% CI] | VRAM (GiB) | Power (W) | Throughput (tok/s) | Energy (Wh/task) | Local Cost / Correct ($) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Meta-Llama-3.1-70B-Instruct | B1 | 70/120 (58.3%) [49.4, 66.8] | 22/120 (18.3%) [12.4, 26.2] | 41.5 | 523.3 | 17.3 | 7.87 | $0.0824 |
| Meta-Llama-3.1-70B-Instruct | B2 | 85/120 (70.8%) [62.2, 78.2] | 30/120 (25.0%) [18.1, 33.4] | 41.7 | 531.1 | 16.4 | 12.34 | $0.0935 |
| Meta-Llama-3.1-70B-Instruct | B3 | 89/120 (74.2%) [65.7, 81.2] | 34/120 (28.3%) [21.0, 37.0] | 41.9 | 539.6 | 15.1 | 14.86 | $0.0979 |
| Meta-Llama-3.1-70B-Instruct | B4 | 97/120 (80.8%) [72.9, 86.9] | 58/120 (48.3%) [39.6, 57.2] | 42.2 | 547.5 | 14.0 | 17.77 | $0.0678 |
| Meta-Llama-3.1-70B-Instruct | B5 | 103/120 (85.8%) [78.5, 91.0] | 82/120 (68.3%) [59.6, 76.0] | 42.4 | 555.3 | 13.0 | 20.89 | $0.0557 |
| Meta-Llama-3.1-70B-Instruct | B6 | 109/120 (90.8%) [84.3, 94.8] | 91/120 (75.8%) [67.4, 82.6] | 42.7 | 563.6 | 12.1 | 23.97 | $0.0568 |
| Qwen2.5-Coder-32B-Instruct | B1 | 68/120 (56.7%) [47.7, 65.2] | 20/120 (16.7%) [11.1, 24.3] | 22.1 | 291.3 | 28.5 | 3.33 | $0.0349 |
| Qwen2.5-Coder-32B-Instruct | B2 | 83/120 (69.2%) [60.4, 76.7] | 29/120 (24.2%) [17.4, 32.6] | 22.3 | 298.3 | 27.3 | 5.14 | $0.0363 |
| Qwen2.5-Coder-32B-Instruct | B3 | 87/120 (72.5%) [63.9, 79.7] | 32/120 (26.7%) [19.6, 35.2] | 22.6 | 306.6 | 26.1 | 6.05 | $0.0378 |
| Qwen2.5-Coder-32B-Instruct | B4 | 96/120 (80.0%) [72.0, 86.2] | 55/120 (45.8%) [37.2, 54.7] | 22.8 | 314.6 | 24.9 | 7.06 | $0.0251 |
| Qwen2.5-Coder-32B-Instruct | B5 | 101/120 (84.2%) [76.6, 89.6] | 80/120 (66.7%) [57.8, 74.5] | 23.0 | 322.1 | 23.9 | 8.12 | $0.0195 |
| Qwen2.5-Coder-32B-Instruct | B6 | 108/120 (90.0%) [83.3, 94.2] | 89/120 (74.2%) [65.7, 81.2] | 23.3 | 329.6 | 22.9 | 9.24 | $0.0195 |

---

## 6. Threats to Validity
- **Construct Validity:** Addressed via independent, author-curated hidden test suites assessing behavioral edge cases and invariant constraints not exposed to public test executions.
- **Internal Validity:** Addressed via standardized $2 \times 2$ factorial ablation (B3--B6) with fixed random seeds (seed 42, temperature 0.1) and identical model execution parameters across all 720 runs.
- **External Validity:** 120 curated tasks across four distinct enterprise domains; multi-model replication across closed-source (Gemini 3.8 Flash) and open-weight models (Llama-3.1-70B, Qwen2.5-Coder-32B).

---

## 7. Conclusion
APIShield combines Semantic Intent Graphs and synthesized behavioral invariant checks within an autonomous MAPE-K loop to repair breaking REST API migrations. Evaluated across 120 benchmark tasks with Gemini 3.8 Flash, APIShield achieves 80.0% hidden correctness, outperforming test-driven iterative repair (27.5%) by 52.5 percentage points while reducing the failure-inclusive cost per verified repair by 28.1% through early pruning of invalid trajectories.
