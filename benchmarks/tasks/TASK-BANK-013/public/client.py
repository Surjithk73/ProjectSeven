# TASK-BANK-013: Convert flat amount_cents (int) to nested amount object {value: int, currency: str}
def build_request(data):
    return {
        'path': '/v1/banking/amount_cents_to_currency_object/task-bank-013',
        'body': {
            'amount_cents': data['amount_cents'],
            'source': data['source'],
            'destination': data['destination'],
            'legacy_token': data['extra_token']
        },
        'headers': {}
    }

def process_wire(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
