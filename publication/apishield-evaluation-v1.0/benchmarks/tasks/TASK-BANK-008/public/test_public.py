def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/banking/iban_bic_restructure/task-bank-008' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('iban_bic_transfer'), dict) for o in outputs)
    }
