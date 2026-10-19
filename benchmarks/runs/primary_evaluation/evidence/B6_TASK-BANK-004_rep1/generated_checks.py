# Inferred structural contract check (B6) for TASK-BANK-004
def check(inputs, outputs):
    return all(o.get('path') == '/v2/banking/iso20022_pacs008_wrap/task-bank-004' and isinstance(o.get('body', {}).get('pacs008_document'), dict) and len(o['body']['pacs008_document']) >= 2 for o in outputs)
