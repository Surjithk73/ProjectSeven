# Inferred logistics invariant check for TASK-SHIP-022 (dimensions_nesting_object)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/logistics/dimensions_nesting_object/task-ship-022':
            return False
        pkg = o.get('body', {}).get('parcel_dimensions_box')
        if not isinstance(pkg, dict) or type(pkg.get('weight_grams')) is not int:
            return False
        if pkg.get('parcel_id') != d['parcel_id'] or o.get('headers', {}).get('X-Shipment-Idempotency') != d['idempotency_key']:
            return False
    return True
