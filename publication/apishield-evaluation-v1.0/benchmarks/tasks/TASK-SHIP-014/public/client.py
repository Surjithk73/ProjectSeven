# TASK-SHIP-014: Migrate package weight from pounds (lbs) to grams (g)
def build_request(data):
    return {
        'path': '/v1/logistics/metric_weight_conversion/task-ship-014',
        'body': {
            'parcel_id': data['parcel_id'],
            'weight_grams': data['weight_grams'],
            'address_line_1': data['street_address'],
            'carrier': data['carrier_code']
        },
        'headers': {}
    }

def generate_label(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
