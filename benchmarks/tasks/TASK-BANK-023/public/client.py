# TASK-BANK-023: Migrate integer account_id to UUID format with validation
def build_request(data):
    return {
        'path': '/v1/banking/account_id_uuid_type/task-bank-023',
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
