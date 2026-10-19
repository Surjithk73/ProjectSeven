def evaluate(inputs, outputs):
    return {'endpoint': all(o.get('path') == '/labels/create' for o in outputs), 'payload_shape': all(isinstance(o.get('body', {}).get('parcel'), dict) for o in outputs)}
