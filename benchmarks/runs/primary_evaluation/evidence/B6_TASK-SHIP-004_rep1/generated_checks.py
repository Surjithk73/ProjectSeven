# Inferred structural contract check (B6) for TASK-SHIP-004
def check(inputs, outputs):
    return all(o.get('path') == '/v2/logistics/dimensions_nesting_object/task-ship-004' and isinstance(o.get('body', {}).get('parcel_dimensions_box'), dict) and len(o['body']['parcel_dimensions_box']) >= 2 for o in outputs)
