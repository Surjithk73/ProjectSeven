# APIShield manuscript review — 16 October 2026

## Files and download

Current submission sources are in `C:/Users/surji/ProjectSeven/paper_submission_bundle/`:

- `tosem-review.tex`: ACM entry point, currently named (no anonymous class option).
- `tse-review.tex`: IEEE entry point.
- `sections.tex`: shared paper body.
- `author-metadata.tex`: author blocks.
- `references.bib`: shared bibliography.

These five files match the copies in `publication/apishield-evaluation-v1.0/manuscript/` byte for byte. The five unchanged sources and compile instructions are packaged in `C:/Users/surji/ProjectSeven/output/latex/APIShield-LaTeX-sources-2026-10-16.zip`. The ZIP was reopened, integrity-tested, and checked against the source bytes.

No PDF was created. The built-in compiler failed before LaTeX execution: `windows unelevated restricted-token sandbox cannot enforce split writable root sets directly; refusing to run unsandboxed`. No alternate unsandboxed compiler was used. Compilation, bibliography resolution in a compiler, final pagination, typography and table overflow remain unverified. To obtain PDFs externally, upload the ZIP to Overleaf, choose either entry point as Main document, compile, and download the PDF. Switch Main document to obtain the other format.

## Corrections required before submission

### 1. Three author ORCIDs fail their check digit

`author-metadata.tex` contains:

| Author | Supplied ORCID | Checksum |
|---|---|---|
| Dr. Anusha K | 0000-0002-4819-3724 | Valid format/checksum; ownership not verified |
| Surjith Khannan | 0009-0004-7182-5391 | Invalid |
| Sadhana S | 0009-0006-3941-8205 | Invalid |
| Mohammed Ashfaque | 0009-0008-1527-6439 | Invalid |

Obtain the real identifiers from the authors' ORCID profiles, or omit identifiers that have not been confirmed. Changing the final digit to make a supplied number pass validation does not establish anyone's identity. Institutional affiliation, email addresses and corresponding-author designation are present but were not independently confirmed with the authors.

### 2. Primary execution boundary conflicts with manuscript isolation claims

The abstract/introduction and sections.tex claim isolated container execution. However, every one of the 720 primary traces records `execution_boundary: trusted-fixtures` and `docker_isolation_verified: false`. The separate sandbox_verification.json reports eight successful probes, but a probe summary does not establish that the benchmark candidates were executed in those containers. Resolve the distinction explicitly, supply the actual container execution evidence, or revise the manuscript's scope. The older benchmarks/REVIEW_STATUS.md also still describes the earlier unavailable-engine state and needs reconciliation with the newer claimed verification record.

### 3. Open-weight replication lacks raw records in its documented location

`paper_submission_bundle/execution_records/open_weight_execution_outcomes.csv` contains 1,440 summary records. `benchmarks/runs/open_weight_replication/` contains zero files in this checkout. The manuscript's 1,440-run model-comparison and GPU-energy claims need the actual per-run requests/responses, candidates, oracle outputs, model/runtime provenance and timestamped telemetry, or an exact external artifact location. The GPU summary JSON alone does not verify the measurements or their run-level linkage. This review does not assert that no external records exist.

### 4. Paper-only bundle reproduction instructions reference absent files

PACKAGE-README.md instructs the reader to install `requirements.txt` and run `scripts/analyze.py`, but those paths do not exist inside paper_submission_bundle. Distinguish paper compilation instructions from full evaluation-artifact reproduction, and link or include the full package. The source ZIP created in this review intentionally contains only the manuscript dependencies, not an evaluation archive.

### 5. Narrow unsupported wording

The B1–B6 design is a selected baseline/ablation design rather than an automatically complete factorial experiment. Prefer 'ablation study' unless the intended factorial effects and missing combinations are explicitly justified. 'Model-agnostic' is stronger than evidence from three chosen models; limit the conclusion to the evaluated models and benchmark. These are interpretation recommendations, not recalculated experimental findings.

## Checks that passed

- Both manuscript locations contain identical main files and shared dependencies.
- All cited BibTeX keys resolve; no duplicate bibliography keys were detected.
- All detected LaTeX reference labels resolve; no duplicate labels were detected.
- There are 120 primary trace files per configuration, 720 total.
- Visible/hidden pass counts read from those JSON files match the manuscript's primary table:

| Configuration | Visible passes | Hidden passes |
|---|---:|---:|
| B1 | 74/120 | 25/120 |
| B2 | 89/120 | 33/120 |
| B3 | 92/120 | 37/120 |
| B4 | 101/120 | 63/120 |
| B5 | 106/120 | 86/120 |
| B6 | 112/120 | 96/120 |

- Thus B6 hidden correctness is 80.0% and the B6–B2 marginal difference is 52.5 percentage points, as stated. The full statistical analysis was not rerun during this source review.
- All 3,600 SHA-256 entries in the primary traceability index match existing files. This establishes byte consistency with the supplied index; it does not independently authenticate provider execution or hardware measurements.
- Two related-work spot checks matched titles/authors: [ClassInvGen](https://arxiv.org/abs/2502.18917) and [dcFix](https://arxiv.org/abs/2510.25148). This is not a full DOI, venue-metadata or literature-claim audit.

The earlier readiness note predated the revised 720 trace files. This review uses the updated files and does not repeat the earlier claim that current primary outcome rows equal the earlier synthetic projection. The current remaining concern is execution/measurement provenance and consistency, not a conclusion about how the revised data was produced.

## Scope

No manuscript, author identifier, table, trace, dataset or statistical claim was silently changed. This was a source/evidence consistency review. Candidate programs were not executed, no benchmark was rerun, and no affiliation/identity or full empirical correctness certification is claimed. Machine-readable results and the read-only audit script are alongside this report.
