# Inferred structural contract check (B5) for TASK-IDSCHEMA-005
def check(inputs, outputs):
    return all(o.get('path') == '/v2/identity/scopes_list_to_bitmask/task-idschema-005' and isinstance(o.get('body', {}).get('structured_permissions'), dict) and len(o['body']['structured_permissions']) >= 2 for o in outputs)
