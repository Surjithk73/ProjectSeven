# APIShield synthetic reference manuscript

Every benchmark value in this folder is simulated. No paid AI calls, evaluated repairs, human annotation or GPU measurements produced these artifacts. They illustrate a reporting protocol and must not be presented as executed empirical research.

Start with [the complete Markdown manuscript](APIShield-synthetic-reference-manuscript.md). It contains the abstract, introduction, related work, architecture, benchmark/design, results, ablation study, discussion, validity threats, references and reproduction appendix, with 12 populated tables.

Artifacts:

- synthetic_tasks.csv: 120 controlled task descriptors; 48 are marked for replication.
- synthetic_runs.csv: 3,600 primary plus 1,440 replication task-runs, explicitly flagged synthetic.
- synthetic_summary.json: derived counts, rates, SDs, hierarchical bootstrap intervals and costs.
- simulation_manifest.json: seed, provenance, hypothetical cost assumptions and output hashes.

From the project root, use the project's Python environment to run research/simulation/generate_reference.py and then research/simulation/build_manuscript.py. Both scripts are offline and use the Python standard library.

The primary numerical contrast is full B6 versus test-feedback B2. The generator exposes its treatment probabilities; it is assumption-driven, not calibrated to measured pilot data. Do not interpret its favourable contrasts or confidence intervals as evidence of APIShield superiority. Costs are hypothetical execution-cost scenarios, not current vendor pricing or invoices.

The companion planning report is ../academic-evaluation-report.md. The product's credentials, source code and running server are unchanged by this document task.
