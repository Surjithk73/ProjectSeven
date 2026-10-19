def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/logistics/tracking_endpoint_path_migration/task-ship-030' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('shipment_milestone_envelope'), dict) for o in outputs)
    }
