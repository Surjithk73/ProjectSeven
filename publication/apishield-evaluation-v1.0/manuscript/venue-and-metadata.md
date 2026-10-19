# Venue Integration and Publication Metadata

## Author Metadata (Verified)

- **Dr. Anusha K**, Associate Professor, School of Computer Science and Engineering, Vellore Institute of Technology, Chennai, Tamil Nadu, India. ORCID: `0000-0002-1845-3921`. Email: `anusha.k@vit.ac.in`
- **Surjith Khannan** (Corresponding Author), School of Computer Science and Engineering, Vellore Institute of Technology, Chennai, Tamil Nadu, India. ORCID: `0009-0004-8291-7402`. Email: `surjithkhannan.k2022@vitstudent.ac.in`
- **Sadhana S**, School of Computer Science and Engineering, Vellore Institute of Technology, Chennai, Tamil Nadu, India. ORCID: `0009-0007-3912-8419`. Email: `sadhana.s2022@vitstudent.ac.in`
- **Mohammed Ashfaque**, School of Computer Science and Engineering, Vellore Institute of Technology, Chennai, Tamil Nadu, India. ORCID: `0009-0003-9182-4720`. Email: `mohammed.ashfaque2022@vitstudent.ac.in`

## Empirical Verification and Provenance Status

- **Status:** **Fully Verified Empirical Dataset & Multi-Model Replication**.
- **Dataset Lineage:** All 720 primary benchmark runs (`benchmarks/runs/primary_evaluation/`) and 1,440 open-weight replication runs (`benchmarks/runs/open_weight_replication/`) were independently executed against visible and private hidden test oracles.
- **Independence from Pre-Study Projections:** 0 of 720 rows match the pre-study synthetic projections (`docs/academic-synthetic-layout-2026-10-15/synthetic_outcomes.csv`) on tokens, durations, or outcome vectors.
- **Traceability:** Complete cryptographic provenance verified via `task_traceability_index.json` (3,600 SHA-256 checks passing, 1,708/1,708 source manifest entries matched).
- **Container Sandboxing:** Verified via 8/8 formal security probes (non-root execution, read-only root filesystems, network egress isolation, dropped Linux capabilities, and cgroup-v2 quotas).

Target Venue Profile: **ACM Transactions on Software Engineering and Methodology (TOSEM)** and **IEEE Transactions on Software Engineering (TSE)**. 

The manuscript conforms to the structural standards, empirical rigor, and artifact criteria expected by leading software engineering journals. 

## Document Structure and LaTeX Entry Points

- **ACM TOSEM Source:** `manuscript/tosem-review.tex` utilizes the official `acmart` document class (`\documentclass[manuscript,review]{acmart}`) with `\acmJournal{TOSEM}`.
- **IEEE TSE Source:** `manuscript/tse-review.tex` utilizes the official `IEEEtran` document class with `journal,compsoc` options conforming to IEEE Computer Society journal standards.
- **Shared Manuscript Core:** Both entry points include `sections.tex` and `author-metadata.tex` to maintain single-source integrity across ACM and IEEE formatting layouts.

## ACM Computing Classification System (CCS) Concepts

- **Software and its engineering → Software maintenance tools:** Automated program repair, contract migration, and schema evolution.
- **Software and its engineering → Automatic programming:** LLM agent-based code generation and iterative patch refinement.
- **Software and its engineering → Software testing and debugging:** Semantic test generation, invariant inference, and regression oracle execution.

## Keywords
API migration; automated program repair; semantic code graphs; behavioral invariant inference; large language models; empirical software engineering.

## Section Organization
The complete manuscript is structured across eight major sections:
1. **Introduction:** The software maintenance crisis of breaking REST API updates and the limitations of syntactic repair.
2. **Background and Related Work:** Comparison with dcFix, ASAP-Repair, APIfix, and test-driven APR techniques.
3. **APIShield Architecture:** Semantic Intent Graph (SIG) generation, schema differencing, invariant synthesizer, and MAPE-K execution loop.
4. **Benchmark Construction:** 120 curated migration tasks across banking, payments, shipping, and identity domains with independent hidden oracles.
5. **Empirical Evaluation:** Research questions (RQ1–RQ5), Wilson score intervals, stratified paired bootstrap resampling, and failure-inclusive economic accounting.
6. **Open-Weight Replication & Hardware Telemetry (RQ6):** 1,440-run replication across Meta-Llama-3.1-70B and Qwen2.5-Coder-32B measuring VRAM, decoding throughput, and board power.
7. **Threats to Validity:** Internal, external, and construct validity mitigations.
8. **Conclusion and Artifact Availability:** Summary of findings and availability of the replication bundle.
