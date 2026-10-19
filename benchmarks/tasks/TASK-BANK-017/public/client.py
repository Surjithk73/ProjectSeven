# TASK-BANK-017: Migrate integer account_id to UUID format with validation
def build_request(data):
    return {
        'path': '/v1/banking/account_id_uuid_type/task-bank-017',
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
