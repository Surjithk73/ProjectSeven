def evaluate(inputs, outputs):
    return {
        'endpoint': all(o.get('path') == '/v2/identity/pagination_cursor_migration/task-idschema-002' for o in outputs),
        'payload_shape': all(isinstance(o.get('body', {}).get('cursor_page_request'), dict) for o in outputs)
    }
