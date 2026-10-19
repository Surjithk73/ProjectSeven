def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/payment/charge_to_payment_intent/task-pay-001' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('payment_intent'), dict) for o in outputs)
    }
