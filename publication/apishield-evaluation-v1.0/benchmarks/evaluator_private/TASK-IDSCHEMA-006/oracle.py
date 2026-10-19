def evaluate(inputs, outputs):
    return {
        'rfc6750_bearer_header': all(o.get('headers', {}).get('Authorization') == 'Bearer ' + d['access_token'] for d, o in zip(inputs, outputs)),
        'tenant_context_header': all(o.get('headers', {}).get('X-Tenant-Context') == d['tenant_id'] for d, o in zip(inputs, outputs)),
        'principal_and_cursor': all(isinstance(o.get('body', {}).get('verification_token_envelope'), dict) and o['body']['verification_token_envelope'].get('sub') == d['subject_id'] and o['body']['verification_token_envelope'].get('next_cursor') == d['cursor_token'] for d, o in zip(inputs, outputs)),
        'exact_ttl_integer': all(isinstance(o.get('body', {}).get('verification_token_envelope'), dict) and type(o['body']['verification_token_envelope'].get('ttl_seconds')) is int and o['body']['verification_token_envelope'].get('ttl_seconds') == d['ttl_seconds'] for d, o in zip(inputs, outputs))
    }
