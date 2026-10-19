# Inferred invariant check for TASK-BANK-001 (amount_cents_to_currency_object)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/banking/amount_cents_to_currency_object/task-bank-001':
            return False
        blk = o.get('body', {}).get('currency_transfer')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
