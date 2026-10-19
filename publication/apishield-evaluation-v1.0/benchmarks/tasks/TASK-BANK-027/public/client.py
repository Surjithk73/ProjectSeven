# TASK-BANK-027: Move idempotency_key from request body to X-Idempotency-Key HTTP header
def build_request(data):
    return {
        'path': '/v1/banking/idempotency_header_enforcement/task-bank-027',
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
