# Results and Evaluation: Synthetic Benchmark Model and Theoretical Walkthrough

**Status: synthetic projection for manuscript layout and structural review.** All correctness outcomes, detection outcomes, task-level variation, runtime distributions and comparative effects below are constructed. They are not observations from container execution or estimates of APIShield's demonstrated performance. Actual inference diagnostics inform only the approximate aggregate token-budget anchor. This section must retain its synthetic designation in drafts and publications; replacing it with empirical findings requires independently evaluated executions.

## Evaluation model and reporting conventions

The projection comprises 120 hypothetical migration tasks: 30 banking, 30 payments, 30 shipping, and 30 identity/multi-endpoint-schema tasks. Applying each of six configurations to the same tasks yields 720 synthetic task-configuration records. These records are separate from the real inference logs and qualification records.

The treatments are B1, code and old/new API documentation; B2, B1 plus existing tests and visible feedback; B3, B2 plus structural localization; B4, B3 plus inferred semantic relationships; B5, B3 plus inferred intent and generated behavioral checks; and B6, B3 plus both semantic relationships and intent-based checks. The independent hidden evaluator is identical across treatments and supplies no retry feedback. Model-generated checks are development-time feedback, not the independent hidden oracle.

Each task has one truly affected and one unaffected candidate location, giving 120 positive and 120 negative detection opportunities. Precision therefore uses TP/(TP+FP), recall uses TP/120, and false-positive rate uses FP/120. Precision depends on this stipulated candidate prevalence. The requested approximately 28% baseline hidden outcome is interpreted as a pass rate, rather than a failure rate.

For binary outcomes, reported values are percentages plus or minus Bernoulli outcome SD, computed as 100 sqrt(p(1-p)), in percentage points. These SDs describe task/outcome heterogeneity, not uncertainty in the mean. Resource SDs are sample SDs across 120 constructed task records. Wilson intervals are nominal 95% intervals conditional on the synthetic counts; they do not quantify uncertainty about actual system effectiveness. No significance claim is inferred from constructed data.

## Change detection and localization

**Table 1: Synthetic Benchmark Projection & Ablation Model (N=120). Detection counts and projected localization quality.**

| Configuration | TP / FP / FN | Precision, % ± SD | Recall, % ± SD | False-positive rate, % | Precision: conditional 95% Wilson interval, % |
|---|---:|---:|---:|---:|---:|
| B1 | 70 / 50 / 50 | 58.3 ± 49.3 | 58.3 ± 49.3 | 41.7 | 49.4–66.8 |
| B2 | 78 / 42 / 42 | 65.0 ± 47.7 | 65.0 ± 47.7 | 35.0 | 56.1–72.9 |
| B3 | 94 / 25 / 26 | 79.0 ± 40.7 | 78.3 ± 41.2 | 20.8 | 70.8–85.3 |
| B4 | 98 / 21 / 22 | 82.4 ± 38.1 | 81.7 ± 38.7 | 17.5 | 74.5–88.2 |
| B5 | 99 / 17 / 21 | 85.3 ± 35.4 | 82.5 ± 38.0 | 14.2 | 77.8–90.6 |
| B6 | 101 / 14 / 19 | 87.8 ± 32.7 | 84.2 ± 36.5 | 11.7 | 80.6–92.6 |

The model assigns the largest initial localization improvement to the structural graph: B3 improves precision by 14.0 percentage points over B2 and reduces false alarms from 42 to 25. The full configuration retains 19 false negatives and 14 false positives, reflecting unresolved dynamic dispatch, ambiguous wrappers and incomplete semantic evidence as anticipated failure classes. These classes motivate future measurements; their prevalence has not been established by execution.

Detection and repair remain distinct outcomes. A model may produce a patch passing weak visible tests despite incomplete localization, while an accurately localized operation may still be repaired incorrectly. The constructed records constrain hidden-correct repairs to tasks whose affected location was detected, without equating detection success with behavioral correctness.

## Visible plausibility and independent correctness

**Table 2: Synthetic Benchmark Projection & Ablation Model (N=120). Visible-test success versus independent hidden correctness.**

| Configuration | Visible passes | Visible pass rate, % ± SD | Hidden passes | Hidden pass rate, % ± SD | Visible-pass / hidden-fail cases | Hidden: conditional 95% Wilson interval, % |
|---|---:|---:|---:|---:|---:|---:|
| B1 | 76/120 | 63.3 ± 48.2 | 26/120 | 21.7 ± 41.2 | 50/120 | 15.2–29.9 |
| B2 | 90/120 | 75.0 ± 43.3 | 34/120 | 28.3 ± 45.1 | 56/120 | 21.0–37.0 |
| B3 | 93/120 | 77.5 ± 41.8 | 36/120 | 30.0 ± 45.8 | 57/120 | 22.5–38.7 |
| B4 | 100/120 | 83.3 ± 37.3 | 62/120 | 51.7 ± 50.0 | 38/120 | 42.8–60.4 |
| B5 | 105/120 | 87.5 ± 33.1 | 87/120 | 72.5 ± 44.7 | 18/120 | 63.9–79.7 |
| B6 | 111/120 | 92.5 ± 26.3 | 97/120 | 80.8 ± 39.4 | 14/120 | 72.9–86.9 |

Hidden success denotes passing visible tests and every applicable independent behavioral assertion. Consequently, hidden successes form a subset of visible successes. The model intentionally represents weak tests accepting structurally plausible but semantically incorrect migrations. B2's visible success of 75.0% coexists with hidden correctness of 28.3%; 56 of its 90 visible-pass candidates, or 62.2%, remain behaviorally incorrect in this scenario. B3 improves localization substantially but hidden correctness only modestly, illustrating the hypothesis that code relevance alone does not establish preservation of business behavior.

Relative to B2, B6 increases visible success by 17.5 percentage points and hidden correctness by 52.5 points. The visible-minus-hidden gap falls from 46.7 to 11.7 points. However, 14 of B6's 111 visible-pass candidates, or 12.6%, still fail hidden checks. The projection therefore preserves a consequential residual risk instead of treating inferred checks as a correctness guarantee.

The paired B2–B6 allocation contains 30 tasks passed by both configurations, 67 passed only by B6, four passed only by B2, and 19 passed by neither. The net difference is 63/120, or 52.5 percentage points; the synthetic risk ratio is 97/34 = 2.85. Resampling the paired synthetic task differences 20,000 times with seed 42 yields a conditional percentile interval of 42.5–62.5 points. This interval is an illustration of the planned analysis pipeline, not empirical evidence for the hypothesized effect. The four reversals explicitly allow additional context or generated checks to cause regressions.

## Behavioral invariant preservation

The three named financial invariants apply to the 60 banking and payment tasks. They are not assigned artificial pass outcomes on shipping or identity tasks. Those domains receive appropriate independent checks, including quantity/unit preservation and identity/schema semantics.

**Table 3: Synthetic Benchmark Projection & Ablation Model (N=120). Financial invariant preservation; each percentage uses the applicable financial subset n=60.**

| Configuration | Exact minor units, % ± SD | Idempotency key preservation, % ± SD | Destination integrity, % ± SD | All three financial invariants, % ± SD |
|---|---:|---:|---:|---:|
| B1 | 43.3 ± 49.6 | 58.3 ± 49.3 | 75.0 ± 43.3 | 25.0 ± 43.3 |
| B2 | 48.3 ± 50.0 | 66.7 ± 47.1 | 80.0 ± 40.0 | 31.7 ± 46.5 |
| B3 | 53.3 ± 49.9 | 73.3 ± 44.2 | 83.3 ± 37.3 | 35.0 ± 47.7 |
| B4 | 71.7 ± 45.1 | 80.0 ± 40.0 | 88.3 ± 32.1 | 56.7 ± 49.6 |
| B5 | 88.3 ± 32.1 | 91.7 ± 27.6 | 95.0 ± 21.8 | 76.7 ± 42.3 |
| B6 | 93.3 ± 24.9 | 95.0 ± 21.8 | 96.7 ± 18.0 | 86.7 ± 34.0 |

The modeled B2–B6 gains are 45.0 points for minor-unit preservation, 28.3 for idempotency keys, and 16.7 for destination integrity. Minor units receive the largest projected gain because simple response-shape assertions can accept a re-nested amount while overlooking a cents-to-dollars conversion. Idempotency preservation additionally requires retaining the original caller-supplied key rather than generating a fresh identifier. Destination integrity requires preserving the intended beneficiary through request-body restructuring.

The joint financial outcomes reconcile with Table 2. B6 passes all financial checks on 52 of 60 financial tasks and passes the applicable hidden checks on 45 of 60 nonfinancial tasks, giving 97 hidden successes overall. B2's corresponding counts are 19 and 15, giving 34. Joint outcomes are explicitly constructed; they are not obtained by assuming independence and multiplying marginal invariant probabilities.

### Theoretical banking walkthrough

Consider a hypothetical migration from amount_cents to amount.value. For an input of 1,999 minor units, a plausible but incorrect patch may send amount.value = 19.99. A weak test checking only the presence of amount can pass that patch. The intended behavioral check instead asserts exact preservation of the integer value 1,999, the supplied currency, destination identifier and idempotency key. A second invocation uses the same key to check the required retry identity. Actual duplicate-transfer prevention additionally requires a stateful provider oracle; merely preserving the request key does not prove exactly-once execution. Table 3 models key preservation, not a verified distributed-systems guarantee.

The B6 hypothesis is that graph-supported context and inferred checks expose these obligations before the final independent evaluation. Hidden assertions themselves are never used to construct or refine the repair. This walkthrough is invented to explain the proposed mechanism; it is not a report of a repaired application execution.

## Computational resource and cost projection

The observed six-configuration inference baseline contained 5,406 prompt tokens and 2,120 completion/reasoning tokens in aggregate. It was not a per-configuration or per-task benchmark mean. For this planning model, the anchor is rounded to 5,400/2,100 and synthetically redistributed across B1–B6 as input budgets of 450, 650, 800, 1,000, 1,150 and 1,350, and output budgets of 250, 280, 320, 350, 400 and 500. These allocations sum to the rounded anchor but do not reproduce the observed per-configuration allocation.

The modeled corpus then uses four times the input budget and three times the output budget to represent larger contexts and staged reasoning. Table 4 reports the resulting means and constructed task-level variation. These multipliers are assumptions, not fitted estimates. Token budgets include all modeled stages and retry allowances; an additional retry multiplier is not applied. Runtime includes detection/context preparation, model stages and projected evaluation, whereas the live diagnostic runs did not execute container tests.

**Table 4: Synthetic Benchmark Projection & Ablation Model (N=120). Per-task tokens and wall-clock resources.**

| Configuration | Prompt tokens, mean ± SD | Completion/reasoning tokens, mean ± SD | Wall seconds/task, mean ± SD | Serial wall hours for 120 tasks |
|---|---:|---:|---:|---:|
| B1 | 1,800 ± 540 | 750 ± 262 | 42.0 ± 18.0 | 1.400 |
| B2 | 2,600 ± 780 | 840 ± 294 | 64.0 ± 26.0 | 2.133 |
| B3 | 3,200 ± 960 | 960 ± 336 | 70.0 ± 25.0 | 2.333 |
| B4 | 4,000 ± 1,200 | 1,050 ± 368 | 93.0 ± 34.0 | 3.100 |
| B5 | 4,600 ± 1,380 | 1,200 ± 420 | 112.0 ± 40.0 | 3.733 |
| B6 | 5,400 ± 1,620 | 1,500 ± 525 | 128.0 ± 47.0 | 4.267 |

API estimates use the published global introductory rates of USD 0.75 per million input tokens and USD 3.75 per million output/reasoning tokens, applicable through 31 December 2026. No cache discount is assumed. Source: https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing . Subsequent pricing changes require recomputation.

For a non-API planning allowance, the host is assumed to consume 65 W, electricity costs USD 0.20/kWh, and reserved controller/evaluation capacity costs USD 0.08/hour, exclusive of electricity. Charging that reserved host throughout wall time adds USD 0.093/hour. These are stipulated costs, not local telemetry measurements. They exclude engineering time, tax, provider-side energy, archive storage and deployment costs.

For task i, C_API,i = (0.75 I_i + 3.75 O_i)/1,000,000 and C_total,i = C_API,i + 0.093 T_i/3,600. Cost per hidden-correct repair is the suite's modeled total expenditure divided by its synthetic hidden-pass count, including expenditure on failed repairs.

**Table 5: Synthetic Benchmark Projection & Ablation Model (N=120). Estimated USD costs; all values are modeled, not invoices.**

| Configuration | Total USD/task, mean ± SD | API USD for 120 tasks | API + modeled host USD for 120 tasks | USD per hidden-correct repair |
|---|---:|---:|---:|---:|
| B1 | 0.00525 ± 0.00183 | 0.4995 | 0.6297 | 0.02422 |
| B2 | 0.00675 ± 0.00233 | 0.6120 | 0.8104 | 0.02384 |
| B3 | 0.00781 ± 0.00259 | 0.7200 | 0.9370 | 0.02603 |
| B4 | 0.00934 ± 0.00311 | 0.8325 | 1.1208 | 0.01808 |
| B5 | 0.01084 ± 0.00359 | 0.9540 | 1.3012 | 0.01496 |
| B6 | 0.01298 ± 0.00434 | 1.1610 | 1.5578 | 0.01606 |

Across all six configurations, the model allocates 2.592 million prompt tokens and 0.756 million output/reasoning tokens, USD 4.7790 in API charges, USD 6.3569 including the stipulated host allowance, and 16.967 serial wall hours. These totals cover one pass through 720 configuration-task combinations. They do not cover repeated trials or open-weight replication.

B6 costs approximately 1.92 times B2 per attempted task but 32.6% less per hidden-correct repair under the constructed outcomes. B5 is more cost-efficient than B6 on that latter measure, while B6 obtains ten additional hidden-correct repairs at an incremental modeled suite cost of USD 0.2566. Thus, the scenario expresses a correctness–cost tradeoff rather than making the full system optimal on every criterion. The low absolute costs depend on small text contexts and explicitly chosen host assumptions; they are not forecasts of a production research budget.

## Ablation interpretation and limitations

The constructed B3–B2 contrast yields a 14.0-point precision gain but only a 1.7-point hidden-correctness gain. Adding semantic relationships to B3 yields a 21.7-point hidden gain, whereas adding inferred intent and generated checks yields 42.5 points. Adding semantic relationships when checks are already present yields a further 8.3 points, from B5 to B6.

These effects are deliberately sub-additive: B6 - B4 - B5 + B3 equals -13.3 percentage points. Semantic context and behavioral checks are modeled as addressing overlapping failure classes. The projection therefore does not support a claim of super-additive synergy. It specifies a hypothesis that the eventual factorial contrasts can test.

The projected B2–B6 difference cannot establish causality, model superiority or publication-ready effectiveness. Both means and distributions are stipulated, the financial subset is selected, and the benchmark prevalence and cost multipliers influence the apparent advantage. Conditional intervals exclude uncertainty about those design choices. Actual evaluation must replace the constructed outcomes, retain failed and abstained runs, use independent hidden oracles, preserve task-family pairing, and test sensitivity to corpus size, model backend and cost assumptions. No empirical table or recorded execution trace has been overwritten by this layout exercise.

## Synthetic data accompanying this section

`synthetic_outcomes.csv` contains 720 explicitly labelled task-configuration records. `synthetic_financial_invariants.csv` contains 360 applicable financial-subset records. `synthetic_metrics.json` records the seed, assumptions and derived summaries. The data use seed 20261015; the illustrative paired bootstrap uses seed 42. Dataset membership, binary marginals, paired comparisons, token totals and cost identities were checked for reconciliation.
