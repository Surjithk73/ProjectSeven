# Inferred invariant check for TASK-PAY-023 (card_token_to_payment_method)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/payment/card_token_to_payment_method/task-pay-023':
            return False
        blk = o.get('body', {}).get('payment_method_charge')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
