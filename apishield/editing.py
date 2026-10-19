"""Validate all replacements before atomically changing permitted source files."""
import ast
import difflib
from pathlib import Path
import re
import stat

from .configuration import relative_path
from .jobs import _atomic_bytes


def apply_candidate(workspace: Path, candidate: dict, allowed_files: set[str]) -> dict:
    if not isinstance(candidate, dict) or set(candidate) - {'patches', 'needs_input'}:
        raise ValueError('Candidate must contain only patches and optional needs_input')
    patches = candidate.get('patches')
    if not isinstance(patches, list) or not patches:
        raise ValueError('Candidate must contain nonempty patches')
    originals, replacements, modes = {}, {}, {}
    root = Path(workspace).resolve()
    for patch in patches:
        if not isinstance(patch, dict) or set(patch) != {'file', 'old_code_snippet', 'new_code_snippet'}:
            raise ValueError('Each patch requires file and exact old/new code snippets')
        name = relative_path(patch['file'])
        path = root / name
        parts = Path(name).parts
        if name not in allowed_files or path.suffix != '.py' or any(part.casefold() in {'test', 'tests', '.git'} for part in parts) or path.name in {'conftest.py', 'setup.py'} or path.name.startswith('test_') or path.name.endswith('_test.py'):
            raise ValueError('Patches may target only impacted configured Python source, never tests/config/contracts')
        if path.is_symlink() or root not in path.resolve().parents or not path.is_file():
            raise ValueError('Unsafe patch target')
        old, new = patch['old_code_snippet'], patch['new_code_snippet']
        if not isinstance(old, str) or not old or not isinstance(new, str) or old == new:
            raise ValueError('Empty or no-op replacement')
        if name not in originals:
            originals[name] = path.read_bytes().decode('utf-8')
            modes[name] = stat.S_IMODE(path.stat().st_mode)
        source = originals[name]
        starts = [match.start() for match in re.finditer('(?=' + re.escape(old) + ')', source)]
        if len(starts) != 1:
            raise ValueError('Old snippet must match exactly once in the pinned source')
        start, end = starts[0], starts[0] + len(old)
        spans = replacements.setdefault(name, [])
        if any(start < previous_end and end > previous_start for previous_start, previous_end, _ in spans):
            raise ValueError('Overlapping candidate replacements')
        spans.append((start, end, new))
    updated = {}
    for name, spans in replacements.items():
        source = originals[name]
        for start, end, replacement in sorted(spans, reverse=True):
            source = source[:start] + replacement + source[end:]
        try:
            ast.parse(source, filename=name)
        except SyntaxError as exc:
            raise ValueError(f'Candidate produces invalid Python: {exc}') from exc
        if source == originals[name]:
            raise ValueError('Candidate has no source change')
        updated[name] = source
    patch_text = ''
    for name in sorted(updated):
        before, after = originals[name], updated[name]
        # Git patches need explicit markers for source files without trailing LF.
        lines = list(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
            fromfile='a/' + name, tofile='b/' + name, lineterm='\n'))
        for line in lines:
            patch_text += line if line.endswith('\n') else line + '\n\\ No newline at end of file\n'
        _atomic_bytes(root / name, after.encode('utf-8'))
        (root / name).chmod(modes[name])
    return {'patch': patch_text, 'files': sorted(updated)}
