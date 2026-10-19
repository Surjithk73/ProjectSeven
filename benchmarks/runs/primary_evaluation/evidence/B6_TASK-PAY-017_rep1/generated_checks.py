# Inferred structural contract check (B6) for TASK-PAY-017
def check(inputs, outputs):
    return all(o.get('path') == '/v2/payment/card_token_to_payment_method/task-pay-017' and isinstance(o.get('body', {}).get('payment_method_charge'), dict) and len(o['body']['payment_method_charge']) >= 2 for o in outputs)
