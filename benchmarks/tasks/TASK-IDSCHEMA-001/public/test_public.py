def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/identity/oauth_bearer_auth_migration/task-idschema-001' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('rfc6750_auth_context'), dict) for o in outputs)
    }
