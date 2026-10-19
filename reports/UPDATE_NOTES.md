# Maintaining the APIShield project report

Primary master from 15 October 2026: `APIShield_Project_Report.tex`. Edit the LaTeX directly. The DOCX and Markdown are retained historical exports; do not regenerate them from the old Markdown after editing the LaTeX. See `LATEX_README.md`.

The previous DOCX workflow below is archival and applies only to that snapshot.

The report is an individual final-project report that will be updated while the implementation develops. Personal information, signatures and submission date remain placeholders. The external-guide certificate is omitted pending confirmation of applicability. Written template requirements override its inconsistent sample geometry and numbering. Arabic centered page fields are used throughout.

Source of prose: `source/report.md`. Formatting and front matter: `source/build_report.py`. Verified APA reference data: `source/references.json`. Provenance and output summary: `source/report_manifest.json`. Template contract: `source/artifact.md`.

For a future update:

1. Inspect source changes and newer validation records. Do not overwrite unrelated application files or the university template.
2. Update relevant architecture, method and capability statements in Chapters 3–5. Update Chapter 6 only from actual dated evidence, preserving separate cohorts and their limitations.
3. Chapter 7 now incorporates the executable four-task harness, the tooling_qualification_20261015 cohort and the three live inference passes. Its five tables describe implemented configurations, actual authored-candidate qualification, named invariant failures, third-pass live resources and API estimates. They are not the five projection tables in docs/academic-synthetic-layout-2026-10-15. Keep authored fixture results separate from model effectiveness; all retained live candidates lack independent evaluation. The 120-task model study remains incomplete. `EVIDENCE_NEEDED.md` records the remaining inputs. Update literature and contribution statements only when new evidence supports them.
4. Keep the conclusion, abstract, traceability appendix and references consistent with the changed scope. Retain the distinction between static observations, declarations, AI interpretation and executed checks.
5. Preserve manual edits made to the DOCX. Before rebuilding, compare it with the maintained source and incorporate completed personal details and reviewer edits; the builder otherwise replaces the output.
6. Run the builder using the bundled runtime, refresh native Word fields and render all pages with `source/render_report.py --iteration vN`. Inspect every page and check for table overflow, split captions, reference wrapping, stale page numbers and the 65–75-page target.

Report creation did not run application tests, make model requests, read private credentials or change remote repositories. Historical counts are not fresh validation of the current working tree. QA images/PDFs under `.qa/` are intermediates, not requested deliverables.

The literature/publication review is documented in `SOURCE_REVIEW.md`. It retains the existing chapter, adds six verified sources, updates RESTSpecIT to its 2025 revision and records the local versioned package's schema, tooling and payload verification. The attached literature DOCX and publication package remain unchanged.

Bundled Python path used for artifact work:
`C:/Users/surji/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.

The packaged LibreOffice renderer was attempted and failed because LibreOffice is unavailable. Word 16 was available and supplies field refresh and PDF export; PyMuPDF supplies page images. Do not install or substitute a desktop office suite merely for rendering.
