# TASK-IDSCHEMA-022: Move tenant_id from URL query string to X-Tenant-Context header
def build_request(data):
    return {
        'path': '/v1/identity/tenant_workspace_routing/task-idschema-022',
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

def get_user_profile(data):
    return build_request(data)

def get_health_status():
    return {'path': '/health', 'status': 'ok'}
