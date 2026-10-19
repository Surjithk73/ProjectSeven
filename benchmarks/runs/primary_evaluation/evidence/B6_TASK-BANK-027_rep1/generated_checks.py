# Inferred invariant check for TASK-BANK-027 (idempotency_header_enforcement)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/banking/idempotency_header_enforcement/task-bank-027':
            return False
        blk = o.get('body', {}).get('idempotent_transfer')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
