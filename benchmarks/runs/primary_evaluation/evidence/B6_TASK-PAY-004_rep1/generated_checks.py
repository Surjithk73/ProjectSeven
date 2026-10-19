# Inferred invariant check for TASK-PAY-004 (split_fee_nesting)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/payment/split_fee_nesting/task-pay-004':
            return False
        blk = o.get('body', {}).get('transfer_data_split')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
