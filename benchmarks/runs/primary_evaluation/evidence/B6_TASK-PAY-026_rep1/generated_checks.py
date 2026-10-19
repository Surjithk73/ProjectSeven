# Inferred invariant check for TASK-PAY-026 (currency_minor_units_enforcement)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/payment/currency_minor_units_enforcement/task-pay-026':
            return False
        blk = o.get('body', {}).get('minor_unit_settlement')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
