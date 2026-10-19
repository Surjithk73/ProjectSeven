def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/banking/account_id_uuid_type/task-bank-011' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('uuid_transfer'), dict) for o in outputs)
    }
