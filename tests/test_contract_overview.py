from apishield.overview import contract_overview


def test_retained_overview_checks_hash_and_does_not_modify_snapshots(tmp_path):
    import hashlib
    import json
    from apishield.overview import retained_overview
    contracts=tmp_path/'contracts';contracts.mkdir()
    content=json.dumps({'openapi':'3.0.3','info':{'title':'Bank'},'paths':{}}).encode()
    for name in ('base','target'):
        (contracts/f'{name}.json').write_bytes(content)
    report={f'{name}_spec_hash':hashlib.sha256(content).hexdigest() for name in ('base','target')}
    overview=retained_overview(tmp_path,report)
    assert overview['before']['info']['title']=='Bank'
    assert all((contracts/f'{name}.json').read_bytes()==content for name in ('base','target'))
    (contracts/'target.json').write_text('{}')
    assert 'unavailable' in retained_overview(tmp_path,report)


def test_unchanged_contract_still_has_original_request_and_response_details():
    spec={'openapi':'3.0.3','info':{'title':'Bank','version':'1'},'paths':{'/transfer':{'post':{'requestBody':{'content':{'application/json':{'schema':{'type':'object','properties':{'amount_cents':{'type':'integer'}}}}}},'responses':{'200':{'description':'Transferred'}}}}}}
    overview=contract_overview(spec,spec)
    assert overview['before']['info']['title']=='Bank'
    assert len(overview['before']['operations'])==1
    assert overview['before']['operations'][0]['definition']['requestBody']==spec['paths']['/transfer']['post']['requestBody']
    assert overview['changes']==[]


def test_overview_retains_both_sides_and_added_removed_operations():
    base={'openapi':'3.0.3','info':{},'paths':{'/old':{'get':{'responses':{'200':{'description':'Old'}}}},'/keep':{'post':{'responses':{}}}}}
    target={'openapi':'3.0.3','info':{},'paths':{'/new':{'get':{'responses':{'200':{'description':'New'}}}},'/keep':{'post':{'responses':{'202':{'description':'Queued'}}}}}}
    overview=contract_overview(base,target)
    assert {n['status'] for n in overview['changes']}=={'added','removed','changed'}
    changed=next(n for n in overview['changes'] if n['status']=='changed')
    assert changed['before']['operation']['responses']=={}
    assert '202' in changed['after']['operation']['responses']
