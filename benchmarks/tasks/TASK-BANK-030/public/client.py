# TASK-BANK-030: Split recipient_name into given_name and family_name
def build_request(data):
    return {
        'path': '/v1/banking/beneficiary_name_structure/task-bank-030',
        'body': {
            'amount_cents': data['amount_cents'],
            'source': data['source'],
            'destination': data['destination'],
            'legacy_token': data['extra_token']
        },
        'headers': {}
    }

def execute_debit(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
