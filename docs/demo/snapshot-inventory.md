# Current-project snapshot inventory

Prepared on 2026-10-19 for the user's requested publication to `Surjithk73/ProjectSeven`.

The snapshot preserves the existing application, examples, tests, launchers, design records, manuscript sources, research/benchmark files, reports, and small media already present in the working directory. These files are preserved as authored; publication is not a claim that research results or manuscript assertions have been independently verified.

The existing ignore rules exclude the local Python environment, frontend dependencies/builds, `.env`, APIShield runtime data, local backups, logs, the downloaded oasdiff executable, benchmark model weights, and benchmark working environments. The managed Google service-account credential is outside this repository under the user's private APIShield settings directory and is not part of the snapshot.

An inventory of roughly 12,000 candidate paths found no individual file above 10 MiB. The largest groups were benchmarks (about 34 MiB), reports (about 14 MiB), and publication artifacts (about 7 MiB). Existing runtime/test fixtures are included only where they are already normal project evidence rather than ignored private state. The literal private-key marker in `tests/test_local_runtime.py` belongs to a synthetic exclusion test and is not a private key.

The feature plan and design at `docs/superpowers/plans/2026-10-19-two-machine-movie-demo.md` and `docs/superpowers/specs/2026-10-19-two-machine-movie-demo-design.md` are proposals awaiting review. Their presence does not mean the new demo has been implemented.

The actual resulting commit ID and remote verification are reported after publication, rather than fabricated in advance or embedded self-referentially in this snapshot. Upload verification and CI/test execution are separate checks.

Prepublication `git diff --cached --check` reported 2,849 whitespace findings in the existing accumulated files, including context lines in retained golden unified patches. They are preserved in this archival snapshot rather than normalizing experiment inputs and invalidating recorded hashes. This check is therefore not reported as passing. The credential-shape scan matched only the synthetic private-key marker test; no ignored `.env`, dependency directory, private backup or APIShield runtime directory appeared in the staged inventory. No full application test run was performed as part of this preservation-only upload.

Final clone-portability inspection found a nested Git checkout under `reports/banking-repair-verification-2026-10-15/_examples/banking`. Its tracked and untracked non-ignored files are preserved in sibling `banking-verification-snapshot.zip`, without its `.git` directory. The original local checkout remains untouched and is ignored by the parent repository; the nonportable gitlink is removed from the published tree.
