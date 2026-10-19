def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/identity/mfa_challenge_response_wrap/task-idschema-030' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('verification_token_envelope'), dict) for o in outputs)
    }
