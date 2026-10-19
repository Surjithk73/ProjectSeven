def build_request(data):
    return {'path': '/labels', 'body': {'weight_grams': data['weight_grams']}, 'headers': {}}
