"""Choose the supported elevated sandbox without changing permission profiles."""
from datetime import datetime
from pathlib import Path
import re
import shutil
import tomllib


def main():
    path = Path.home() / '.codex/config.toml'
    original = path.read_bytes()
    text = original.decode('utf-8')
    expected = tomllib.loads(text)
    if expected.get('windows', {}).get('sandbox') != 'unelevated':
        raise ValueError('Unexpected sandbox setting; no change made')
    section = re.search(r'(?ms)^\[windows\][^\r\n]*\r?\n(.*?)(?=^\[|\Z)', text)
    if not section:
        raise ValueError('Windows section not found; no change made')
    block, count = re.subn(r'(?m)^(sandbox\s*=\s*)"unelevated"', r'\1"elevated"', section.group(1))
    if count != 1:
        raise ValueError('Ambiguous sandbox setting; no change made')
    updated = text[:section.start(1)] + block + text[section.end(1):]
    expected['windows']['sandbox'] = 'elevated'
    assert tomllib.loads(updated) == expected
    backup = path.with_name('config.toml.before-latex-sandbox-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    if backup.exists():
        raise ValueError('Backup already exists; no change made')
    shutil.copy2(path, backup)
    path.write_bytes(updated.encode('utf-8'))
    assert tomllib.loads(path.read_text()) == expected
    print('Changed only windows.sandbox: unelevated -> elevated')
    print('Backup: ' + str(backup))


if __name__ == '__main__':
    main()
