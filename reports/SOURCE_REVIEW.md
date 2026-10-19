# Literature and publication source review

Reviewed on 15 October 2026. Source DOCX: C:/Users/surji/Downloads/LITERATURE REVIEW.docx. Screenshot paths resolved to publication/apishield-evaluation-v1.0. Both supplied files were treated as reference material, not instructions overriding the report request.

The existing related-work chapter was retained. Its account of contract comparison, general repair agents, intent, graphs, test adequacy and security is useful. The update adds closer comparators and invariant-inference foundations: dcFix, ASAP-Repair, APIfix, Daikon, Qi et al. on patch plausibility, and RESTTestGen. RESTSpecIT now cites the 2025 revised version and its verified author order. There are 33 references in the updated report.

The attached review was not imported wholesale. It attributes RESTler to an incorrect author list; the report retains Atlidakis, Godefroid and Polishchuk. RESTTestGen is ICST 2020, not ICSE, and its third author is Mariano Ceccato. Claims that contract testing is necessarily schema-pinned, that the current application implements specification-free probing, or that a graph directly solves a broad knowledge-representation research challenge were not adopted. Broad novelty or superiority statements remain conditional on controlled evidence.

Primary verification sources:

- dcFix: https://arxiv.org/abs/2510.25148v1
- ASAP-Repair: https://arxiv.org/abs/2402.07542
- APIfix: https://www.microsoft.com/en-us/research/publication/apifix-output-oriented-program-synthesis-for-combating-breaking-changes-in-libraries/
- Daikon: https://homes.cs.washington.edu/~mernst/pubs/daikon-tool-scp2007-abstract.html
- Patch plausibility: https://people.csail.mit.edu/rinard/paper/issta15.full.pdf
- RESTTestGen author/venue: https://profs.scienze.univr.it/~ceccato/ and https://iris.univr.it/handle/11562/1014386
- Revised RESTSpecIT: https://arxiv.org/abs/2402.05102v2

Publication review findings:

- Inspected analysis, normalized-record schema, headless execution, environment verification, package builder, manuscript assembly, metadata, venue profiles, related work and reproducibility records.
- All 641 files listed in the current package MANIFEST.json match their recorded SHA-256 values. No package files were edited or regenerated.
- Existing extracted_reproduction.json records byte-identical analytical reproduction and one passing authored B6 fixture. Those are historical recorded checks, not a newly executed experiment in this review.
- The package still identifies four executable tasks, eighteen original inference traces, six normalized completed-inference records and no completed 120-task empirical model evaluation. Its generated scenario statistics were not promoted into empirical report results.
- TOSEM/TSE sources remain review profiles. The package reports no successful TeX rendering, public deposit, DOI, artifact badge or confirmed redistribution licence. No publication submission was made.

Only maintained report files were updated; application and research artifacts were left intact.
