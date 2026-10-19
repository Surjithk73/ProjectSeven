# TASK-IDSCHEMA-012: Wrap 2FA verification challenge in verification_token envelope
def build_request(data):
    return {
        'path': '/v1/identity/mfa_challenge_response_wrap/task-idschema-012',
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
