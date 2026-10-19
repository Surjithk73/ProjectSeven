# Inferred invariant check for TASK-PAY-009 (merchant_idempotency_v2)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/payment/merchant_idempotency_v2/task-pay-009':
            return False
        blk = o.get('body', {}).get('merchant_charge_v2')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
