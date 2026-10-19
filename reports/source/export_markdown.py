"""Export the maintained report as ordinary Markdown with portable image assets."""
from pathlib import Path
import json
import re
import shutil
import zipfile

from docx import Document

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'reports'
SRC = REPORTS / 'source'
OUT = REPORTS / 'APIShield_Project_Report.md'
ASSETS = REPORTS / 'assets'
ASSETS.mkdir(exist_ok=True)
doc = Document(REPORTS / 'APIShield_Project_Report.docx')
paragraphs = doc.paragraphs
title = doc.core_properties.title

# The front matter is read from the delivered DOCX, including its current abstract.
front = ['# ' + title, '']
for p in paragraphs:
    value = p.text.strip()
    if value == 'PROJECT REPORT':
        break
    if not value or value == 'A project report on' or p.style.name == 'Title':
        continue
    front.extend([value.replace('\n', '  \n'), ''])
front.extend(['![Institution logo](assets/institution_logo.jpg)', ''])
active = False
for p in paragraphs:
    value = p.text.strip()
    if value == 'DECLARATION':
        active = True
    if value == 'TABLE OF CONTENTS':
        break
    if not active or not value:
        continue
    if p.style.name == 'Front Heading':
        front.extend(['## ' + value.title(), ''])
    else:
        front.extend([value.replace('\n', '  \n'), ''])

refs = json.loads((SRC/'references.json').read_text(encoding='utf-8'))
reference_lines = []
for ref in refs:
    line = f"{ref['author']} ({ref['year']}). *{ref['title']}*. {ref['type']}."
    url = ref['url']
    if url.startswith('http'):
        line += f' [Source]({url}).'
    else:
        line += ' ProjectSeven repository: ' + '; '.join('`' + p.strip() + '`' for p in url.split(';')) + '.'
    reference_lines.extend([line, ''])

lines = (SRC/'report.md').read_text(encoding='utf-8').splitlines()
out = front
figures = []
tables = 0
i = 0
inserted_references = False
while i < len(lines):
    line = lines[i]
    if line == '<!-- PAGE -->':
        i += 1
        continue
    if line.startswith('[[TABLE:'):
        parts = line[len('[[TABLE:'):-2].split('|')
        number, caption, *headers = parts
        out.extend([f'**Table {number}. {caption}**', '', '| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |'])
        i += 1
        while lines[i] != '[[ENDTABLE]]':
            cells = lines[i].split('|')
            assert len(cells) == len(headers), (number, cells)
            out.append('| ' + ' | '.join(cells) + ' |')
            i += 1
        out.append('')
        tables += 1
    elif line.startswith('[[FIGURE:'):
        number, caption, kind = line[len('[[FIGURE:'):-2].split('|')
        filename = f'figure_{kind}.png'
        shutil.copy2(REPORTS/'.qa'/filename, ASSETS/filename)
        out.extend([f'![Figure {number}. {caption}](assets/{filename})', '', f'*Figure {number}. {caption}*', ''])
        figures.append(filename)
    elif line == '[[CODE]]':
        out.extend(['', '```json' if i + 1 < len(lines) and lines[i+1].strip() == '{' else '```text'])
    elif line == '[[ENDCODE]]':
        out.extend(['```', ''])
    elif line.startswith('[[REFERENCES:'):
        if not inserted_references:
            out.extend(reference_lines)
            inserted_references = True
    else:
        out.append(line)
    i += 1

shutil.copy2(REPORTS/'.qa/institution_logo.jpg', ASSETS/'institution_logo.jpg')
content = '\n'.join(out)
content = re.sub(r'^# (CHAPTER|APPENDIX) (\d+)\n# ([^\n]+)', lambda m: '# ' + m[1].title() + ' ' + m[2] + ' ' + m[3], content, flags=re.M)
content = re.sub(r'\n{3,}', '\n\n', content).rstrip() + '\n'
assert '[[' not in content
assert tables == 31 and len(figures) == 7 and len(refs) == 27
for relative in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', content):
    assert (REPORTS/relative).is_file(), relative
OUT.write_text(content, encoding='utf-8')

readme = REPORTS/'MARKDOWN_README.md'
readme.write_text('''# APIShield Markdown report

Open APIShield_Project_Report.md in any Markdown editor. Keep the assets folder next to it so all seven diagrams and the institution logo render. Tables, references, front matter and the current abstract are included as ordinary Markdown.

Markdown does not preserve Word page breaks, page numbers, margins, signatures or automatic contents fields. The DOCX remains the formatted academic submission version.

The diagrams are already included. Current application screenshots have not been captured for this report. Personal details, real signatures, submission details and a target venue remain to be completed. Appendix 4 contains an intentionally reusable run-record form; its bracketed fields are form fields, not claims that the existing diagnostics lack all metadata. See EVIDENCE_NEEDED.md for the remaining empirical study records.

Maintained prose is source/report.md; front matter and formatting are in source/build_report.py. This Markdown is an export, and edits to it do not automatically update the DOCX. Recreate the export using the bundled Python runtime and source/export_markdown.py after updating the maintained sources and DOCX.
''', encoding='utf-8')
bundle = REPORTS/'APIShield_Markdown_Bundle.zip'
with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in [OUT, readme, REPORTS/'EVIDENCE_NEEDED.md', *[ASSETS/name for name in figures], ASSETS/'institution_logo.jpg']:
        archive.write(p, p.relative_to(REPORTS).as_posix())
print(json.dumps({'markdown':str(OUT),'bundle':str(bundle),'figures':len(figures),'logo':1,'tables':tables,'references':len(refs),'words':len(content.split())}, indent=2))
