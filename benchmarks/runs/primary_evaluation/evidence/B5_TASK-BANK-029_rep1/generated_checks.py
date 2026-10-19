# Inferred structural contract check (B5) for TASK-BANK-029
def check(inputs, outputs):
    return all(o.get('path') == '/v2/banking/account_id_uuid_type/task-bank-029' and isinstance(o.get('body', {}).get('uuid_transfer'), dict) and len(o['body']['uuid_transfer']) >= 2 for o in outputs)
