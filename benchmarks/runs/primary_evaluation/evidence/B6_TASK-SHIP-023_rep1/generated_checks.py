# Inferred logistics invariant check for TASK-SHIP-023 (hazmat_declaration_subschema)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/logistics/hazmat_declaration_subschema/task-ship-023':
            return False
        pkg = o.get('body', {}).get('hazmat_shipping_declaration')
        if not isinstance(pkg, dict) or type(pkg.get('weight_grams')) is not int:
            return False
        if pkg.get('parcel_id') != d['parcel_id'] or o.get('headers', {}).get('X-Shipment-Idempotency') != d['idempotency_key']:
            return False
    return True
