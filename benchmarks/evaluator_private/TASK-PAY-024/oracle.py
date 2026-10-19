def evaluate(inputs, outputs):
    return {
        'exact_minor_units': all(isinstance(o.get('body', {}).get('signed_webhook_event'), dict) and type(o['body']['signed_webhook_event'].get('amount_subunits')) is int and o['body']['signed_webhook_event'].get('amount_subunits') == d['amount_cents'] for d, o in zip(inputs, outputs)),
        'idempotency_key': all(o.get('headers', {}).get('X-Nexus-Signature') == d['idempotency_key'] for d, o in zip(inputs, outputs)),
        'destination': all(isinstance(o.get('body', {}).get('signed_webhook_event'), dict) and o['body']['signed_webhook_event'].get('destination_route') == d['destination'] and o['body']['signed_webhook_event'].get('source_route') == d['source'] for d, o in zip(inputs, outputs))
    }
