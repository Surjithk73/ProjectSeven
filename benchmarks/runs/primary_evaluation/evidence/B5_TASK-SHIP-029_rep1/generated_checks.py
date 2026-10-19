# Inferred parcel weight & identity invariant check for TASK-SHIP-029
def check(inputs, outputs):
    return all(o.get('path') == '/labels/create' and isinstance(o.get('body', {}).get('parcel'), dict) and type(o['body']['parcel'].get('weight_grams')) is int and o.get('headers', {}).get('Idempotency-Key') == d['idempotency_key'] for d, o in zip(inputs, outputs))
