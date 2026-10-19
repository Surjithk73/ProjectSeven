# Inferred invariant check for TASK-PAY-019 (charge_to_payment_intent)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/payment/charge_to_payment_intent/task-pay-019':
            return False
        blk = o.get('body', {}).get('payment_intent')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
