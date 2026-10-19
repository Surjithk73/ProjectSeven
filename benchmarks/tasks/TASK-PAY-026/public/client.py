# TASK-PAY-026: Ensure zero-decimal currencies (JPY) vs two-decimal currencies (USD/EUR) avoid float truncation
def build_request(data):
    return {
        'path': '/v1/payment/currency_minor_units_enforcement/task-pay-026',
        'body': {
            'amount_cents': data['amount_cents'],
            'source': data['source'],
            'destination': data['destination'],
            'legacy_token': data['extra_token']
        },
        'headers': {}
    }

def create_charge(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
