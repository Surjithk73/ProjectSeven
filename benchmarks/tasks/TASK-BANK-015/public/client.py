def build_request(data):
    return {'path': '/transfers', 'body': {'amount_cents': data['amount_cents']}, 'headers': {}}
