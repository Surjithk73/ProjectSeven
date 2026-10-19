# TASK-SHIP-015: Standardize proprietary carrier codes to ISO carrier codes
def build_request(data):
    return {
        'path': '/v1/logistics/carrier_code_enum_standardization/task-ship-015',
        'body': {
            'parcel_id': data['parcel_id'],
            'weight_grams': data['weight_grams'],
            'address_line_1': data['street_address'],
            'carrier': data['carrier_code']
        },
        'headers': {}
    }

def book_courier(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
