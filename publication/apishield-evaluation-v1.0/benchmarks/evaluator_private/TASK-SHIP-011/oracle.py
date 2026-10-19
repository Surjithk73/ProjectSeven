def evaluate(inputs, outputs):
    return {
        'parcel_identity': all(isinstance(o.get('body', {}).get('hazmat_shipping_declaration'), dict) and o['body']['hazmat_shipping_declaration'].get('parcel_id') == d['parcel_id'] for d, o in zip(inputs, outputs)),
        'exact_weight_grams': all(isinstance(o.get('body', {}).get('hazmat_shipping_declaration'), dict) and type(o['body']['hazmat_shipping_declaration'].get('weight_grams')) is int and o['body']['hazmat_shipping_declaration'].get('weight_grams') == d['weight_grams'] for d, o in zip(inputs, outputs)),
        'carrier_and_address': all(isinstance(o.get('body', {}).get('hazmat_shipping_declaration'), dict) and o['body']['hazmat_shipping_declaration'].get('carrier_iso') == d['carrier_code'] and o['body']['hazmat_shipping_declaration'].get('route_address') == d['street_address'] for d, o in zip(inputs, outputs)),
        'idempotency_key': all(o.get('headers', {}).get('X-Shipment-Idempotency') == d['idempotency_key'] for d, o in zip(inputs, outputs))
    }
