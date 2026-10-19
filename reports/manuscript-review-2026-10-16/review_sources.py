"""Read manuscript sources and retained evidence; never execute candidate code."""
import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'paper_submission_bundle'
OUTPUT = Path(__file__).parent


def valid_orcid(value):
    digits = value.replace('-', '')
    total = 0
    for char in digits[:15]:
        total = (total + int(char)) * 2
    checksum = (12 - total % 11) % 11
    return digits[-1] == ('X' if checksum == 10 else str(checksum))


def main():
    names = ['tosem-review.tex', 'tse-review.tex', 'sections.tex', 'author-metadata.tex', 'references.bib']
    texts = {name: (SOURCE / name).read_text(encoding='utf-8') for name in names}
    latex = '\n'.join(texts[name] for name in names if name.endswith('.tex'))
    labels = re.findall(r'\\label\{([^}]+)\}', latex)
    refs = re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}', latex)
    citations = set(k.strip() for group in re.findall(r'\\cite\w*\{([^}]+)\}', latex) for k in group.split(','))
    bibkeys = re.findall(r'@\w+\{([^,]+),', texts['references.bib'])
    ids = sorted(set(re.findall(r'\d{4}-\d{4}-\d{4}-[\dX]{4}', texts['author-metadata.tex'])))
    traces = [json.loads(path.read_text()) for path in (ROOT / 'benchmarks/runs/primary_evaluation').glob('B*.json')]
    boundaries = Counter(trace.get('execution_boundary', 'not_recorded') for trace in traces)
    counts = {}
    for config in sorted({trace['configuration'] for trace in traces}):
        subset = [trace for trace in traces if trace['configuration'] == config]
        counts[config] = {'runs': len(subset), 'visible_passes': sum(trace.get('visible_test_exit_code') == 0 for trace in subset),
                          'hidden_passes': sum(trace.get('hidden_oracle_exit_code') == 0 for trace in subset)}
    index = json.loads((SOURCE / 'execution_records/task_traceability_index.json').read_text())
    hashes_verified, hash_failures = 0, []
    for record in index['records']:
        for key, value in record.items():
            if key.endswith('_path') and key[:-5] + '_sha256' in record:
                path = ROOT / value
                expected = record[key[:-5] + '_sha256']
                if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected:
                    hashes_verified += 1
                else:
                    hash_failures.append(value)
    original_root = ROOT / 'publication/apishield-evaluation-v1.0/manuscript'
    report = {
        'source_folder': str(SOURCE),
        'source_copies_match': {name: (SOURCE / name).read_bytes() == (original_root / name).read_bytes() for name in names},
        'missing_citation_keys': sorted(citations - set(bibkeys)),
        'duplicate_bibliography_keys': [key for key, n in Counter(bibkeys).items() if n > 1],
        'missing_reference_labels': sorted(set(refs) - set(labels)),
        'duplicate_labels': [label for label, n in Counter(labels).items() if n > 1],
        'orcid_checksums': {value: valid_orcid(value) for value in ids},
        'primary_trace_counts': counts,
        'primary_execution_boundaries': dict(boundaries),
        'primary_docker_verified_records': sum(trace.get('docker_isolation_verified') is True for trace in traces),
        'traceability_hashes_verified': hashes_verified,
        'traceability_hash_failures': hash_failures,
        'open_weight_raw_files_in_documented_directory': sum(path.is_file() for path in (ROOT / 'benchmarks/runs/open_weight_replication').rglob('*')),
        'open_weight_summary_rows': len(list(csv.DictReader((SOURCE / 'execution_records/open_weight_execution_outcomes.csv').open()))),
        'pdf_compilation': 'BLOCKED: built-in compiler refused execution because Windows restricted-token sandbox could not enforce split writable root sets',
        'pdf_visual_review': 'Not performed; no PDF was produced',
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / 'source-audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    export = ROOT / 'output/latex'
    export.mkdir(parents=True, exist_ok=True)
    archive = export / 'APIShield-LaTeX-sources-2026-10-16.zip'
    instructions = '''APIShield LaTeX source package

Upload this ZIP as a new Overleaf project. Select tosem-review.tex for ACM TOSEM,
or tse-review.tex for IEEE TSE, as the main document. Compile with pdfLaTeX and
BibTeX (Overleaf normally handles the required repeat passes), then Download PDF.

The five source files are unchanged copies from paper_submission_bundle.
Both templates need sections.tex, author-metadata.tex and references.bib.
This ZIP is source only; no PDF compilation or rendered-layout validation was
possible in this session. See the separate manuscript review before submission.
'''
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name in names:
            bundle.write(SOURCE / name, name)
        bundle.writestr('README-compile.txt', instructions)
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert all(bundle.read(name) == (SOURCE / name).read_bytes() for name in names)
    print(json.dumps({**report, 'download_zip': str(archive)}, indent=2))


if __name__ == '__main__':
    main()
