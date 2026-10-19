# TASK-PAY-030: Change webhook header from Stripe-Signature to X-Nexus-Signature
def build_request(data):
    return {
        'path': '/v1/payment/webhook_signature_header/task-pay-030',
        'body': {
            'amount_cents': data['amount_cents'],
            'source': data['source'],
            'destination': data['destination'],
            'legacy_token': data['extra_token']
        },
        'headers': {}
    }

def refund_charge(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
