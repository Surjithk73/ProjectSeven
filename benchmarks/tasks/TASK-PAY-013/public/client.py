# TASK-PAY-013: Migrate legacy /v1/charges payload to /v2/payment_intents state machine
def build_request(data):
    return {
        'path': '/v1/payment/charge_to_payment_intent/task-pay-013',
        'body': {
            'amount_cents': data['amount_cents'],
            'source': data['source'],
            'destination': data['destination'],
            'legacy_token': data['extra_token']
        },
        'headers': {}
    }

def capture_intent(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
