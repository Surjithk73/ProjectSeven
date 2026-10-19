def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/payment/card_token_to_payment_method/task-pay-023' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('payment_method_charge'), dict) for o in outputs)
    }
