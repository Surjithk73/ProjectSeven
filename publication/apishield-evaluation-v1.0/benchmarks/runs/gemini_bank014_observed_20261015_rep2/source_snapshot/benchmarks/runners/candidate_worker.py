"""Candidate-side protocol. No hidden oracle or reference patch is mounted here."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import client

inputs = json.load(sys.stdin)
outputs = [client.build_request(item) for item in inputs]
checks_ok = True
if Path('generated_checks.py').exists():
    import generated_checks
    checks_ok = bool(generated_checks.check(inputs, outputs))
print(json.dumps({'outputs': outputs, 'generated_checks_pass': checks_ok}, ensure_ascii=True))
