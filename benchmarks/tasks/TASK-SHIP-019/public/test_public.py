def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/logistics/address_component_decomposition/task-ship-019' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('structured_address_manifest'), dict) for o in outputs)
    }
