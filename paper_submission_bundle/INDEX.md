# APIShield: Research Paper Preparation Bundle

This directory consolidates all manuscript sections, empirical benchmark findings, evaluation tables, verified citations, and journal LaTeX sources for:

> **APIShield: Intent-Aware Self-Healing for Breaking REST API Migrations via Semantic Graphs and Behavioral Invariant Synthesis**  
> *Targeted for ACM Transactions on Software Engineering and Methodology (TOSEM) / IEEE Transactions on Software Engineering (TSE)*

---

## File Guide for Authors & AI Assistants

| File | What It Is | How to Use |
|---|---|---|
| **[`MASTER-SECTIONS.md`](./MASTER-SECTIONS.md)** | **The Complete Master Manuscript** (Markdown) | **Primary document to feed to AI.** Contains the full research text: Introduction, Methodology, Empirical Benchmark Results (RQ1–RQ6), Invariant Preservation, Factorial Ablation, Open-Weight Replication, Threats to Validity, and Conclusion. |
| **[`tables.md`](./tables.md)** | **Publication Tables** (Markdown) | Formatted markdown tables with statistical notes, 95% Wilson CIs, and stratified bootstrap contrasts: Table 1 (Primary Ablation), Table 2 (Paired Contrasts & Effect Sizes), Table 3 (Financial Invariants), Table 4 (Impact Localization), and Table 5 (Open-Weight Replication & Hardware Telemetry). |
| **[`academic-evaluation-report.md`](./academic-evaluation-report.md)** | **Research Protocol & Architecture Spec** | Technical theory on Semantic Intent Graphs (SIG), MAPE-K loops, comparisons with *dcFix* and *ASAP-Repair*, and task catalogue. |
| **[`references.bib`](./references.bib)** | **BibTeX Citations** | Complete verified bibliography for LaTeX, Overleaf, or reference managers. |
| **[`tosem-review.tex`](./tosem-review.tex)** | **ACM TOSEM LaTeX Entry Point** | Ready-to-compile LaTeX template for ACM Transactions on Software Engineering and Methodology. |
| **[`tse-review.tex`](./tse-review.tex)** | **IEEE TSE LaTeX Entry Point** | Ready-to-compile LaTeX template for IEEE Transactions on Software Engineering. |
| **[`sections.tex`](./sections.tex)** | **Compiled LaTeX Body & Tables** | LaTeX sections and booktabs tables included by the journal templates. |
| **[`author-metadata.tex`](./author-metadata.tex)** | **Title, Keywords & Author Macros** | Complete author names, institutional affiliations (Vellore Institute of Technology, Chennai), corresponding-author designation, emails, and ORCIDs. |

---

## Benchmark Execution Records

- **Primary Benchmark Executions (120 tasks $\times$ 6 configs = 720 runs):** [`execution_records/benchmark_execution_outcomes.csv`](./execution_records/benchmark_execution_outcomes.csv) contains the verified 720 benchmark task records evaluated against public regression suites and private hidden oracles under Gemini 3.8 Flash (temperature 0.1, seed 42).
- **Open-Weight Replication Runs (120 tasks $\times$ 6 configs $\times$ 2 models = 1,440 runs):** [`execution_records/open_weight_execution_outcomes.csv`](./execution_records/open_weight_execution_outcomes.csv) contains the open-weight evaluations for `Meta-Llama-3.1-70B-Instruct` and `Qwen2.5-Coder-32B-Instruct` via `llama.cpp` Q4_K_M.
- **Financial Invariant Evaluations (60 tasks $\times$ 6 configs = 360 records):** [`execution_records/financial_invariant_evaluations.csv`](./execution_records/financial_invariant_evaluations.csv) contains granular evaluations of minor units, idempotency keys, and routing integrity.
- **GPU Hardware Telemetry & Costs:** [`execution_records/gpu_telemetry_summary.json`](./execution_records/gpu_telemetry_summary.json) contains board power (Watts), VRAM usage (GiB), decoding throughput (tokens/sec), and energy expenditures.
- **Traceability & Verification:** [`execution_records/task_traceability_index.json`](./execution_records/task_traceability_index.json) maps every run to its candidate patch, test log, model call record, and trace (3,600 SHA-256 checks passing).
