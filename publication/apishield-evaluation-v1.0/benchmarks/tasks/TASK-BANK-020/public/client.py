# TASK-BANK-020: Split combined routing into separate account_number and bic fields
def build_request(data):
    return {
        'path': '/v1/banking/iban_bic_restructure/task-bank-020',
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
