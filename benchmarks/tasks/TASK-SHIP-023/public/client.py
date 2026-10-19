# TASK-SHIP-023: Add required hazardous_materials boolean and classification code
def build_request(data):
    return {
        'path': '/v1/logistics/hazmat_declaration_subschema/task-ship-023',
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
