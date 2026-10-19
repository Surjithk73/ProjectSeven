# Inferred structural contract check (B5) for TASK-PAY-011
def check(inputs, outputs):
    return all(o.get('path') == '/v2/payment/card_token_to_payment_method/task-pay-011' and isinstance(o.get('body', {}).get('payment_method_charge'), dict) and len(o['body']['payment_method_charge']) >= 2 for o in outputs)
