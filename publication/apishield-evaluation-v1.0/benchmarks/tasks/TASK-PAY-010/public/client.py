# TASK-PAY-010: Nest application_fee_amount inside transfer_data object
def build_request(data):
    return {
        'path': '/v1/payment/split_fee_nesting/task-pay-010',
        'body': {
            'amount_cents': data['amount_cents'],
            'source': data['source'],
            'destination': data['destination'],
            'legacy_token': data['extra_token']
        },
        'headers': {}
    }

def refund_charge(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
