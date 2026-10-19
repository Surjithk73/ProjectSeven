# TASK-PAY-011: Replace raw token string with payment_method_data dictionary
def build_request(data):
    return {
        'path': '/v1/payment/card_token_to_payment_method/task-pay-011',
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
