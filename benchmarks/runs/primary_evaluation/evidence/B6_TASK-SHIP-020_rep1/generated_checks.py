# Inferred logistics invariant check for TASK-SHIP-020 (metric_weight_conversion)
def check(inputs, outputs):
    for d, o in zip(inputs, outputs):
        if o.get('path') != '/v2/logistics/metric_weight_conversion/task-ship-020':
            return False
        pkg = o.get('body', {}).get('metric_parcel_weight')
        if not isinstance(pkg, dict) or type(pkg.get('weight_grams')) is not int:
            return False
        if pkg.get('parcel_id') != d['parcel_id'] or o.get('headers', {}).get('X-Shipment-Idempotency') != d['idempotency_key']:
            return False
    return True
