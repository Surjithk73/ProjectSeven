def evaluate(inputs, outputs):
    return {'endpoint': all(o.get('path') == '/refunds/create' for o in outputs), 'payload_shape': all(isinstance(o.get('body', {}).get('refund'), dict) for o in outputs)}
