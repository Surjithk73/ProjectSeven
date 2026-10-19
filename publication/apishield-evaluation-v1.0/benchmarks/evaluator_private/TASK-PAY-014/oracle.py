def evaluate(inputs, outputs):
    return {
        'exact_minor_units': all(isinstance(o.get('body', {}).get('minor_unit_settlement'), dict) and type(o['body']['minor_unit_settlement'].get('amount_subunits')) is int and o['body']['minor_unit_settlement'].get('amount_subunits') == d['amount_cents'] for d, o in zip(inputs, outputs)),
        'idempotency_key': all(o.get('headers', {}).get('Idempotency-Key') == d['idempotency_key'] for d, o in zip(inputs, outputs)),
        'destination': all(isinstance(o.get('body', {}).get('minor_unit_settlement'), dict) and o['body']['minor_unit_settlement'].get('destination_route') == d['destination'] and o['body']['minor_unit_settlement'].get('source_route') == d['source'] for d, o in zip(inputs, outputs))
    }
