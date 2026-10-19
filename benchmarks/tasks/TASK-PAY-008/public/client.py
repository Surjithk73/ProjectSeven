def build_request(data):
    return {'path': '/refunds', 'body': {'transaction_id': data['transaction_id']}, 'headers': {}}
