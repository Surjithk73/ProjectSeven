def evaluate(inputs, outputs):
    return {
        'parcel_identity': all(isinstance(o.get('body', {}).get('shipment_milestone_envelope'), dict) and o['body']['shipment_milestone_envelope'].get('parcel_id') == d['parcel_id'] for d, o in zip(inputs, outputs)),
        'exact_weight_grams': all(isinstance(o.get('body', {}).get('shipment_milestone_envelope'), dict) and type(o['body']['shipment_milestone_envelope'].get('weight_grams')) is int and o['body']['shipment_milestone_envelope'].get('weight_grams') == d['weight_grams'] for d, o in zip(inputs, outputs)),
        'carrier_and_address': all(isinstance(o.get('body', {}).get('shipment_milestone_envelope'), dict) and o['body']['shipment_milestone_envelope'].get('carrier_iso') == d['carrier_code'] and o['body']['shipment_milestone_envelope'].get('route_address') == d['street_address'] for d, o in zip(inputs, outputs)),
        'idempotency_key': all(o.get('headers', {}).get('X-Shipment-Idempotency') == d['idempotency_key'] for d, o in zip(inputs, outputs))
    }
