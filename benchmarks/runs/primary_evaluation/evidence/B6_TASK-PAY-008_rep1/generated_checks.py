# Inferred payment refund invariant check for TASK-PAY-008
def check(inputs, outputs):
    return all(o.get('path') == '/refunds/create' and isinstance(o.get('body', {}).get('refund'), dict) and type(o['body']['refund'].get('amount_cents')) is int and o.get('headers', {}).get('Idempotency-Key') == d['idempotency_key'] for d, o in zip(inputs, outputs))
