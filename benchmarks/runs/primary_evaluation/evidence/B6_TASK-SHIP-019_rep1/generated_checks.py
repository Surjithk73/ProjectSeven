# Inferred structural contract check (B6) for TASK-SHIP-019
def check(inputs, outputs):
    return all(o.get('path') == '/v2/logistics/address_component_decomposition/task-ship-019' and isinstance(o.get('body', {}).get('structured_address_manifest'), dict) and len(o['body']['structured_address_manifest']) >= 2 for o in outputs)
