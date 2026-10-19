def evaluate(inputs, outputs):
    return {'endpoint': all(o.get('path') == '/transfers' for o in outputs), 'payload_shape': all(isinstance(o.get('body', {}).get('amount'), dict) for o in outputs)}
