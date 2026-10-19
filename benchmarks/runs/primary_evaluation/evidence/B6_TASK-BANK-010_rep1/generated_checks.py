# Inferred invariant check for TASK-BANK-010 (iso20022_pacs008_wrap)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/banking/iso20022_pacs008_wrap/task-bank-010':
            return False
        blk = o.get('body', {}).get('pacs008_document')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('Idempotency-Key') != d['idempotency_key']:
            return False
    return True
