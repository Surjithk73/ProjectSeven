# Inferred structural contract check (B5) for TASK-IDSCHEMA-024
def check(inputs, outputs):
    return all(o.get('path') == '/v2/identity/mfa_challenge_response_wrap/task-idschema-024' and isinstance(o.get('body', {}).get('verification_token_envelope'), dict) and len(o['body']['verification_token_envelope']) >= 2 for o in outputs)
