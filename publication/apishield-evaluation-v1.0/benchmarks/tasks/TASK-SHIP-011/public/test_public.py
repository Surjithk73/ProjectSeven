def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/logistics/hazmat_declaration_subschema/task-ship-011' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('hazmat_shipping_declaration'), dict) for o in outputs)
    }
