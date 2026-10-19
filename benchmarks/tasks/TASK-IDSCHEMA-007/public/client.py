# TASK-IDSCHEMA-007: Migrate Authorization: Token to Authorization: Bearer with RFC 6750 schema
def build_request(data):
    return {
        'path': '/v1/identity/oauth_bearer_auth_migration/task-idschema-007',
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
