# Inferred structural contract check (B5) for TASK-IDSCHEMA-015
def check(inputs, outputs):
    return all(o.get('path') == '/v2/identity/user_profile_claim_flattening/task-idschema-015' and isinstance(o.get('body', {}).get('flattened_principal_claims'), dict) and len(o['body']['flattened_principal_claims']) >= 2 for o in outputs)
