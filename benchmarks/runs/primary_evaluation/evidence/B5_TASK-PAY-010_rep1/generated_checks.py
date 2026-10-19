# Inferred structural contract check (B5) for TASK-PAY-010
def check(inputs, outputs):
    return all(o.get('path') == '/v2/payment/split_fee_nesting/task-pay-010' and isinstance(o.get('body', {}).get('transfer_data_split'), dict) and len(o['body']['transfer_data_split']) >= 2 for o in outputs)
