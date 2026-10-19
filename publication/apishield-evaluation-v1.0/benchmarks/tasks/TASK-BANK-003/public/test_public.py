def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/banking/idempotency_header_enforcement/task-bank-003' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('idempotent_transfer'), dict) for o in outputs)
    }
