def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/identity/scopes_list_to_bitmask/task-idschema-017' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('structured_permissions'), dict) for o in outputs)
    }
