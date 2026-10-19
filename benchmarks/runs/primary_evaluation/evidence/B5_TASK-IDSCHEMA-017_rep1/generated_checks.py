# Inferred OAuth/OIDC & schema invariant check for TASK-IDSCHEMA-017 (scopes_list_to_bitmask)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/identity/scopes_list_to_bitmask/task-idschema-017':
            return False
        if o.get('headers', {}).get('Authorization') != 'Bearer ' + d['access_token']:
            return False
        if o.get('headers', {}).get('X-Tenant-Context') != d['tenant_id']:
            return False
        env = o.get('body', {}).get('structured_permissions')
        if not isinstance(env, dict) or type(env.get('ttl_seconds')) is not int:
            return False
    return True
