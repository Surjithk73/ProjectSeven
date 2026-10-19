# Inferred structural contract check (B6) for TASK-SHIP-014
def check(inputs, outputs):
    return all(o.get('path') == '/v2/logistics/metric_weight_conversion/task-ship-014' and isinstance(o.get('body', {}).get('metric_parcel_weight'), dict) and len(o['body']['metric_parcel_weight']) >= 2 for o in outputs)
