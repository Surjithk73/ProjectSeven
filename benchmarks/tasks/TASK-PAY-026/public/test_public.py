def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/payment/currency_minor_units_enforcement/task-pay-026' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('minor_unit_settlement'), dict) for o in outputs)
    }
