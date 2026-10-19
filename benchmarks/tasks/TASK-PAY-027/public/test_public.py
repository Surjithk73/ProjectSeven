def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/payment/merchant_idempotency_v2/task-pay-027' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('merchant_charge_v2'), dict) for o in outputs)
    }
