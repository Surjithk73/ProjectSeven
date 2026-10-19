"""Trusted evaluator container: receives data, never imports candidate code."""
import importlib.util
import json
import sys

payload = json.load(sys.stdin)
spec = importlib.util.spec_from_file_location('oracle', '/oracle.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
try:
    checks = module.evaluate(payload['inputs'], payload['outputs'])
    if not isinstance(checks, dict) or not checks or any(type(v) is not bool for v in checks.values()):
        raise ValueError('Expected nonempty boolean assertions')
except (KeyError, TypeError, IndexError):
    checks = {'oracle_contract': False}
print(json.dumps(checks))
