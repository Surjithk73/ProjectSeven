# Inferred OAuth/OIDC & schema invariant check for TASK-IDSCHEMA-004 (tenant_workspace_routing)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/identity/tenant_workspace_routing/task-idschema-004':
            return False
        if o.get('headers', {}).get('Authorization') != 'Bearer ' + d['access_token']:
            return False
        if o.get('headers', {}).get('X-Tenant-Context') != d['tenant_id']:
            return False
        env = o.get('body', {}).get('workspace_session_payload')
        if not isinstance(env, dict) or type(env.get('ttl_seconds')) is not int:
            return False
    return True
