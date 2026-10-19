# Inferred OAuth/OIDC & schema invariant check for TASK-IDSCHEMA-009 (user_profile_claim_flattening)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/identity/user_profile_claim_flattening/task-idschema-009':
            return False
        if o.get('headers', {}).get('Authorization') != 'Bearer ' + d['access_token']:
            return False
        if o.get('headers', {}).get('X-Tenant-Context') != d['tenant_id']:
            return False
        env = o.get('body', {}).get('flattened_principal_claims')
        if not isinstance(env, dict) or type(env.get('ttl_seconds')) is not int:
            return False
    return True
