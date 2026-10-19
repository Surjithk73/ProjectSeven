from apishield.repository_graph import build_repository_graph


def test_changed_endpoint_reaches_python_callers_and_frontend(tmp_path):
    (tmp_path / 'app.py').write_text('''import httpx
API_BASE = "https://bank.test"
def transfer():
    """Business Intent: Move money without changing its value."""
    return httpx.post(f"{API_BASE}/transfers", json={})
@app.post("/api/pay")
def pay():
    return transfer()
def unrelated():
    return 1
''')
    (tmp_path / 'ui.js').write_text('export async function sendPayment() { return fetch("/api/pay", {method: "POST"}); }')
    scan = {'sites':[{'file':'app.py','function':'transfer','method':'POST','endpoint':'/transfers','line':5}]}
    graph = build_repository_graph(tmp_path, scan, [], [{'method':'POST','endpoint':'/transfers'}])
    nodes = {n.get('function'):n for n in graph['nodes'] if n.get('function')}
    assert nodes['transfer']['impact'] == 'direct'
    assert nodes['pay']['impact'] == 'potential'
    assert nodes['sendPayment']['impact'] == 'potential'
    assert not nodes['unrelated'].get('impact')
    assert nodes['transfer']['code'].startswith('def transfer')
    assert any(n['kind'] == 'intent' for n in graph['nodes'])


def test_ambiguous_calls_do_not_invent_cross_module_edges(tmp_path):
    for name in ('a', 'b'):
        (tmp_path / f'{name}.py').write_text('def same(): return 1\n')
    (tmp_path / 'c.py').write_text('def run(): return same()\n')
    graph = build_repository_graph(tmp_path, {'sites':[]}, [], [])
    assert not any(e['kind'] == 'calls' for e in graph['edges'])


def test_imported_python_calls_are_resolved_without_executing_source(tmp_path):
    (tmp_path / 'client.py').write_text('def get_balance(): return 12\n')
    (tmp_path / 'service.py').write_text('from client import get_balance as balance\ndef overview(): return balance()\n')
    graph = build_repository_graph(tmp_path, {'sites':[]}, [], [])
    nodes = {n['id']:n for n in graph['nodes']}
    assert any(nodes[e['from']].get('function') == 'overview' and nodes[e['to']].get('function') == 'get_balance' for e in graph['edges'] if e['kind'] == 'calls')


def test_ambiguous_routes_and_js_strings_do_not_turn_code_red(tmp_path):
    for file in ('a.py','b.py'):
        (tmp_path/file).write_text('@app.get("/balance")\ndef balance(): return 1\n')
    (tmp_path/'ui.js').write_text('''function help() { return "fetch('/balance')"; }
function commented() { /* fetch('/balance'); */ return 1; }
function real() { return fetch('/balance'); }
''')
    graph = build_repository_graph(tmp_path, {'sites':[]}, [], [])
    assert not any(e['kind'] == 'calls_route' for e in graph['edges'])
    assert any('Ambiguous route' in n['reason'] for n in graph['notes'])


def test_only_real_js_fetch_and_unshadowed_python_calls_connect(tmp_path):
    (tmp_path/'app.py').write_text('''@app.get("/balance")
def changed(): return 1
def wrapper():
    def changed(): return 2
    return changed()
def imported():
    from other import changed
    return changed()
''')
    (tmp_path/'ui.js').write_text('''function help() { return "fetch('/balance')"; }
function commented() { /* fetch('/balance'); */ return 1; }
function real() { return fetch('/balance'); }
''')
    graph = build_repository_graph(tmp_path, {'sites':[]}, [], [])
    nodes = {n['id']:n for n in graph['nodes']}
    assert [nodes[e['from']]['function'] for e in graph['edges'] if e['kind'] == 'calls_route'] == ['real']
    assert not any(e['kind'] == 'calls' and nodes[e['from']].get('function') in {'wrapper','imported'} for e in graph['edges'])
