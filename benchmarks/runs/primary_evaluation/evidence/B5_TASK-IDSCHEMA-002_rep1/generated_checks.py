# Inferred structural contract check (B5) for TASK-IDSCHEMA-002
def check(inputs, outputs):
    return all(o.get('path') == '/v2/identity/pagination_cursor_migration/task-idschema-002' and isinstance(o.get('body', {}).get('cursor_page_request'), dict) and len(o['body']['cursor_page_request']) >= 2 for o in outputs)
