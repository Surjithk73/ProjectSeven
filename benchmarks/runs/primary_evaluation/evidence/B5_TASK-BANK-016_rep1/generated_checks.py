# Inferred structural contract check (B5) for TASK-BANK-016
def check(inputs, outputs):
    return all(o.get('path') == '/v2/banking/iso20022_pacs008_wrap/task-bank-016' and isinstance(o.get('body', {}).get('pacs008_document'), dict) and len(o['body']['pacs008_document']) >= 2 for o in outputs)
