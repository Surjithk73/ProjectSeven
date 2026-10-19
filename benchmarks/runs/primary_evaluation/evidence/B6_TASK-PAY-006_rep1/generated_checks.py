# Inferred invariant check for TASK-PAY-006 (webhook_signature_header)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/payment/webhook_signature_header/task-pay-006':
            return False
        blk = o.get('body', {}).get('signed_webhook_event')
        if not isinstance(blk, dict) or type(blk.get('amount_subunits')) is not int:
            return False
        if o.get('headers', {}).get('X-Nexus-Signature') != d['idempotency_key']:
            return False
    return True
