# TASK-IDSCHEMA-014: Migrate page/per_page offset query parameters to next_cursor/limit
def build_request(data):
    return {
        'path': '/v1/identity/pagination_cursor_migration/task-idschema-014',
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

def introspect_token(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
