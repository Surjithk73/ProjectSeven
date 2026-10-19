# TASK-PAY-002: Ensure zero-decimal currencies (JPY) vs two-decimal currencies (USD/EUR) avoid float truncation
def build_request(data):
    return {
        'path': '/v1/payment/currency_minor_units_enforcement/task-pay-002',
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
