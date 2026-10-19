def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/logistics/carrier_code_enum_standardization/task-ship-003' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('iso_carrier_dispatch'), dict) for o in outputs)
    }
