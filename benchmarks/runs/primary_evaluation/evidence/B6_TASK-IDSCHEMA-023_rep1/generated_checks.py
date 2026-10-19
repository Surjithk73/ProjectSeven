# Inferred structural contract check (B6) for TASK-IDSCHEMA-023
def check(inputs, outputs):
    return all(o.get('path') == '/v2/identity/scopes_list_to_bitmask/task-idschema-023' and isinstance(o.get('body', {}).get('structured_permissions'), dict) and len(o['body']['structured_permissions']) >= 2 for o in outputs)
