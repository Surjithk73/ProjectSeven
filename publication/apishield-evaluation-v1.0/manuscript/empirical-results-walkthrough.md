# Empirical Results and Evaluation

We present the empirical findings from our evaluation of APIShield. We analyze change localization accuracy (RQ1), end-to-end migration correctness and factorial ablation (RQ2, RQ3), domain business invariant preservation (RQ4), and failure-inclusive economic efficiency (RQ5).

## RQ1: Change Detection and Impact Localization

Effective automated migration requires identifying all call sites and data transformations impacted by upstream API contract diffs without overwhelming developers or repair prompts with irrelevant files. Table 4 summarizes detection precision, recall, false-positive rate (FPR), and F1-score across all 120 benchmark tasks (comprising 120 true affected call sites and 120 negative distraction candidates).

```
Table 4: Change Detection and Impact Localization Performance (RQ1, N=120)
Config | TP / FP / FN | Precision (%) | Recall (%) | False Alarm Rate (%) | F1-Score
B1     | 70 / 50 / 50 | 58.3%         | 58.3%      | 41.7%                | 0.583
B2     | 78 / 42 / 42 | 65.0%         | 65.0%      | 35.0%                | 0.650
B3     | 94 / 25 / 26 | 79.0%         | 78.3%      | 20.8%                | 0.787
B4     | 98 / 21 / 22 | 82.4%         | 81.7%      | 17.5%                | 0.820
B5     | 99 / 17 / 21 | 85.3%         | 82.5%      | 14.2%                | 0.839
B6     | 101 / 14 / 19| 87.8%         | 84.2%      | 11.7%                | 0.860
```

Under documentation-only prompting (B1), the language model suffers from severe hallucination and false alarms, achieving an F1-score of only 0.583 with a 41.7% false-alarm rate. Introducing the structural dependency graph (B3) yields the single largest localization improvement, increasing precision by +14.0 percentage points (from 65.0% to 79.0%) and reducing false alarms from 42 to 25. 

When enriched with Semantic Intent Graph (SIG) call-chain representations in APIShield (B6), impact localization reaches 87.8% precision, 84.2% recall, and an F1-score of 0.860, cutting the false alarm rate down to 11.7%. The remaining 19 false negatives stem from dynamic reflection, nested wrapper indirections, and unannotated kwargs dictionaries, which represent natural boundaries for static-semantic analysis.

## RQ2 & RQ3: End-to-End Migration Repair and Factorial Ablation

Table 1 reports visible-test pass rates, independent hidden correctness, repair attempt distributions, runtimes, and failure-inclusive economic costs across all six evaluated treatments on the primary 120-task benchmark using Gemini 3.8 Flash. Table 2 presents the paired statistical contrasts, 95% stratified bootstrap confidence intervals, Cliff's delta effect sizes, and per-task win/loss breakdowns.

```
Table 1: Primary Benchmark & Ablation Study (N=120, Model: Gemini 3.8 Flash)
Config | Visible Pass; % [95% CI] | Hidden Correct; % [95% CI] | Mean Attempts | Runtime (s) | Total ($) | USD/Correct
B1     | 76/120; 63.3% [54.4, 71.4] | 26/120; 21.7% [15.2, 29.9] | 1.00          | 42.0 ± 18.0 | $0.6297   | $0.02422
B2     | 90/120; 75.0% [66.6, 81.9] | 34/120; 28.3% [21.0, 37.0] | 1.60          | 64.0 ± 26.0 | $0.8104   | $0.02384
B3     | 93/120; 77.5% [69.2, 84.1] | 36/120; 30.0% [22.5, 38.7] | 1.50          | 70.0 ± 25.0 | $0.9370   | $0.02603
B4     | 100/120; 83.3% [75.7, 88.9]| 62/120; 51.7% [42.8, 60.4] | 1.45          | 93.0 ± 34.0 | $1.1208   | $0.01808
B5     | 105/120; 87.5% [80.4, 92.3]| 87/120; 72.5% [63.9, 79.7] | 1.35          | 112.0 ± 40.0| $1.3012   | $0.01496
B6     | 111/120; 92.5% [86.4, 96.0]| 97/120; 80.8% [72.9, 86.9] | 1.25          | 128.0 ± 47.0| $1.5578   | $0.01606
```

### The Overfitting Gap in Naive APR
A critical finding is the massive disparity between visible test passage and genuine behavioral correctness in standard LLM repair. Under baseline iterative test-driven repair (B2), 75.0% of generated patches pass the existing unit test suite, but only 28.3% pass the independent hidden behavioral checks. In other words, **62.2% of seemingly successful patches under B2 are overfitted regressions** that introduce silent bugs into production clients (e.g., converting integer cents into floating-point dollars or dropping transaction routing metadata).

### Factorial Ablation Analysis
Analyzing the step-by-step additions reveals the exact mechanisms that resolve this overfitting crisis:
1. **Structural Localization (B3 vs. B2):** Providing structural AST localization alone improves hidden correctness by only +1.7 pp (from 28.3% to 30.0%). While AST localization prevents editing the wrong files, code location alone does not explain semantic intent.
2. **Semantic Intent Graph (B4 vs. B3):** Adding semantic overlays and caller-callee intent representations boosts hidden correctness from 30.0% to 51.7% (+21.7 pp gain), enabling the model to understand the business role of payload parameters.
3. **Inferred Behavioral Invariant Checks (B5 vs. B3):** Synthesizing and executing dynamic invariant assertions during the MAPE-K planning loop produces a massive +42.5 pp surge in hidden correctness (reaching 72.5%), directly exposing semantic regressions before commit.
4. **The Full APIShield Synergy (B6):** Combining structural, semantic, and invariant verification reaches **80.8% hidden correctness (97/120 tasks)**. The visible-to-hidden correctness gap narrows from 46.7 pp (in B2) to just 11.7 pp (in B6).

```
Table 2: Primary Paired Contrasts & Effect Sizes (N=120)
Contrast | Risk Difference [Bootstrap 95% CI] | Cliff's Delta [95% CI] | Win/Loss Breakdown (B6 / Base / Both / Neither)
B6 - B2  | +52.5 pp [42.5, 62.5]             | 0.525 [0.425, 0.625]   | 67 / 4 / 30 / 19
B6 - B3  | +50.8 pp [40.8, 60.8]             | 0.508 [0.408, 0.608]   | 66 / 5 / 31 / 18
```

The paired contrast between APIShield (B6) and baseline iterative repair (B2) demonstrates an enormous +52.5 pp risk difference with Cliff's delta of 0.525, which exceeds the threshold for a large statistical effect. Out of 120 tasks, APIShield succeeds on 67 tasks where B2 fails, whereas B2 succeeds on only 4 tasks where B6 fails.

## RQ4: Domain Invariant Preservation in Mission-Critical APIs

In fintech, banking, and commerce integrations, subtle deviations in payload transformations lead to severe monetary anomalies. We evaluated the preservation of three critical domain invariants across the 60 banking and payment tasks in our benchmark:
1. **Minor-Unit Precision:** Guaranteeing that integer values representing currency cents/subunits are not converted to lossy floating-point decimals.
2. **Idempotency Key Preservation:** Ensuring original idempotency and correlation headers are retained and reused across retries to prevent duplicate billing.
3. **Destination Routing Integrity:** Ensuring recipient identifiers, bank routing codes, and payload account mappings are preserved during schema refactoring.

```
Table 3: Domain Invariant Preservation on Financial Integration Corpus (N=60)
Config | Minor Units (%) | Idempotency Key (%) | Destination Routing (%) | All Invariants Preserved (%)
B1     | 26/60 (43.3%)   | 35/60 (58.3%)       | 45/60 (75.0%)           | 15/60 (25.0%)
B2     | 29/60 (48.3%)   | 40/60 (66.7%)       | 48/60 (80.0%)           | 19/60 (31.7%)
B3     | 32/60 (53.3%)   | 44/60 (73.3%)       | 50/60 (83.3%)           | 21/60 (35.0%)
B4     | 43/60 (71.7%)   | 48/60 (80.0%)       | 53/60 (88.3%)           | 34/60 (56.7%)
B5     | 53/60 (88.3%)   | 55/60 (91.7%)       | 57/60 (95.0%)           | 46/60 (76.7%)
B6     | 56/60 (93.3%)   | 57/60 (95.0%)       | 58/60 (96.7%)           | 52/60 (86.7%)
```

As demonstrated in Table 3, baseline test-driven repair preserves all three invariants in only 31.7% of migrations. Unit tests that assert HTTP 200 or inspect only the top-level response envelope routinely pass patches that convert `$50.00` (5,000 cents) into `50.00` integer or omit idempotency headers. In contrast, APIShield (B6) achieves **86.7% joint invariant preservation**, preserving minor units in 93.3% of tasks and idempotency keys in 95.0% of tasks.

## RQ5: Failure-Inclusive Economic Accounting

A common concern with multi-stage agentic frameworks is token consumption and cost. In Table 1, we account for every failed repair attempt, rejected candidate, and validation run. 
- Baseline B1 has an apparent low cost of $0.00525 per attempt, but because 78.3% of its repairs fail independent testing, its cost per verified correct repair is **$0.02422**.
- Baseline B2 wastes multiple retry iterations chasing misleading test failures, resulting in **$0.02384** per correct repair.
- In contrast, APIShield (B6) resolves migrations in fewer attempts (1.25 mean attempts vs 1.60 for B2), resulting in a failure-inclusive cost of **$0.01606 per correct repair**—a **32.6% cost reduction** compared to B2. In short, semantic guidance prevents wasted exploratory iterations.
