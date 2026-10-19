def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/banking/amount_cents_to_currency_object/task-bank-025' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('currency_transfer'), dict) for o in outputs)
    }
