# Inferred structural contract check (B6) for TASK-SHIP-009
def check(inputs, outputs):
    return all(o.get('path') == '/v2/logistics/carrier_code_enum_standardization/task-ship-009' and isinstance(o.get('body', {}).get('iso_carrier_dispatch'), dict) and len(o['body']['iso_carrier_dispatch']) >= 2 for o in outputs)
