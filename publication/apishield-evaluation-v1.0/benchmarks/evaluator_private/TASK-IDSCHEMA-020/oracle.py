def evaluate(inputs, outputs):
    return {
        'rfc6750_bearer_header': all(o.get('headers', {}).get('Authorization') == 'Bearer ' + d['access_token'] for d, o in zip(inputs, outputs)),
        'tenant_context_header': all(o.get('headers', {}).get('X-Tenant-Context') == d['tenant_id'] for d, o in zip(inputs, outputs)),
        'principal_and_cursor': all(isinstance(o.get('body', {}).get('cursor_page_request'), dict) and o['body']['cursor_page_request'].get('sub') == d['subject_id'] and o['body']['cursor_page_request'].get('next_cursor') == d['cursor_token'] for d, o in zip(inputs, outputs)),
        'exact_ttl_integer': all(isinstance(o.get('body', {}).get('cursor_page_request'), dict) and type(o['body']['cursor_page_request'].get('ttl_seconds')) is int and o['body']['cursor_page_request'].get('ttl_seconds') == d['ttl_seconds'] for d, o in zip(inputs, outputs))
    }
