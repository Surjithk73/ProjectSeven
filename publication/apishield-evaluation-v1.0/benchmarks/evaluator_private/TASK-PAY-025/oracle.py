def evaluate(inputs, outputs):
    return {
        'exact_minor_units': all(isinstance(o.get('body', {}).get('payment_intent'), dict) and type(o['body']['payment_intent'].get('amount_subunits')) is int and o['body']['payment_intent'].get('amount_subunits') == d['amount_cents'] for d, o in zip(inputs, outputs)),
        'idempotency_key': all(o.get('headers', {}).get('Idempotency-Key') == d['idempotency_key'] for d, o in zip(inputs, outputs)),
        'destination': all(isinstance(o.get('body', {}).get('payment_intent'), dict) and o['body']['payment_intent'].get('destination_route') == d['destination'] and o['body']['payment_intent'].get('source_route') == d['source'] for d, o in zip(inputs, outputs))
    }
