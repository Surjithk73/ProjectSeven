def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/logistics/dimensions_nesting_object/task-ship-028' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('parcel_dimensions_box'), dict) for o in outputs)
    }
