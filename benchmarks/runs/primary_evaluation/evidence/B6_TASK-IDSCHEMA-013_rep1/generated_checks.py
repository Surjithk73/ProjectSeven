# Inferred OAuth/OIDC & schema invariant check for TASK-IDSCHEMA-013 (oauth_bearer_auth_migration)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/identity/oauth_bearer_auth_migration/task-idschema-013':
            return False
        if o.get('headers', {}).get('Authorization') != 'Bearer ' + d['access_token']:
            return False
        if o.get('headers', {}).get('X-Tenant-Context') != d['tenant_id']:
            return False
        env = o.get('body', {}).get('rfc6750_auth_context')
        if not isinstance(env, dict) or type(env.get('ttl_seconds')) is not int:
            return False
    return True
