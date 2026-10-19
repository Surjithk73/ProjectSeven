# Inferred structural contract check (B6) for TASK-SHIP-006
def check(inputs, outputs):
    return all(o.get('path') == '/v2/logistics/tracking_endpoint_path_migration/task-ship-006' and isinstance(o.get('body', {}).get('shipment_milestone_envelope'), dict) and len(o['body']['shipment_milestone_envelope']) >= 2 for o in outputs)
