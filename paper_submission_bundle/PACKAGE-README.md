# APIShield Evaluation v1.0 — Curated Benchmark & Replication Package

This package contains the complete curated benchmark evaluation dataset, task specifications, analysis scripts, model outputs, and publication sources for:

> **APIShield: Intent-Aware Self-Healing for Breaking REST API Migrations via Semantic Graphs and Behavioral Invariant Synthesis**  
> *Targeted for ACM Transactions on Software Engineering and Methodology (TOSEM) / IEEE Transactions on Software Engineering (TSE)*

## Core Research Contents

- **Authors & Affiliation:** Dr. Anusha K, Surjith Khannan (Corresponding Author), Sadhana S, Mohammed Ashfaque (School of Computer Science and Engineering, Vellore Institute of Technology, Chennai, India). Defined in `author-metadata.tex`.
- **Master Manuscript:** `MASTER-SECTIONS.md` and `sections.tex` contain the complete paper sections covering RQ1–RQ6.
- **Publication Tables:** `tables.md` contains the 7 empirical comparison tables (Table 1: Primary Benchmark & Factorial Ablation, Table 2: Paired Contrasts & Effect Sizes, Table 3: Financial Invariant Preservation, Table 4: Change Detection & Localization, Table 5: Open-Weight Replication & Hardware Telemetry, Table 6: Observed Live SDK Diagnostics, Table 7: Container Sandbox Verification).
- **LaTeX Sources:** `tosem-review.tex` (ACM TOSEM format) and `tse-review.tex` (IEEE TSE format) including `sections.tex`, `author-metadata.tex`, and `references.bib`.
- **Curated Benchmark Records:**
  - `execution_records/benchmark_execution_outcomes.csv`: 720 benchmark evaluations across B1–B6 (Gemini 3.8 Flash) covering 120 curated tasks.
  - `execution_records/open_weight_execution_outcomes.csv`: 1,440 replication evaluations across Meta-Llama-3.1-70B and Qwen2.5-Coder-32B.
  - `execution_records/financial_invariant_evaluations.csv`: 360 financial invariant records evaluating minor units, idempotency keys, and routing integrity.
  - `execution_records/gpu_telemetry_summary.json`: Detailed GPU board power, VRAM peak, decoding throughput, and energy measurements.
  - `execution_records/task_traceability_index.json`: Cryptographic mapping from all 720 runs to individual patches, logs, and prompt tokens (3,600 SHA-256 checks verified).
- **Task Manifest:** `tasks_manifest.json` specifies all 120 benchmark migration tasks across Banking, Payment, Shipping, and Identity domains with complete endpoint mappings.

## Execution and Replication Instructions

```bash
# 1. Set up virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Recompute all benchmark tables and bootstrap contrasts
python scripts/analyze.py --output analysis

# 3. Compile LaTeX manuscript
pdflatex tosem-review.tex
bibtex tosem-review
pdflatex tosem-review.tex
```
