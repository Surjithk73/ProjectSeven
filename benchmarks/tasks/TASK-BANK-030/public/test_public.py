def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/banking/beneficiary_name_structure/task-bank-030' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('beneficiary_transfer'), dict) for o in outputs)
    }
