def evaluate(inputs, outputs):
    return {
        'exact_minor_units': all(isinstance(o.get('body', {}).get('iban_bic_transfer'), dict) and type(o['body']['iban_bic_transfer'].get('amount_subunits')) is int and o['body']['iban_bic_transfer'].get('amount_subunits') == d['amount_cents'] for d, o in zip(inputs, outputs)),
        'idempotency_key': all(o.get('headers', {}).get('Idempotency-Key') == d['idempotency_key'] for d, o in zip(inputs, outputs)),
        'destination': all(isinstance(o.get('body', {}).get('iban_bic_transfer'), dict) and o['body']['iban_bic_transfer'].get('destination_route') == d['destination'] and o['body']['iban_bic_transfer'].get('source_route') == d['source'] for d, o in zip(inputs, outputs))
    }
