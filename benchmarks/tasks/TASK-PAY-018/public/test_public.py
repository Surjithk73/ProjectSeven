def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/payment/webhook_signature_header/task-pay-018' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('signed_webhook_event'), dict) for o in outputs)
    }
