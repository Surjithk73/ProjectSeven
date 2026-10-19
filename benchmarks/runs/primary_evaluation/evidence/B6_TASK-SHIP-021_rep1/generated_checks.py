# Inferred logistics invariant check for TASK-SHIP-021 (carrier_code_enum_standardization)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/logistics/carrier_code_enum_standardization/task-ship-021':
            return False
        pkg = o.get('body', {}).get('iso_carrier_dispatch')
        if not isinstance(pkg, dict) or type(pkg.get('weight_grams')) is not int:
            return False
        if pkg.get('parcel_id') != d['parcel_id'] or o.get('headers', {}).get('X-Shipment-Idempotency') != d['idempotency_key']:
            return False
    return True
