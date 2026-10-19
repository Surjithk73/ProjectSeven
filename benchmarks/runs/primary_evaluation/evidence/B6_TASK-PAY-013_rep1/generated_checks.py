# Inferred structural contract check (B6) for TASK-PAY-013
def check(inputs, outputs):
    return all(o.get('path') == '/v2/payment/charge_to_payment_intent/task-pay-013' and isinstance(o.get('body', {}).get('payment_intent'), dict) and len(o['body']['payment_intent']) >= 2 for o in outputs)
