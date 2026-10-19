# TASK-PAY-024: Change webhook header from Stripe-Signature to X-Nexus-Signature
def build_request(data):
    return {
        'path': '/v1/payment/webhook_signature_header/task-pay-024',
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
