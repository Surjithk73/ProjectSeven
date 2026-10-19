# APIShield report master

Edit `APIShield_Project_Report.tex` directly. It is authoritative. The earlier DOCX, Markdown, reference JSON and conversion scripts are historical inputs; do not rerun them over later LaTeX edits.

The report contains eight chapters, six appendices, 35 tables, seven inline TikZ diagrams, eight application screenshots and 33 references. Keep `assets/` alongside the master, including the university logo and screenshots. Original screenshots are unchanged; detail views are cropped by graphicx during typesetting.

Open the existing source in Codex for live compilation and PDF preview. External compilation uses XeLaTeX with Times New Roman; compile enough times to resolve contents and lists. The source also supplies a Times-compatible fallback for other systems. Body text, table cells and code are set to 12 pt Times New Roman. Captions may be smaller, above the required 10 pt minimum. Appendix hyperlink anchors are unique.

The inspected PDF is 86 pages as of 16 October 2026, within the user's below-100-page limit. All pages were visually inspected; pages affected by the final humanizer pass were checked again. The final pass simplified 36 passages without changing numerical values, tables, code, citations, paths or personal placeholders. The built-in compiler reports success. The source bundle includes the master and required image assets. Local QA PDFs, logs and page renders remain under `.qa/final-latex/`.

Personal/institutional details, signatures, seals and submission dates remain for the user to complete. Recheck compilation and pagination after filling them. TOSEM and TSE are candidate publication venues; this report retains university formatting. Experimental results supplied and edited by the user have not been independently re-executed during formatting.

Pagination: cover, title, declaration and certificate are unnumbered. Abstract is i, followed by Acknowledgement ii, contents iii-v, figures vi, tables vii-viii and abbreviations ix. Chapter 1 resets to Arabic 1. Contents entries begin at Abstract and include Acknowledgement and all lists. APPENDICES is a parent entry with six indented children in both contents and PDF bookmarks. Footers are centered under the content area (6.35 mm right of physical page center), as requested. The reference list uses numbered [1]. entries, regular text and justified flat paragraphs; each entry stays on one page. Code and unscaled diagram labels use 12 pt Times New Roman. All table cells use the body one-and-a-half spacing setting.

The default opening pages remain in each export. The user intends to replace them manually: cover/title/declaration/certificate are physical pages 1-4; Abstract is physical page 5 and Acknowledgement is physical page 6. Preserve Abstract when replacing the other pages, and retain ii on the replacement Acknowledgement.

Table 1.1 has its caption and explanatory paragraph together above the data rows. Reference list formatting follows the user-provided numbered example; bibliographic facts and in-text author-year citations are retained.
