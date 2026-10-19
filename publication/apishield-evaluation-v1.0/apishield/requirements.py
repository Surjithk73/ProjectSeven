"""Developer declarations and conservative source/test evidence, not semantic proof."""
from collections import Counter
import hashlib
import json
from pathlib import PurePosixPath
import re
import xml.etree.ElementTree as ET

from .configuration import relative_path


def validate_requirements(value, code_paths):
    if not isinstance(value, list) or len(value) > 100:
        raise ValueError('requirements must be a list of at most 100 rules')
    result, ids = [], set()
    for rule in value:
        keys = {'id', 'description', 'scope', 'origin', 'confirmed', 'checks'}
        if not isinstance(rule, dict) or set(rule) != keys:
            raise ValueError('Each requirement needs id, description, scope, origin, confirmed and checks only')
        if not isinstance(rule['id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', rule['id']) or rule['id'] in ids:
            raise ValueError('Requirement IDs must be unique letters, numbers, hyphens or underscores (1–64 characters)')
        if not isinstance(rule['description'], str) or not rule['description'].strip() or len(rule['description']) > 2000:
            raise ValueError('Requirement description must contain 1–2,000 characters')
        if rule['origin'] not in ('developer', 'source_intent') or type(rule['confirmed']) is not bool:
            raise ValueError('Invalid requirement origin or confirmation')
        scope = rule['scope']
        if not isinstance(scope, dict) or set(scope) != {'file', 'function'}:
            raise ValueError('Requirement scope needs file and function only')
        file = relative_path(scope['file'])
        if not file.endswith('.py') or not any(PurePosixPath(file).is_relative_to(path) for path in code_paths):
            raise ValueError('Requirement scope must be a Python file in configured source paths')
        function = scope['function']
        if not isinstance(function, str) or not (function == '<module>' or re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*', function)):
            raise ValueError('Requirement scope needs an exact scanner function name')
        checks = rule['checks']
        if not isinstance(checks, list) or len(checks) > 30 or any(not isinstance(c, str) for c in checks):
            raise ValueError('Requirement checks must be a list of at most 30 pytest references')
        for check in checks:
            parts = check.split('::')
            test_file = relative_path(parts[0])
            name = PurePosixPath(test_file).name
            protected = name.startswith('test_') or name.endswith('_test.py') or any(p in {'test', 'tests'} for p in PurePosixPath(test_file).parts[:-1])
            if test_file.startswith('-') or test_file != parts[0] or not test_file.endswith('.py') or not protected or len(parts) not in {2, 3}:
                raise ValueError('Checks must name a protected pytest file and exact test function')
            if not re.fullmatch(r'test_[A-Za-z0-9_]+', parts[-1]) or (len(parts) == 3 and not re.fullmatch(r'Test[A-Za-z0-9_]*', parts[1])):
                raise ValueError('Checks accept test functions and optional Test classes, without options or parameter expressions')
        if len(set(checks)) != len(checks):
            raise ValueError('Requirement checks must not contain duplicate references')
        ids.add(rule['id'])
        result.append({**rule, 'scope':{'file':file, 'function':function}, 'checks':list(checks)})
    return result


def requirements_hash(requirements):
    return hashlib.sha256(json.dumps(requirements, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()


def _id(kind, identity):
    return kind + ':' + requirements_hash(identity)[:24]


def build_requirement_graph(scan, requirements, source):
    nodes, edges, notes, suggestions, calls = {}, [], [], {}, []
    counts = Counter()
    for site in scan['sites']:
        identity = [site['file'], site['function'], site['method'], site['endpoint']]
        key = tuple(identity)
        counts[key] += 1
        call_id = _id('call', [*identity, counts[key]])
        nodes[call_id] = {'id':call_id, 'kind':'call', **site}
        calls.append((site, call_id))
        if site['endpoint'] is not None:
            op_id = _id('operation', [site['method'], site['endpoint']])
            nodes[op_id] = {'id':op_id, 'kind':'operation', 'method':site['method'], 'endpoint':site['endpoint']}
            edges.append({'from':call_id, 'to':op_id, 'kind':'consumes', 'basis':'scanner'})
        else:
            notes.append({'file':site['file'], 'line':site['line'], 'reason':'Unresolved operation; no operation edge inferred'})
        if site.get('intent'):
            suggested_id = 'intent-' + _id('scope', [site['file'], site['function']]).split(':')[1]
            suggestions[suggested_id] = {'id':suggested_id, 'description':site['intent'],
                'scope':{'file':site['file'], 'function':site['function']}, 'origin':'source_intent', 'confirmed':False, 'checks':[]}
    for rule in requirements:
        rule_id = _id('requirement', rule['id'])
        nodes[rule_id] = {'kind':'requirement', **rule, 'id':rule_id, 'requirement_id':rule['id']}
        matching = [(site, call_id) for site, call_id in calls if all(site[k] == v for k, v in rule['scope'].items())]
        if not matching:
            notes.append({'requirement_id':rule['id'], 'reason':'Declared source scope did not match a supported call'})
        for _, call_id in matching:
            edges.append({'from':rule_id, 'to':call_id, 'kind':'scopes', 'basis':'developer_declaration', 'confirmed':rule['confirmed']})
        for check in rule['checks']:
            test_id = _id('test', check)
            nodes[test_id] = {'id':test_id, 'kind':'test', 'reference':check}
            edges.append({'from':rule_id, 'to':test_id, 'kind':'checked_by', 'basis':'developer_declaration'})
    return {'version':1, 'source_commit':source.get('source_commit'), 'nodes':list(nodes.values()),
            'edges':edges, 'notes':notes, 'suggestions':list(suggestions.values())}


def requirement_outcomes(requirements, scan, impacted_sites, workspace):
    outcomes = []
    affected_files = {site['file'] for site in impacted_sites}
    for rule in requirements:
        outcome = {**rule, 'status':'unconfirmed', 'evidence':[]}
        outcomes.append(outcome)
        if not rule['confirmed']:
            continue
        matching = [site for site in scan['sites'] if all(site[k] == v for k, v in rule['scope'].items())]
        affected = any(all(site[k] == v for k, v in rule['scope'].items()) for site in impacted_sites)
        unresolved = not matching or any(site['endpoint'] is None for site in matching)
        if not affected and not (unresolved and rule['scope']['file'] in affected_files):
            outcome['status'] = 'not_applicable'
            continue
        reason = None
        if unresolved:
            reason = 'Source scope is unresolved in an affected file; review the file/function and coverage notes'
        elif not rule['checks']:
            reason = 'Link a committed pytest test before validating this confirmed requirement'
        else:
            missing = [c for c in rule['checks'] if not (workspace / c.split('::')[0]).is_file()]
            if missing:
                reason = 'Selected test is absent from the pinned revision: ' + ', '.join(missing)
        outcome['status'] = 'needs_input' if reason else 'pending'
        if reason:
            outcome['reason'] = reason
    return outcomes


def read_check_result(path, exit_code):
    """Read capped, untrusted pytest XML; process success alone is insufficient."""
    try:
        if path.is_symlink() or path.stat().st_size > 1024 * 1024:
            raise ValueError('Selected-check report is unsafe or exceeds 1 MiB')
        content = path.read_bytes()
        if b'<!DOCTYPE' in content.upper() or b'<!ENTITY' in content.upper():
            raise ValueError('Selected-check report contains a forbidden XML declaration')
        root = ET.fromstring(content)
        if root.tag not in {'testsuites', 'testsuite'}:
            raise ValueError('Selected-check report is not pytest JUnit evidence')
        cases = list(root.iter('testcase'))
        nonpassing = sum(any(case.find(tag) is not None for tag in ('failure', 'error', 'skipped')) for case in cases)
        errors = list(root.iter('error'))
        passed = exit_code == 0 and bool(cases) and nonpassing == 0 and not errors
        return {'passed':passed, 'tests':len(cases), 'nonpassing':nonpassing,
                'reason':None if passed else 'Selected tests must actually pass; empty, skipped, failed and error checks do not validate a requirement'}
    except (OSError, ValueError, ET.ParseError) as error:
        return {'passed':False, 'tests':0, 'reason':f'Cannot establish selected-check evidence: {error}'}
