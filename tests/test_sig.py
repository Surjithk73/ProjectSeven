import json
from pathlib import Path

import pytest

from sig_engine.graph_builder import build_sig
from sig_engine.graph_builder import ensure_sig_current
from agent.analyzer import analyze_impact


def write_service(path, marker):
    path.write_text('''import httpx
API_BASE = "http://localhost:8001"
def pay(amount):
    """Business Intent: Charge a subscription."""
    url = f"{API_BASE}/charge"
    payload = {"amount": amount}
    # MARKER
    return httpx.post(url, json=payload)
'''.replace('MARKER', marker), encoding='utf-8')


def test_offline_graph_uses_explicit_labels_and_edges(tmp_path):
    source = tmp_path / 'client_app'
    source.mkdir()
    write_service(source / 'payment.py', 'before')
    graph = build_sig(str(source), str(tmp_path / 'sig.json'), infer_with_llm=False)
    intents = [n for n, data in graph.nodes(data=True) if data['type'] == 'intent']
    assert intents == ['Charge a subscription.']
    assert graph.has_node('/charge')
    assert len(json.loads((tmp_path / 'sig.json').read_text())['edges']) == 2


def test_impact_refreshes_stale_function_source(tmp_path):
    source = tmp_path / 'client_app'
    source.mkdir()
    write_service(source / 'payment.py', 'before')
    store = str(tmp_path / 'sig.json')
    build_sig(str(source), store, infer_with_llm=False)
    write_service(source / 'payment.py', 'after')
    sites = analyze_impact('[{"path":"/charge"}]', store)
    assert len(sites) == 1
    assert '# after' in sites[0]['code']
    assert '# before' not in sites[0]['code']


def test_unrelated_diff_does_not_guess_charge(tmp_path):
    source = tmp_path / 'client_app'
    source.mkdir()
    write_service(source / 'payment.py', 'before')
    store = str(tmp_path / 'sig.json')
    build_sig(str(source), store, infer_with_llm=False)
    assert analyze_impact('[]', store) == []
    with pytest.raises(ValueError):
        analyze_impact('not-json', store)


def test_graph_records_empty_source_after_last_call_removed(tmp_path):
    source = tmp_path / 'client_app'
    source.mkdir()
    file = source / 'payment.py'
    write_service(file, 'before')
    store = str(tmp_path / 'sig.json')
    build_sig(str(source), store, infer_with_llm=False)
    file.write_text('def pay(amount):\n    return amount\n', encoding='utf-8')
    assert analyze_impact('[{"path":"/charge"}]', store) == []


def test_simultaneous_graph_refreshes_publish_complete_json(tmp_path, monkeypatch):
    import threading
    from concurrent.futures import ThreadPoolExecutor
    source = tmp_path / 'client_app'
    source.mkdir()
    write_service(source / 'payment.py', 'concurrent')
    output = tmp_path / 'sig.json'
    barrier = threading.Barrier(2)
    actual_replace = Path.replace
    paths = []
    def replace(src, dst):
        if src not in paths:
            paths.append(src)
            barrier.wait(timeout=5)
        if len(set(paths)) != 2:
            raise FileNotFoundError('Concurrent publisher consumed shared temporary file')
        return actual_replace(src, dst)
    monkeypatch.setattr(Path, 'replace', replace)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: build_sig(str(source), str(output)), range(2)))
    assert all(graph.has_node('/charge') for graph in results)
    assert json.loads(output.read_text())['graph']['source_hashes']
    assert not list(tmp_path.glob('.sig-*'))


def test_graph_relocation_uses_available_current_checkout(tmp_path):
    source = tmp_path / 'client_app'
    source.mkdir()
    write_service(source / 'payment.py', 'relocated')
    store = tmp_path / 'sig.json'
    build_sig(str(source), str(store))
    data = json.loads(store.read_text())
    data['graph']['client_dir'] = str(tmp_path / 'nonexistent_old_checkout')
    store.write_text(json.dumps(data))
    graph = ensure_sig_current(str(store), str(source))
    assert graph.has_node('/charge')
