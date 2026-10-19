# TASK-SHIP-024: Migrate /v1/tracking/shipments/{id} to /v2/shipments/{id}/milestones
def build_request(data):
    return {
        'path': '/v1/logistics/tracking_endpoint_path_migration/task-ship-024',
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
