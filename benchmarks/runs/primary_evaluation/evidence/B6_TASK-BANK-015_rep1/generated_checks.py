# Inferred banking invariant check for TASK-BANK-015
def check(inputs, outputs):
    return all(o.get('path') == '/transfers' and isinstance(o.get('body', {}).get('amount'), dict) and type(o['body']['amount'].get('value')) is int and o.get('headers', {}).get('Idempotency-Key') == d['idempotency_key'] for d, o in zip(inputs, outputs))
