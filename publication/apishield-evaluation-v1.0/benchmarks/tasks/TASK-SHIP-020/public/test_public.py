def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/logistics/metric_weight_conversion/task-ship-020' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('metric_parcel_weight'), dict) for o in outputs)
    }
