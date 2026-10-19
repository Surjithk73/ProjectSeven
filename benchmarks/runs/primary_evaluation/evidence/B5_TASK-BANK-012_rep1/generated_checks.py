# Inferred invariant check for TASK-BANK-012 (beneficiary_name_structure)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/banking/beneficiary_name_structure/task-bank-012':
            return False
        blk = o.get('body', {}).get('beneficiary_transfer')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
