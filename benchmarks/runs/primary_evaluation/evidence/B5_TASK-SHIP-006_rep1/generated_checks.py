# Inferred logistics invariant check for TASK-SHIP-006 (tracking_endpoint_path_migration)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/logistics/tracking_endpoint_path_migration/task-ship-006':
            return False
        pkg = o.get('body', {}).get('shipment_milestone_envelope')
        if not isinstance(pkg, dict) or type(pkg.get('weight_grams')) is not int:
            return False
        if pkg.get('parcel_id') != d['parcel_id'] or o.get('headers', {}).get('X-Shipment-Idempotency') != d['idempotency_key']:
            return False
    return True
