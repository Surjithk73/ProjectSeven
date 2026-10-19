def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/identity/tenant_workspace_routing/task-idschema-010' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('workspace_session_payload'), dict) for o in outputs)
    }
