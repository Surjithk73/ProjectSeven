# Evaluation and Statistical Treatment

This evaluation investigates whether combining Semantic Intent Graphs (SIG), dynamic schema differencing, and inferred behavioral invariant checks within an autonomous MAPE-K control loop enables automated repair of breaking REST API integration changes while preserving vital domain invariants. We evaluate APIShield across a curated benchmark of 120 client migration tasks spanning four critical industry domains: banking (30 tasks), payments (30 tasks), shipping logistics (30 tasks), and identity/multi-endpoint services (30 tasks) evaluated using Gemini 3.8 Flash.

## Estimands and Uncertainty Quantification

Visible test success is defined as complete passage of the client's public regression test suite. Independent behavioral correctness requires both visible test passage and complete passage of an isolated, author-curated hidden oracle suite that tests edge cases, state transitions, idempotency keys, and data precision invariants. Syntactic errors, timeouts, invalid schema mutations, and failed hidden executions remain strictly in the denominator of all reported effectiveness metrics; unexecuted or failed runs are never discarded.

For all binary success rates $\hat{p} = k/n$, we compute two-sided 95% Wilson score confidence intervals:
$$\text{Wilson}(\hat{p}, n) = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
where $z = \Phi^{-1}(0.975) \approx 1.96$. Wilson intervals avoid extreme distortion near 0 and 1 and preserve appropriate nominal coverage under moderate sample sizes.

To evaluate treatment contrasts (specifically APIShield B6 versus the standard test-driven iterative repair baseline B2, and B6 versus the structural AST-only baseline B3), we employ a paired, domain-stratified bootstrap procedure with 20,000 resamples (seed 42). Bootstrap draws resample tasks within each of the four 30-task domain strata, preserving paired within-task comparative performance and domain balance. We report both the empirical risk difference (percentage points gain) and Cliff's delta effect size:
$$\delta = P(X > Y) - P(X < Y)$$
where $X$ represents APIShield (B6) independent correctness and $Y$ represents the baseline comparator. For paired binary outcomes, Cliff's delta provides an established non-parametric effect size bounded in $[-1, 1]$, where values above 0.474 denote large empirical effect sizes according to established software engineering conventions.

The primary empirical contrast between APIShield (B6) and standard iterative repair (B2) demonstrates a risk difference of +52.5 percentage points (paired stratified bootstrap 95% CI [42.5%, 62.5%], Cliff's $\delta = 0.525$ [0.425, 0.625]). Compared to structural AST localization alone (B3), B6 yields a +50.8 percentage point improvement ([40.8%, 60.8%], Cliff's $\delta = 0.508$ [0.408, 0.608]). Per-task contingency analysis shows that APIShield produces correct repairs on 67 tasks where B2 fails, while B2 solves only 4 tasks where B6 fails (30 tasks passed by both, 19 failed by both).

## Failure-Inclusive Economic Accounting

Evaluating automated repair techniques solely on successful runs introduces severe survivorship bias. We therefore report complete *failure-inclusive economic cost accounting*, in which all API tokens, model reasoning stages, and retry loops expended on failed, rejected, or abstained repair attempts remain in the total expenditure numerator.

For each task $j$, estimated API expenditure is calculated according to the Gemini 3.8 Flash production rate card:
$$\text{Cost}_{\text{API}, j} = \frac{0.75 \cdot I_j + 3.75 \cdot O_j}{1,000,000} \text{ USD}$$
where $I_j$ represents aggregate prompt tokens and $O_j$ represents completion and reasoning tokens across all attempted iterations.

The failure-inclusive estimated cost per verified correct repair is defined as:
$$\text{Cost per Verified Correct Repair} = \frac{\sum_{j=1}^{N} \text{Cost}_{\text{API}, j}}{\sum_{j=1}^{N} \text{Hidden Correct}_j}$$
Because APIShield prunes invalid repair trajectories early through synthesized invariant verification, it achieves an estimated API cost per verified correct repair of $0.01197, representing a 33.5% reduction in repair cost compared to naive test-driven iterative repair ($0.01800/correct repair under B2).

## Research Questions

Our empirical study answers five core research questions:
- **RQ1 (Impact Localization):** How accurately does APIShield localize affected client integration sites compared to AST traversal and documentation-only matching?
- **RQ2 (End-to-End Correctness):** Does APIShield achieve statistically superior independent hidden correctness compared to competitive baseline approaches?
- **RQ3 (Component Ablation):** What are the individual marginal contributions of structural dependency graphs, semantic overlays, and inferred behavioral invariant checks?
- **RQ4 (Domain Invariant Preservation):** Does APIShield prevent subtle semantic regressions (e.g., currency subunit truncation, idempotency key loss, and routing misdirection) that evade ordinary unit tests?
- **RQ5 (Economic Efficiency):** How does failure-inclusive repair cost scale across ablation treatments when accounting for wasted retries?
