def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/banking/iso20022_pacs008_wrap/task-bank-016' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('pacs008_document'), dict) for o in outputs)
    }
