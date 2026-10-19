# Inferred invariant check for TASK-BANK-002 (iban_bic_restructure)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/banking/iban_bic_restructure/task-bank-002':
            return False
        blk = o.get('body', {}).get('iban_bic_transfer')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
