# TASK-PAY-027: Preserve caller idempotency hash across automatic network retry headers
def build_request(data):
    return {
        'path': '/v1/payment/merchant_idempotency_v2/task-pay-027',
        'body': {
            'amount_cents': data['amount_cents'],
            'source': data['source'],
            'destination': data['destination'],
            'legacy_token': data['extra_token']
        },
        'headers': {}
    }

def authorize_payment(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
