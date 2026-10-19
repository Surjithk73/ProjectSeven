# Inferred OAuth/OIDC & schema invariant check for TASK-IDSCHEMA-018 (mfa_challenge_response_wrap)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/identity/mfa_challenge_response_wrap/task-idschema-018':
            return False
        if o.get('headers', {}).get('Authorization') != 'Bearer ' + d['access_token']:
            return False
        if o.get('headers', {}).get('X-Tenant-Context') != d['tenant_id']:
            return False
        env = o.get('body', {}).get('verification_token_envelope')
        if not isinstance(env, dict) or type(env.get('ttl_seconds')) is not int:
            return False
    return True
