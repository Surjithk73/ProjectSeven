# TASK-IDSCHEMA-027: Flatten nested claims object to top-level attributes in response parser
def build_request(data):
    return {
        'path': '/v1/identity/user_profile_claim_flattening/task-idschema-027',
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
