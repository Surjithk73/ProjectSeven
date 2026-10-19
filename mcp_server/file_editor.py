"""Validated local edits, with one transaction across all affected files."""
import ast
import io
from pathlib import Path
import tokenize

try:
    from fastmcp import FastMCP
    mcp = FastMCP('File Editor Server')
except ImportError:
    mcp = None

CLIENT_ROOT = Path(__file__).resolve().parents[1] / 'client_app'


def resolve_client_file(file_path: str) -> Path:
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError('A file path is required')
    path = Path(file_path).resolve()
    if not path.is_relative_to(CLIENT_ROOT.resolve()) or not path.is_file():
        raise ValueError('Security violation: target must be an existing file inside client_app')
    return path


def read_source(path: Path) -> str:
    raw = path.read_bytes()
    encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
    return raw.decode(encoding).replace('\r\n', '\n').replace('\r', '\n')


def apply_patch_group(plans: list[dict]) -> str:
    originals = {}
    candidates = {}
    try:
        if not plans:
            raise ValueError('At least one patch is required')
        grouped = {}
        for plan in plans:
            if not isinstance(plan, dict):
                raise ValueError('Patch must be an object')
            path = resolve_client_file(plan.get('file'))
            grouped.setdefault(path, []).append(plan)
        for path, edits in grouped.items():
            raw = path.read_bytes()
            originals[path] = raw
            encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
            content = read_source(path)
            ranges = []
            for edit in edits:
                old, new = edit.get('old_code_snippet'), edit.get('new_code_snippet')
                if not isinstance(old, str) or not isinstance(new, str) or not old.strip() or not new.strip():
                    raise ValueError('Old and new snippets must be nonempty strings')
                if old == new:
                    raise ValueError('No-op patch is not allowed')
                locations = []
                position = content.find(old)
                while position >= 0:
                    locations.append(position)
                    position = content.find(old, position + 1)
                if len(locations) != 1:
                    raise ValueError('Old snippet must match exactly once in the original file')
                start = locations[0]
                end = start + len(old)
                if any(start < other_end and other_start < end for other_start, other_end, _ in ranges):
                    raise ValueError('Overlapping patches are not allowed')
                ranges.append((start, end, new))
            updated = content
            for start, end, new in sorted(ranges, reverse=True):
                updated = updated[:start] + new + updated[end:]
            if updated == content:
                raise ValueError('No-op patch is not allowed')
            if path.suffix == '.py':
                ast.parse(updated, filename=str(path))
            newline = '\r\n' if b'\r\n' in raw else '\n'
            candidates[path] = updated.replace('\n', newline).encode(encoding)
        for path, raw in candidates.items():
            path.write_bytes(raw)
        return f'Successfully patched {len(candidates)} file(s)'
    except Exception as exc:
        for path, raw in originals.items():
            path.write_bytes(raw)
        return f'Error applying patch: {exc}'


def apply_patch(file_path: str, old_code_snippet: str, new_code_snippet: str) -> str:
    return apply_patch_group([{'file': file_path, 'old_code_snippet': old_code_snippet, 'new_code_snippet': new_code_snippet}])


if mcp is not None:
    # Register without rebinding; some FastMCP versions return a Tool object.
    mcp.tool()(apply_patch)

if __name__ == '__main__' and mcp is not None:
    mcp.run()
