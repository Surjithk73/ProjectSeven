# Inferred logistics invariant check for TASK-SHIP-007 (address_component_decomposition)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/logistics/address_component_decomposition/task-ship-007':
            return False
        pkg = o.get('body', {}).get('structured_address_manifest')
        if not isinstance(pkg, dict) or type(pkg.get('weight_grams')) is not int:
            return False
        if pkg.get('parcel_id') != d['parcel_id'] or o.get('headers', {}).get('X-Shipment-Idempotency') != d['idempotency_key']:
            return False
    return True
