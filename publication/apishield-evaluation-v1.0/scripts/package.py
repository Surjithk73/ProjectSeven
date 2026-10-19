"""Build a content-verified local review artifact, with complete empirical evidence."""
import argparse
import gzip
import hashlib
import json
import re
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'.venv', 'venv', '__pycache__', '.pytest_cache', '.git', 'models', 'analysis-reproduced'}

def digest(raw):
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'md5': hashlib.md5(raw, usedforsecurity=False).hexdigest(), 'bytes': len(raw)}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--overwrite', action='store_true', help='Allow overwriting existing output archive')
    args = p.parse_args(); args.output = args.output.resolve()
    
    if args.output.exists() and not args.overwrite:
        raise ValueError('Archive already exists. Specify --overwrite to replace.')
    if args.output.is_relative_to(ROOT):
        raise ValueError('Archive must be written outside its own payload')
        
    status = {
        'package_version': '1.0',
        'package_kind': 'curated_benchmark_evaluation_package',
        'curated_benchmark_tasks': 120,
        'benchmark_evaluations': 720,
        'domains': ['Banking', 'Payment', 'Shipping', 'IdentitySchema'],
        'executable_qualification_fixtures': 4,
        'primary_model': 'gemini-3.8-flash',
        'evaluation_mode': 'curated_multi_domain_benchmark',
        'pricing_basis': 'Gemini 3.8 Flash Rate Card ($0.75/1M prompt, $3.75/1M completion)',
        'author_status': 'anonymous_peer_review',
        'license_status': 'open_access_mit',
        'schema_versions': {
            'tasks_manifest': 2,
            'normalized_experiment_record': '2.0'
        }
    }
    (ROOT / 'ARCHIVE_STATUS.json').write_text(json.dumps(status, indent=2) + '\n')
    
    files = []
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE for part in rel.parts): continue
        if path.is_symlink(): raise ValueError('Unexpected symlink: ' + str(rel))
        if not path.is_file() or path.name in {'MANIFEST.json', 'DIRECTORY_MANIFEST.txt'}: continue
        if path.name == '.env' or path.name.startswith('.env.') or path.name == 'service-account.json':
            raise ValueError('Credential-bearing filename disallowed')
        raw = path.read_bytes()
        if re.search(rb'-----BEGIN (?:RSA )?PRIVATE KEY-----\s+[A-Za-z0-9+/=\r\n]{80,}-----END (?:RSA )?PRIVATE KEY-----', raw):
            raise ValueError('Private key material disallowed')
        files.append(path)
        
    listing = sorted([p.relative_to(ROOT).as_posix() for p in files] + ['MANIFEST.json', 'DIRECTORY_MANIFEST.txt'])
    directory = ROOT / 'DIRECTORY_MANIFEST.txt'
    directory.write_text('APIShield-evaluation-v1.0/\n' + '\n'.join('  ' + name for name in listing) + '\n')
    files.append(directory)
    
    records = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in sorted(files)}
    manifest = ROOT / 'MANIFEST.json'
    manifest.write_text(json.dumps({'schema_version': '1.0', 'evidence_status': status['package_kind'],
        'excludes_self': True, 'files': records}, indent=2) + '\n')
    files.append(manifest)
    
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as archive:
                for path in sorted(files):
                    name = 'APIShield-evaluation-v1.0/' + path.relative_to(ROOT).as_posix()
                    info = archive.gettarinfo(str(path), arcname=name)
                    info.uid = info.gid = 0; info.uname = info.gname = ''; info.mtime = 0; info.mode = 0o644
                    with path.open('rb') as source: archive.addfile(info, source)
                    
    with tarfile.open(args.output, 'r:gz') as archive:
        for name, expected in records.items():
            assert digest(archive.extractfile('APIShield-evaluation-v1.0/' + name).read()) == expected, name
            
    observed = digest(args.output.read_bytes())
    for algorithm in ['sha256', 'md5']:
        args.output.with_name(args.output.name + '.' + algorithm).write_text(observed[algorithm] + '  ' + args.output.name + '\n')
    args.output.with_name(args.output.name + '.manifest.json').write_text(json.dumps({
        'archive': args.output.name, **observed, 'payload_files': len(files),
        'internal_manifest': digest(manifest.read_bytes()), 'status': status
    }, indent=2) + '\n')
    
    print(json.dumps({'archive': str(args.output), 'files': len(files), **observed}, indent=2))

if __name__ == '__main__':
    main()
