from pathlib import Path


def test_explicit_receiver_binding_scans_class_adapter(tmp_path):
    from apishield.analysis import scan_sources
    (tmp_path / 'adapter.py').write_text('class Payment:\n def call(self):\n  return self.client.post("/payments", json={})\n')
    assert not scan_sources(tmp_path, ['adapter.py'])['sites']
    scan = scan_sources(tmp_path, ['adapter.py'], http_bindings={'adapter.py': {
        'provider_id': 'payment', 'base_url': 'http://localhost:8102', 'receiver': 'self.client'}})
    assert scan['sites'][0]['provider_id'] == 'payment'
    assert scan['sites'][0]['endpoint'] == '/__provider__/payment/payments'
    assert scan['sites'][0]['display_endpoint'] == '/payments'


def test_combined_contract_keeps_colliding_paths_and_components_distinct():
    from apishield.projects import combined_contract
    document = {'openapi': '3.0.3', 'info': {'version': '1.0.0'}, 'paths': {'/payments': {'post': {
        'responses': {'200': {'description': 'ok', 'content': {'application/json': {'schema': {'$ref': '#/components/schemas/Money'}}}}}}}},
        'components': {'schemas': {'Money': {'type': 'integer'}}}}
    result = combined_contract({'theatre': document, 'payment': document})
    assert len(result['paths']) == 2
    assert result['paths']['/__provider__/payment/payments']['post']['responses']['200']['content']['application/json']['schema']['$ref'] == '#/components/schemas/payment__Money'
    assert len(result['components']['schemas']) == 2


def test_bound_graph_labels_are_readable_and_provider_qualified(tmp_path):
    from apishield.analysis import scan_sources
    from apishield.repository_graph import build_repository_graph
    (tmp_path/'adapter.py').write_text('class Payment:\n def call(self):\n  return self.client.post("/payments", json={})\n')
    scan = scan_sources(tmp_path,['adapter.py'],{'adapter.py':{'provider_id':'payment','base_url':'http://localhost:8102','receiver':'self.client'}})
    graph=build_repository_graph(tmp_path,scan,[],[])
    operation=next(n for n in graph['nodes'] if n['kind']=='operation')
    assert operation['provider_id']=='payment'
    assert '/__provider__/' not in operation['label']


def test_binding_does_not_claim_a_different_absolute_origin(tmp_path):
    from apishield.analysis import scan_sources
    (tmp_path/'adapter.py').write_text('class Payment:\n def call(self):\n  return self.client.get("http://other.local/payments")\n')
    scan=scan_sources(tmp_path,['adapter.py'],{'adapter.py':{'provider_id':'payment','base_url':'http://localhost:8102','receiver':'self.client'}})
    assert scan['sites'][0]['endpoint'] is None
