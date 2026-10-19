# TASK-PAY-009: Preserve caller idempotency hash across automatic network retry headers
def build_request(data):
    return {
        'path': '/v1/payment/merchant_idempotency_v2/task-pay-009',
        'body': {
            'amount_cents': data['amount_cents'],
            'source': data['source'],
            'destination': data['destination'],
            'legacy_token': data['extra_token']
        },
        'headers': {}
    }

def submit_transaction(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
