# Inferred OAuth/OIDC & schema invariant check for TASK-IDSCHEMA-020 (pagination_cursor_migration)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/identity/pagination_cursor_migration/task-idschema-020':
            return False
        if o.get('headers', {}).get('Authorization') != 'Bearer ' + d['access_token']:
            return False
        if o.get('headers', {}).get('X-Tenant-Context') != d['tenant_id']:
            return False
        env = o.get('body', {}).get('cursor_page_request')
        if not isinstance(env, dict) or type(env.get('ttl_seconds')) is not int:
            return False
    return True
