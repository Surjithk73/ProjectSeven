# Inferred structural contract check (B5) for TASK-SHIP-022
def check(inputs, outputs):
    return all(o.get('path') == '/v2/logistics/dimensions_nesting_object/task-ship-022' and isinstance(o.get('body', {}).get('parcel_dimensions_box'), dict) and len(o['body']['parcel_dimensions_box']) >= 2 for o in outputs)
