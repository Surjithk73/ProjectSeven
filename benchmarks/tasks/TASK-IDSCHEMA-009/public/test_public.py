def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/identity/user_profile_claim_flattening/task-idschema-009' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('flattened_principal_claims'), dict) for o in outputs)
    }
