# TASK-SHIP-013: Decompose address_line_1 into street_number, route, and unit
def build_request(data):
    return {
        'path': '/v1/logistics/address_component_decomposition/task-ship-013',
        'body': {
            'parcel_id': data['parcel_id'],
            'weight_grams': data['weight_grams'],
            'address_line_1': data['street_address'],
            'carrier': data['carrier_code']
        },
        'headers': {}
    }

def dispatch_package(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
