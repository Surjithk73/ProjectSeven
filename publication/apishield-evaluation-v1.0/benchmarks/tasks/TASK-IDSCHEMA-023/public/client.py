# TASK-IDSCHEMA-023: Convert space-separated OAuth scope string to structured permission object list
def build_request(data):
    return {
        'path': '/v1/identity/scopes_list_to_bitmask/task-idschema-023',
        'body': {
            'subject_id': data['subject_id'],
            'tenant_id': data['tenant_id'],
            'scopes': data['scope_str'],
            'ttl': data['ttl_seconds']
        },
        'headers': {
            'Authorization': 'Token ' + data['access_token']
        }
    }

def exchange_token(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
