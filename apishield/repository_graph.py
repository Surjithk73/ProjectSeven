"""Bounded, read-only source graph. Dynamic behavior stays unresolved."""
import ast
from collections import deque
from pathlib import Path
import re


def _path(value):
    return re.sub(r'\{[^}]+\}', '{}', value)


def _body_nodes(node):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        yield child
        yield from _body_nodes(child)


def _js_mask(source, strings=True):
    """Keep offsets/newlines while excluding comments and optionally strings."""
    output, index = list(source), 0
    while index < len(source):
        start, end, hide = index, index + 1, True
        if source.startswith('//', index):
            end = source.find('\n', index)
            end = len(source) if end < 0 else end
        elif source.startswith('/*', index):
            found = source.find('*/', index + 2)
            end = len(source) if found < 0 else found + 2
        elif source[index] in "\"'`":
            quote, end, hide = source[index], index + 1, strings
            while end < len(source):
                if source[end] == '\\':
                    end += 2
                elif source[end] == quote:
                    end += 1
                    break
                else:
                    end += 1
        else:
            index += 1
            continue
        if hide:
            for position in range(start, min(end, len(source))):
                if source[position] != '\n':
                    output[position] = ' '
        index = end
    return ''.join(output)


def _scope_bindings(node):
    names = set()
    def visit(item):
        for child in ast.iter_child_nodes(item):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(child.name)
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                names.update(a.asname or (a.name.split('.')[0] if isinstance(child, ast.Import) else a.name) for a in child.names)
            else:
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                    names.add(child.id)
                visit(child)
    visit(node)
    return names


def _js_functions(source):
    # Only named function declarations; arrows/closures are explicitly uncovered.
    pattern = r'(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{'
    for match in re.finditer(pattern, _js_mask(source)):
        depth, index, quote = 1, match.end(), None
        while index < len(source) and depth:
            char = source[index]
            if quote:
                if char == '\\':
                    index += 2
                    continue
                if char == quote:
                    quote = None
            elif char in "\"'`":
                quote = char
            elif source.startswith('//', index):
                end = source.find('\n', index)
                index = len(source) if end < 0 else end
                continue
            elif source.startswith('/*', index):
                end = source.find('*/', index + 2)
                index = len(source) if end < 0 else end + 2
                continue
            elif char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
            index += 1
        if not depth:
            yield match.group(1), source.count('\n', 0, match.start()) + 1, source[match.start():index]


def build_repository_graph(root, scan, requirements, changed_operations, check=lambda: None):
    root = Path(root)
    nodes, edges, notes, records, routes = {}, [], [], {}, {}
    ignored = {'node_modules', '.git', 'venv', '.venv', '__pycache__', 'dist', 'build'}
    files = [p for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink()
             and not ignored.intersection(p.relative_to(root).parts)
             and p.suffix in {'.py', '.js', '.jsx', '.ts', '.tsx'}]
    if len(files) > 500:
        notes.append({'reason':'Source graph limited to 500 files; remaining files were not analyzed'})
    def edge(a, b, kind, basis='static'):
        item = {'from':a, 'to':b, 'kind':kind, 'basis':basis}
        if a in nodes and b in nodes and item not in edges:
            edges.append(item)
    def function(file, name, line, code, parent, tree=None):
        key = f'function:{file}:{name}'
        nodes[key] = {'id':key, 'kind':'test' if Path(file).name.startswith('test_') else 'function',
                      'file':file, 'function':name, 'label':name, 'line':line, 'code':code[:6000]}
        edge(parent, key, 'contains')
        records[(file, name)] = tree
        return key
    imports, source_bytes = {}, 0
    for path in files[:500]:
        check()
        file = path.relative_to(root).as_posix()
        if path.stat().st_size > 262144:
            notes.append({'file':file, 'reason':'Source exceeds 256 KiB graph limit'})
            continue
        try:
            source = path.read_text(encoding='utf-8')
        except UnicodeError:
            notes.append({'file':file, 'reason':'Source is not UTF-8'})
            continue
        source_bytes += len(source.encode('utf-8'))
        if source_bytes > 2 * 1024 * 1024:
            notes.append({'reason':'Source graph limited to 2 MiB of text; remaining files were not analyzed'})
            break
        module = f'module:{file}'
        nodes[module] = {'id':module, 'kind':'module', 'file':file, 'label':file}
        imports[file] = {}
        if path.suffix != '.py':
            for name, line, code in _js_functions(source):
                function(file, name, line, code, module)
            notes.append({'file':file, 'reason':'JS/TS coverage: named function declarations and literal fetch routes only; arrows, JSX event closures and dynamic URLs are unresolved'})
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            notes.append({'file':file, 'reason':'Python syntax could not be parsed'})
            continue
        for item in tree.body:
            if isinstance(item, ast.ImportFrom) and item.module:
                package = '.'.join(Path(file).with_suffix('').parts[:-item.level]) if item.level else ''
                base = package + '.' if package else ''
                for alias in item.names:
                    imports[file][alias.asname or alias.name] = (base + item.module, alias.name)
            elif isinstance(item, ast.Import):
                for alias in item.names:
                    imports[file][alias.asname or alias.name] = (alias.name, '')
        def walk(items, prefix='', parent=module):
            for item in items:
                if not isinstance(item, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                name = prefix + item.name
                code = '\n'.join(source.splitlines()[item.lineno - 1:item.end_lineno])
                if isinstance(item, ast.ClassDef):
                    key = f'class:{file}:{name}'
                    nodes[key] = {'id':key,'kind':'class','file':file,'label':name,'line':item.lineno}
                    edge(parent, key, 'contains')
                    walk(item.body, name + '.', key)
                    continue
                key = function(file, name, item.lineno, code, parent, item)
                doc = ast.get_docstring(item) or ''
                intent = re.search(r'Business Intent:\s*([^\n]+)', doc)
                if intent:
                    intent_id = 'intent:' + key
                    nodes[intent_id] = {'id':intent_id,'kind':'intent','label':intent.group(1),'file':file,
                                        'description':intent.group(1),'origin':'source_docstring'}
                    edge(key, intent_id, 'serves', 'source_declaration')
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute) and decorator.func.attr in {'get','post','put','patch','delete'} and decorator.args and isinstance(decorator.args[0], ast.Constant) and isinstance(decorator.args[0].value, str):
                        route = (decorator.func.attr.upper(), _path(decorator.args[0].value))
                        routes.setdefault(route, []).append(key)
                walk(item.body, name + '.', key)
        walk(tree.body)
    for (file, name), tree in records.items():
        check()
        key = f'function:{file}:{name}'
        if tree is None:
            code = nodes[key]['code']
            clean = _js_mask(code)
            real_fetch = {m.start() for m in re.finditer(r'(?<![.\w])fetch\s*\(', clean)}
            for match in re.finditer(r'fetch\s*\(\s*[\"\']([^\"\']+)[\"\']\s*(?:,\s*\{([^}]*))?', _js_mask(code, strings=False)):
                if match.start() not in real_fetch:
                    continue
                method = re.search(r'method:\s*[\"\'](\w+)', match.group(2) or '')
                targets = routes.get(((method.group(1) if method else 'GET').upper(), _path(match.group(1))), [])
                if len(targets) == 1:
                    edge(key, targets[0], 'calls_route', 'literal_route_match')
                elif targets:
                    notes.append({'file':file,'reason':'Ambiguous route; multiple definitions match this literal fetch; no edge inferred'})
            for other_file, other_name in records:
                if other_file == file and other_name != name and re.search(r'(?<![.\w])' + re.escape(other_name) + r'\s*\(', clean):
                    edge(key, f'function:{file}:{other_name}', 'calls', 'named_js_call')
            continue
        shadowed = {arg.arg for arg in (*tree.args.posonlyargs, *tree.args.args, *tree.args.kwonlyargs)}
        shadowed.update(_scope_bindings(tree))
        for call in (n for n in _body_nodes(tree) if isinstance(n, ast.Call)):
            target_file, target_name = file, None
            if isinstance(call.func, ast.Name) and call.func.id not in shadowed:
                target_name = call.func.id
                if target_name in imports[file]:
                    mod, target_name = imports[file][target_name]
                    target_file = mod.replace('.', '/') + '.py'
            elif isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
                owner = call.func.value.id
                if owner == 'self' and '.' in name:
                    target_name = name.rsplit('.', 1)[0] + '.' + call.func.attr
                elif owner in imports[file] and owner not in shadowed:
                    mod, imported = imports[file][owner]
                    target_file = mod.replace('.', '/') + '.py'
                    target_name = (imported + '.' if imported else '') + call.func.attr
                    imported_file = (mod.replace('.', '/') + '/' + imported + '.py') if imported else ''
                    if (imported_file, call.func.attr) in records:
                        target_file, target_name = imported_file, call.func.attr
            if target_name and (target_file, target_name) in records:
                edge(key, f'function:{target_file}:{target_name}', 'calls')
    changed = {(op['method'], _path(op['endpoint'])) for op in changed_operations}
    direct = set()
    for site in scan['sites']:
        if site.get('endpoint') is None:
            continue
        key = f"function:{site['file']}:{site['function']}"
        op = f"operation:{site['method']}:{site['endpoint']}"
        nodes[op] = {'id':op,'kind':'operation','method':site['method'],'endpoint':site['endpoint'],
                     'label':f"{site['method']} {site['endpoint']}"}
        if site.get('provider_id'):
            nodes[op].update(provider_id=site['provider_id'], display_endpoint=site['display_endpoint'],
                             label=f"{site['method']} {site['display_endpoint']} · {site['provider_id']}")
            for node in nodes.values():
                if node.get('file') == site['file']:
                    node['provider_id'] = site['provider_id']
        edge(key, op, 'consumes', 'scanner')
        if (site['method'], _path(site['endpoint'])) in changed:
            nodes[op]['impact'] = 'direct'
            if key in nodes:
                direct.add(key)
    for rule in requirements:
        rule_id = 'rule:' + rule['id']
        nodes[rule_id] = {'id':rule_id,'kind':'requirement','label':rule['description'], **rule}
        nodes[rule_id]['id'] = rule_id
        edge(f"function:{rule['scope']['file']}:{rule['scope']['function']}", rule_id, 'scopes', 'developer_declaration')
        for reference in rule.get('checks', []):
            parts = reference.split('::')
            edge(rule_id, f"function:{parts[0]}:{'.'.join(parts[1:])}", 'checked_by', 'developer_declaration')
    affected, queue = set(direct), deque(direct)
    while queue:
        check()
        key = queue.popleft()
        for item in edges:
            if item['to'] == key and item['kind'] in {'calls','calls_route'} and item['from'] not in affected:
                affected.add(item['from']); queue.append(item['from'])
    for key in affected:
        nodes[key]['impact'] = 'direct' if key in direct else 'potential'
        nodes[key]['impact_reason'] = 'Calls a changed API operation' if key in direct else 'Depends on an affected function; runtime failure is not established'
    for item in edges:
        if item['from'] in affected and item['kind'] in {'serves','scopes'}:
            nodes[item['to']]['impact'] = 'potential'
    notes.append({'reason':'Static relationships are bounded evidence, not complete runtime or field-level data-flow analysis'})
    return {'version':1, 'nodes':list(nodes.values()), 'edges':edges, 'notes':notes}
