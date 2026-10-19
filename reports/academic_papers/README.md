# APIShield research manuscript variants

Prepared 16 October 2026. These are author-review drafts, separate from the college report.

## Entry points

- `ieee_conference/APIShield_IEEE_Conference.tex`: generic IEEEtran conference draft, eight-page working budget.
- `ieee_access/APIShield_IEEE_Access.tex`: expanded IEEE Access draft, eleven pages including author-biography placeholders.
- Each directory contains its matching compiled PDF and required figure assets.
- `shared/` contains the maintained scientific sections, bibliography, aggregate-plot script and copies of the two supplied analysis CSVs.

The text is shared to keep methods and numerical reporting consistent. `\ifAccess` selects journal-only expansions. Edit the shared sections for scientific changes, and the entry points for title, abstract, author details and publisher-specific settings. Both outputs must be rebuilt after a shared edit. Do not rerun the historical college-report builders over these files.

## Layout and prose revision

Both entry points explicitly select two-column body text. Wide architecture diagrams, comparison tables and the paired correctness/cost figure span both columns; the Access title, abstract and keywords retain the template's full-width front matter. Reference-column breaks use IEEEtran's native mechanism. The short Access biography placeholders are kept together to avoid page-height stretching.

The architecture has been redrawn at a larger size, the SIG fragment enlarged, and the crowded benchmark/accounting table split into readable tables. Both papers now show correctness and cost side by side. Repeated procedural commentary has been removed or consolidated into the validity and reproducibility sections. The supplied outcome counts and intervals remain unchanged.

## Build

Keep the directory structure intact. Compile from the relevant entry-point directory. With Tectonic:

```text
cd ieee_conference
tectonic -X compile APIShield_IEEE_Conference.tex
```

```text
cd ieee_access
tectonic -X compile APIShield_IEEE_Access.tex
```

The PDFs delivered here were built with the Codex application's bundled Tectonic engine and visually inspected. These are multi-file projects with local class/font assets, so use a project-capable LaTeX compiler. A standalone editor that uploads only the entry-point text may not resolve the included files.

For Overleaf, upload the complete source bundle, choose the entry-point file as the main document and compile as a project. The source also retains the template's pdfLaTeX path; local pdfLaTeX compilation was not separately tested.

`shared/make_figures.py` rebuilds the supplied-aggregate plots with matplotlib and NumPy. It runs no experiments or inference. The two architectural figures are native TikZ in `shared/method.tex`. The application screenshot is an unchanged copy of the previously supplied Tests and Intent capture, cropped during typesetting. It is explicitly separated from benchmark evidence.

## Format provenance

The conference uses IEEEtran 1.8b, obtained from CTAN. The Access style uses the bundled IEEE Access class, fonts and logos distributed through a public template mirror. The current official ZIP URL returned HTTP 403 during preparation; its URL and the mirror asset hashes are retained in `shared/template_provenance.json`. Confirm the current official template release before final submission.

`ieeeaccess.original.cls` preserves the downloaded class. The working class has limited compatibility corrections: equivalent CMYK blue under XeTeX in place of pdfTeX-only spot-color primitives, independent abstract/title length registers, a fitted abstract gutter, and zero-width footer overlays that do not emit spurious overflow warnings. The footer identifies an author-review draft rather than inventing a publication volume/year. The entry point restores the TeX year primitive for TikZ and fixes the Access paper size consistently across pages. The changes are recorded in `shared/ieeeaccess_compatibility.patch`.

## Evidence and writing scope

The papers analyze the author-supplied 120-task/six-treatment release. They do not assert new experiments or independent authentication of historical execution. Numerical tables preserve the supplied aggregate values. Descriptive factorial contrasts and cost interpretations are identified as derived quantities. The text distinguishes curated request builders from sampled industrial repositories, generated checks from private oracles, and cost per correct repair from cost per attempted task.

Original prose was drafted and revised using the requested humanizer skill. Literature is cited, and the papers include AI-assistance disclosure. No commercial similarity/plagiarism score was measured, and no score is guaranteed. See `AUTHOR_COMPLETION.md` for the fields and review decisions still needed.

These are alternative versions of the same study. They are not independent studies suitable for simultaneous duplicate submission. If a conference version is published first, the journal submission needs a substantively justified extension, citation/disclosure of the conference paper and compliance with the selected journal's overlap policy.
