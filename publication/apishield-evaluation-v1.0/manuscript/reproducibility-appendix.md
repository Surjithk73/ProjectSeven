# Artifact and Reproducibility Appendix

## Artifact Scope and Availability

The complete evaluation artifact is packaged as `APIShield-evaluation-v1.0.tar.gz`. The artifact contains the primary 120-task multi-domain benchmark dataset, the automated evaluation harness, the independent hidden oracle suites, analysis scripts, and replication environments conforming to ACM/IEEE Artifact Review and Badging guidelines.

The archive contents are completely enumerated in `DIRECTORY_MANIFEST.txt` and cryptographically hashed in `MANIFEST.json`. Every payload file includes SHA-256 and MD5 checksum records and byte size specifications. Adjacent cryptographic checksum sidecars (`.sha256` and `.md5`) verify archive integrity.

## Directory and Evidence Structure

The archive unpacks into `APIShield-evaluation-v1.0/` with the following directory organization:

| Directory / File | Contents and Description |
|---|---|
| `README.md` | Reproduction instructions, environment requirements, and replication workflows |
| `ARCHIVE_STATUS.json` | Package metadata, model configurations, and benchmark profiles |
| `schemas/` | Standardized JSON schemas for benchmark task specifications and evaluation execution traces |
| `data/benchmarks/` | Complete 120-task primary execution records and financial invariant evaluation logs |
| `data/observed/` | Direct model inference traces, including prompt-completion pairs and raw diff outputs |
| `data/qualification/` | Author-curated qualification fixtures for testing the execution sandbox and test runner |
| `benchmarks/tasks/` | Runnable public client migration tasks, original API contracts, and V2 specifications |
| `benchmarks/evaluator_private/` | Isolated hidden behavioral assertion suites and invariant oracles, strictly separated from prompt context |
| `benchmarks/harness/` | Autonomous evaluation runners, Docker sandboxing containers, and metric aggregation tools |
| `benchmarks/profiles/` | Model profile definitions, rate cards, and sampling parameters |
| `apishield/` | Core APIShield engine: Semantic Intent Graph (SIG) builder, AST parser, and MAPE-K controller |
| `scripts/` | End-to-end analysis scripts, statistical bootstrap runners, and artifact packaging tools |
| `analysis/` | Computed empirical tables (`tables.md`), CSV comparisons, and summary JSON metrics |
| `manuscript/` | Full ACM TOSEM and IEEE TSE camera-ready LaTeX sources and master sections |
| `references/` | BibTeX bibliography containing complete digital object identifiers (DOIs) |

## Exact Reproduction Commands

The replication package runs under Python 3.11+ and POSIX or Windows environments. Candidate evaluation executes inside network-isolated Docker containers to prevent external state leakage.

```bash
# 1. Extract archive
tar -xzf APIShield-evaluation-v1.0.tar.gz
cd APIShield-evaluation-v1.0

# 2. Set up clean Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Verify environment and cryptographic payload integrity
python scripts/verify_environment.py

# 4. Recompute all empirical benchmark tables and statistical contrasts
python scripts/analyze.py --output analysis-reproduced

# 5. Verify exact numerical identity against published results
diff -u analysis/comparison.csv analysis-reproduced/comparison.csv
diff -u analysis/metrics.json analysis-reproduced/metrics.json

# 6. Rebuild complete manuscript sections and LaTeX tables
python scripts/build_manuscript.py
```
