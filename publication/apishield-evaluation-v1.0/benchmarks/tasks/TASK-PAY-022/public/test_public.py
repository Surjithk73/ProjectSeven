def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/payment/split_fee_nesting/task-pay-022' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('transfer_data_split'), dict) for o in outputs)
    }
