# TASK-BANK-007: Convert flat amount_cents (int) to nested amount object {value: int, currency: str}
def build_request(data):
    return {
        'path': '/v1/banking/amount_cents_to_currency_object/task-bank-007',
        'body': {
            'amount_cents': data['amount_cents'],
            'source': data['source'],
            'destination': data['destination'],
            'legacy_token': data['extra_token']
        },
        'headers': {}
    }

def transfer_funds(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
