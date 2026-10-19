# Inferred structural contract check (B5) for TASK-IDSCHEMA-022
def check(inputs, outputs):
    return all(o.get('path') == '/v2/identity/tenant_workspace_routing/task-idschema-022' and isinstance(o.get('body', {}).get('workspace_session_payload'), dict) and len(o['body']['workspace_session_payload']) >= 2 for o in outputs)
