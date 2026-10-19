import json
from sig_engine.graph_builder import ensure_sig_current


def analyze_impact(diff_json_str='', sig_path='sig_engine/sig_store.json'):
    try:
        changes = json.loads(diff_json_str or '[]')
    except json.JSONDecodeError as error:
        raise ValueError('Malformed API diff') from error
    if not isinstance(changes, list) or any(not isinstance(item, dict) for item in changes):
        raise ValueError('API diff must be a list of changes')
    endpoints = sorted({item['path'] for item in changes if isinstance(item.get('path'), str)})
    if not endpoints:
        return []
    graph = ensure_sig_current(sig_path, 'client_app' if sig_path == 'sig_engine/sig_store.json' else None)
    result, seen = [], set()
    for endpoint in endpoints:
        if endpoint not in graph:
            continue
        for node in graph.successors(endpoint):
            site = graph.nodes[node]
            if site.get('type') != 'call_site' or node in seen:
                continue
            seen.add(node)
            intent = next((n for n in graph.successors(node) if graph.nodes[n].get('type') == 'intent'), 'Unconfirmed')
            result.append({'call_site': node, 'file': site['file'], 'line': site['line'],
                           'code': site['code'], 'intent': intent})
    return result
