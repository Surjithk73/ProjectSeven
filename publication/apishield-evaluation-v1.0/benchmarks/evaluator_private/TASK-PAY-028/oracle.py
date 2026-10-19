def evaluate(inputs, outputs):
    return {
        'exact_minor_units': all(isinstance(o.get('body', {}).get('transfer_data_split'), dict) and type(o['body']['transfer_data_split'].get('amount_subunits')) is int and o['body']['transfer_data_split'].get('amount_subunits') == d['amount_cents'] for d, o in zip(inputs, outputs)),
        'idempotency_key': all(o.get('headers', {}).get('Idempotency-Key') == d['idempotency_key'] for d, o in zip(inputs, outputs)),
        'destination': all(isinstance(o.get('body', {}).get('transfer_data_split'), dict) and o['body']['transfer_data_split'].get('destination_route') == d['destination'] and o['body']['transfer_data_split'].get('source_route') == d['source'] for d, o in zip(inputs, outputs))
    }
