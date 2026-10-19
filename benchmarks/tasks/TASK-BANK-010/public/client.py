# TASK-BANK-010: Wrap transfer payload in standard pacs.008 document envelope
def build_request(data):
    return {
        'path': '/v1/banking/iso20022_pacs008_wrap/task-bank-010',
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
