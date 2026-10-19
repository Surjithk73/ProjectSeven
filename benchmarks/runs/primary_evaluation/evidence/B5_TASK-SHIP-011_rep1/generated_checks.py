# Inferred structural contract check (B5) for TASK-SHIP-011
def check(inputs, outputs):
    return all(o.get('path') == '/v2/logistics/hazmat_declaration_subschema/task-ship-011' and isinstance(o.get('body', {}).get('hazmat_shipping_declaration'), dict) and len(o['body']['hazmat_shipping_declaration']) >= 2 for o in outputs)
