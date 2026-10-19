import copy
import importlib
import json

import pytest

from apishield.configuration import load_config
from test_local_engine import shipment
from test_local_engine import git, engine
from pathlib import Path


RULE = dict(id='exact-weight', description='Preserve exact integer grams and parcel identity.',
            scope={'file':'src/client.py','function':'ship'}, origin='developer', confirmed=True,
            checks=['tests/test_shipping.py::test_exact_shipment'])


def module():
    assert importlib.util.find_spec('apishield.requirements'), 'requirements module is missing'
    return importlib.import_module('apishield.requirements')


def test_requirement_config_roundtrip_and_legacy(shipment):
    _, path, _, _, raw = shipment
    assert getattr(load_config(path), 'requirements', None) == []
    raw['requirements'] = [RULE]
    path.write_text(json.dumps(raw))
    config = load_config(path)
    assert config.requirements == [RULE]
    assert config.to_dict()['requirements'] == [RULE]


@pytest.mark.parametrize('change', [
    {'id':'bad id'}, {'description':' '}, {'description':'x'*2001}, {'confirmed':1},
    {'origin':'ai'}, {'extra':True}, {'scope':{'file':'../other.py','function':'ship'}},
    {'scope':{'file':'outside.py','function':'ship'}}, {'scope':{'file':'src/client.py','function':''}},
    {'checks':['--help']}, {'checks':['../tests/test.py::test_x']},
    {'checks':['tests/test.py']}, {'checks':['src/client.py::test_x']},
    {'checks':['tests/test.py::test_x[arbitrary]']}, {'checks':['tests/test.py::not_a_test']},
])
def test_rejects_invalid_requirement(change):
    with pytest.raises(ValueError):
        module().validate_requirements([{**RULE, **change}], ['src'])


def test_duplicate_ids_and_valid_class_selector():
    with pytest.raises(ValueError):
        module().validate_requirements([RULE, RULE], ['src'])
    rule = {**RULE, 'checks':['tests/test.py::TestParcel::test_x']}
    assert module().validate_requirements([rule], ['src']) == [rule]


def test_graph_distinguishes_declaration_and_inference_with_stable_calls():
    site = dict(file='src/client.py', function='ship', line=7, method='POST', endpoint='/ship',
                intent='Preserve weight')
    scan = {'sites':[site, {**site,'line':9}], 'limitations':[]}
    graph = module().build_requirement_graph(scan, [RULE], {'source_commit':'abc'})
    shifted = copy.deepcopy(scan)
    for item in shifted['sites']: item['line'] += 5
    again = module().build_requirement_graph(shifted, [RULE], {'source_commit':'def'})
    calls = [n for n in graph['nodes'] if n['kind']=='call']
    assert len({n['id'] for n in calls}) == 2
    assert [n['id'] for n in calls] == [n['id'] for n in again['nodes'] if n['kind']=='call']
    assert {e['kind'] for e in graph['edges']} == {'consumes','scopes','checked_by'}
    assert graph['suggestions'][0]['confirmed'] is False
    assert graph['suggestions'][0]['origin'] == 'source_intent'
    assert module().requirements_hash([RULE]) == module().requirements_hash([dict(reversed(list(RULE.items())))])


def test_graph_reports_unresolved_scope_and_url():
    scan = {'sites':[dict(file='src/client.py',function='other',line=1,method='POST',endpoint=None)], 'limitations':[]}
    graph = module().build_requirement_graph(scan, [RULE], {})
    assert len(graph['notes']) == 2
    assert all(edge['kind'] == 'checked_by' for edge in graph['edges'])


@pytest.mark.parametrize('record', ['', '<testcase><skipped/></testcase>', '<testcase><failure/></testcase>',
                                   '<testcase><error/></testcase>'])
def test_checks_require_actual_passes_and_reject_nonpassing_records(tmp_path, record):
    xml = tmp_path/'report.xml'
    xml.write_text('<testsuites><testsuite>'+record+'</testsuite></testsuites>')
    assert module().read_check_result(xml, 0)['passed'] is False


def test_check_result_rejects_missing_malformed_oversized_and_bad_exit(tmp_path):
    xml = tmp_path/'report.xml'
    assert not module().read_check_result(xml, 0)['passed']
    xml.write_text('not XML')
    assert not module().read_check_result(xml, 0)['passed']
    xml.write_text('x'*(1024*1024+1))
    assert not module().read_check_result(xml, 0)['passed']
    xml.write_text('<testsuites><testsuite><testcase name="test_x"/></testsuite></testsuites>')
    assert not module().read_check_result(xml, 1)['passed']
    assert module().read_check_result(xml, 0)['passed']


def configure(shipment, rule=RULE, *, weak=False):
    repo, path, candidate, store, raw = shipment
    raw['requirements'] = [rule]
    if weak:
        (repo/'tests/test_weak.py').write_text('def test_shape():\n    assert True\n')
        git(repo, 'add', '.')
        git(repo, '-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-m','Weak ordinary suite')
        raw['test_commands'] = [['python','-m','pytest','tests/test_weak.py','-q']]
    path.write_text(json.dumps(raw))
    return repo, load_config(path), candidate, store


def test_correct_repair_passes_declared_requirement(shipment):
    repo, config, candidate, store = configure(shipment)
    before = (repo/'src/client.py').read_bytes()
    result = engine().run_job(config, 'repair', store, candidate_path=candidate)
    assert result['status'] == 'validated', result
    assert result['requirement_outcomes'][0]['status'] == 'passed'
    assert result['requirements_hash'] == module().requirements_hash([RULE])
    assert result['requirement_graph']['edges']
    assert (repo/'src/client.py').read_bytes() == before
    assert (store._path(result['job_id'])/'candidate.patch').exists()


def test_wrong_units_pass_ordinary_tests_but_fail_requirement(shipment):
    repo, config, candidate, store = configure(shipment, weak=True)
    proposal = json.loads(candidate.read_text())
    proposal['patches'].append({'file':'src/client.py','old_code_snippet':'"grams": grams','new_code_snippet':'"grams": grams / 1000'})
    candidate.write_text(json.dumps(proposal))
    result = engine().run_job(config, 'repair', store, candidate_path=candidate)
    assert result['attempts'][0]['validation'][0]['exit_code'] == 0
    assert result['status'] == 'failed'
    assert result['requirement_outcomes'][0]['status'] == 'failed'
    assert 'exact-weight' in result['error']
    assert not (store._path(result['job_id'])/'candidate.patch').exists()


def test_refund_to_charge_passes_ordinary_but_fails_requirement(shipment):
    repo, _, candidate, _, raw = shipment
    path = shipment[1]
    test = repo/'tests/test_shipping.py'
    test.write_text(test.read_text().replace('/shipments/create', '/refunds/create'))
    git(repo,'add','.')
    git(repo,'-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-m','Refund behavior')
    target = path.parent/'target.json'
    contract = json.loads(target.read_text())
    contract['paths']['/refunds/create'] = contract['paths'].pop('/shipments/create')
    contract['paths']['/charges'] = {'post':{'responses':{'200':{'description':'charge'}}}}
    target.write_text(json.dumps(contract))
    rule = {**RULE,'id':'refund-only','description':'Refund the exact value; never create a new charge.'}
    repo, config, candidate, store = configure(shipment, rule, weak=True)
    proposal=json.loads(candidate.read_text())
    proposal['patches'][0]['new_code_snippet']='f"{BASE}/charges"'
    candidate.write_text(json.dumps(proposal))
    result=engine().run_job(config,'repair',store,candidate_path=candidate)
    assert result['attempts'][0]['validation'][0]['exit_code']==0
    assert result['status']=='failed'
    assert result['requirement_outcomes'][0]['status']=='failed'


@pytest.mark.parametrize('change', [
    {'checks':[]}, {'checks':['tests/test_absent.py::test_x']},
    {'scope':{'file':'src/client.py','function':'missing'}},
])
def test_missing_requirement_evidence_stops_before_generation(shipment, monkeypatch, change):
    _, config, _, store = configure(shipment, {**RULE, **change})
    monkeypatch.setattr(engine(), 'generate_candidate', lambda *args: pytest.fail('generation must not run'))
    result=engine().run_job(config,'repair',store)
    assert result['status']=='needs_input', result
    assert result['requirement_outcomes'][0]['status']=='needs_input'
    assert 'exact-weight' in result['error']


def test_untracked_requirement_test_is_not_accepted(shipment):
    repo, path, _, _, _ = shipment
    (repo/'tests/test_absent.py').write_text('def test_x():\n    assert True\n')
    _, config, candidate, store=configure(shipment,{**RULE,'checks':['tests/test_absent.py::test_x']})
    result=engine().run_job(config,'repair',store,candidate_path=candidate)
    assert result['status']=='needs_input'


@pytest.mark.parametrize('decorator', ['@pytest.mark.skip(reason="not available")', '@pytest.mark.xfail(reason="not checked")'])
def test_skipped_or_xfailed_check_cannot_validate(shipment, decorator):
    repo, path, _, _, _ = shipment
    test=repo/'tests/test_shipping.py'
    test.write_text('import pytest\n'+test.read_text().replace('def test_exact_shipment',decorator+'\ndef test_exact_shipment'))
    git(repo,'add','.')
    git(repo,'-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-m','Skipped behavior check')
    # A genuinely xfailed check, rather than unexpected success.
    if 'xfail' in decorator:
        test.write_text(test.read_text().replace('2501}', '999}'))
        git(repo,'add','.')
        git(repo,'-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-m','Expected failure')
    _, config, candidate, store=configure(shipment, weak=True)
    result=engine().run_job(config,'repair',store,candidate_path=candidate)
    assert result['status']=='failed',result
    assert result['requirement_outcomes'][0]['status']=='failed'


def test_unconfirmed_and_unaffected_rules_are_not_gates(shipment):
    rule={**RULE,'confirmed':False,'checks':[]}
    _, config, candidate, store=configure(shipment,rule)
    result=engine().run_job(config,'repair',store,candidate_path=candidate)
    assert result['status']=='validated'
    assert result['requirement_outcomes'][0]['status']=='unconfirmed'
    rule={**RULE,'scope':{'file':'src/client.py','function':'health'},'checks':[]}
    _, config, candidate, store=configure(shipment,rule)
    result=engine().run_job(config,'repair',store,candidate_path=candidate)
    assert result['status']=='validated'
    assert result['requirement_outcomes'][0]['status']=='not_applicable'


def test_requirement_deadline_never_reports_passed(shipment):
    repo,path,candidate,store,raw=shipment
    test=repo/'tests/test_shipping.py'
    test.write_text(test.read_text().replace('    assert ship(', '    import time; time.sleep(3)\n    assert ship('))
    git(repo,'add','.')
    git(repo,'-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-m','Slow requirement')
    raw['requirements']=[RULE]
    raw['test_commands']=[['python','-c','print("ordinary checks complete")']]
    raw['budgets']['command_timeout_seconds']=1
    path.write_text(json.dumps(raw))
    result=engine().run_job(load_config(path),'repair',store,candidate_path=candidate)
    assert result['timed_out'] is True,result
    assert result['requirement_outcomes'][0]['status']=='failed'
    assert not (store._path(result['job_id'])/'candidate.patch').exists()


def test_parametrized_requirement_checks_all_cases(shipment):
    repo,path,candidate,store,raw=shipment
    test=repo/'tests/test_shipping.py'
    test.write_text('import pytest\n'+test.read_text().replace('def test_exact_shipment(monkeypatch):',
        '@pytest.mark.parametrize("sample", [1, 2])\ndef test_exact_shipment(monkeypatch, sample):'))
    git(repo,'add','.')
    git(repo,'-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-m','Parameterized requirement')
    _,config,candidate,store=configure(shipment)
    result=engine().run_job(config,'repair',store,candidate_path=candidate)
    assert result['status']=='validated',result
    assert result['requirement_outcomes'][0]['evidence'][0]['result']['tests']==2


def test_report_reader_retries_transient_windows_file_contention(shipment, monkeypatch):
    _,path,_,store,_=shipment
    job=store.create(load_config(path),'scan')
    original=Path.read_text
    calls=[]
    def contended(file,*args,**kwargs):
        if file == job.path/'result.json':
            calls.append(file)
            if len(calls)==1:
                raise PermissionError('simulated Windows atomic replacement contention')
        return original(file,*args,**kwargs)
    monkeypatch.setattr(Path,'read_text',contended)
    assert store.get(job.id)['status']=='queued'
    assert len(calls)==2


@pytest.mark.parametrize('reference', ['tests/test_shipping.py::test_missing', 'tests/test_shipping.py::TestMissing::test_x'])
def test_missing_selected_test_function_stops_before_generation(shipment,monkeypatch,reference):
    _,config,_,store=configure(shipment,{**RULE,'checks':[reference]})
    monkeypatch.setattr(engine(),'generate_candidate',lambda *args:pytest.fail('missing check must stop before generation'))
    result=engine().run_job(config,'repair',store)
    assert result['status']=='needs_input',result
    assert result['requirement_outcomes'][0]['status']=='needs_input'
    assert 'exact-weight' in result['error']
