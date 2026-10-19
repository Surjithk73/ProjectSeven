# Inferred invariant check for TASK-BANK-029 (account_id_uuid_type)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/banking/account_id_uuid_type/task-bank-029':
            return False
        blk = o.get('body', {}).get('uuid_transfer')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
