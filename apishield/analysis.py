"""Conservative static coverage of direct requests/httpx GET and POST calls."""
import ast
from pathlib import Path
import re
from urllib.parse import urlsplit

from .configuration import relative_path


def _string(node, values):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return values.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _string(node.left, values), _string(node.right, values)
        return left + right if left is not None and right is not None else None
    if isinstance(node, ast.JoinedStr):
        parts = []
        for part in node.values:
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                parts.append(part.value)
            elif isinstance(part, ast.FormattedValue) and part.conversion == -1 and part.format_spec is None:
                value = _string(part.value, values)
                if value is None and isinstance(part.value, ast.Name):
                    value = '{' + part.value.id + '}'
                if value is None:
                    return None
                parts.append(value)
            else:
                return None
        return ''.join(parts)
    return None


def _endpoint(url):
    if url is None:
        return None
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in {'http', 'https'} or not parsed.netloc or '{' in parsed.netloc:
            return None
        return parsed.path or '/'
    except ValueError:
        return None


class _Scanner:
    def __init__(self, file, source):
        self.file, self.source = file, source
        self.sites, self.limitations = [], []

    def limitation(self, node, reason):
        self.limitations.append({'file': self.file, 'line': getattr(node, 'lineno', None), 'reason': reason})

    def calls(self, node, values, modules, direct, function, intent):
        def current_scope_nodes(current):
            if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda,
                                    ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                self.limitation(current, 'Nested lexical scope in an expression/compound statement is unsupported; endpoint not inferred')
                return
            yield current
            for child in ast.iter_child_nodes(current):
                yield from current_scope_nodes(child)

        for call in current_scope_nodes(node):
            if not isinstance(call, ast.Call):
                continue
            method = None
            if isinstance(call.func, ast.Attribute) and call.func.attr in {'get', 'post'}:
                if isinstance(call.func.value, ast.Name) and call.func.value.id in modules:
                    method = call.func.attr.upper()
                elif isinstance(call.func.value, ast.Name) and call.func.value.id in self.reassigned_imports:
                    self.limitation(call, 'HTTP import binding is reassigned at module scope; endpoint not inferred')
                else:
                    self.limitation(call, 'Wrapper or client-instance call unsupported; endpoint not inferred')
            elif isinstance(call.func, ast.Name):
                method = direct.get(call.func.id)
                if method is None and call.func.id in self.reassigned_imports:
                    self.limitation(call, 'HTTP import binding is reassigned at module scope; endpoint not inferred')
            if method is None:
                continue
            url_node = call.args[0] if call.args else next((kw.value for kw in call.keywords if kw.arg == 'url'), None)
            url = _string(url_node, values)
            endpoint = _endpoint(url)
            self.sites.append({'file': self.file, 'function': function, 'line': call.lineno,
                'method': method, 'endpoint': endpoint, 'intent': intent})
            if endpoint is None:
                self.limitation(call, 'Dynamic or unsupported URL; endpoint unknown')

    def body(self, body, values=None, modules=None, direct=None, function='<module>', intent=None, lexical=None):
        values, modules, direct = dict(values or {}), set(modules or ()), dict(direct or {})
        if function == '<module>':
            # Functions resolve module globals at call time. Resolve stable
            # assignments even when declared below a function, and refuse
            # reassigned/branch-dependent names instead of guessing old values.
            assignments, uncertain = {}, set()
            imported, network_imports, declarations = {}, set(), set()
            for statement in body:
                if isinstance(statement, ast.Import):
                    for alias in statement.names:
                        name = alias.asname or alias.name.split('.')[0]
                        imported[name] = imported.get(name, 0) + 1
                        if alias.name in {'requests', 'httpx'}:
                            network_imports.add(name)
                elif isinstance(statement, ast.ImportFrom):
                    for alias in statement.names:
                        name = alias.asname or alias.name
                        imported[name] = imported.get(name, 0) + 1
                        if statement.module in {'requests', 'httpx'} and alias.name in {'get', 'post'}:
                            network_imports.add(name)
                elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    declarations.add(statement.name)
                if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                    targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                    for target in targets:
                        if isinstance(target, ast.Name):
                            assignments.setdefault(target.id, []).append(statement.value)
                        else:
                            uncertain.update(n.id for n in ast.walk(target) if isinstance(n, ast.Name))
                elif not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    uncertain.update(n.id for n in ast.walk(statement) if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)))
            self.reassigned_imports = network_imports & (set(assignments) | uncertain | declarations
                | {name for name, count in imported.items() if count > 1})
            self.module_values = {}
            for _ in range(len(assignments) + 1):
                for name, expressions in assignments.items():
                    self.module_values[name] = _string(expressions[0], self.module_values) if len(expressions) == 1 and name not in uncertain else None
        for node in body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in {'requests', 'httpx'}:
                        modules.add(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module in {'requests', 'httpx'}:
                for alias in node.names:
                    if alias.name in {'get', 'post'}:
                        direct[alias.asname or alias.name] = alias.name.upper()
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node) or ''
                match = re.search(r'Business Intent:\s*([^\n]+)', doc)
                if lexical is not None:
                    # A class namespace does not enclose its methods. They
                    # resolve names in the enclosing function/module instead.
                    enclosing_values, enclosing_modules, enclosing_direct = lexical
                else:
                    enclosing_values = self.module_values if function == '<module>' else values
                    enclosing_modules, enclosing_direct = modules, direct
                local = dict(enclosing_values)
                arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
                if node.args.vararg:
                    arguments.append(node.args.vararg)
                if node.args.kwarg:
                    arguments.append(node.args.kwarg)
                shadowed = {arg.arg for arg in arguments}
                # A local assignment shadows a global throughout the function.
                shadowed.update(n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store))
                for name in shadowed:
                    local.pop(name, None)
                shadowed_bindings = shadowed | self.reassigned_imports
                self.body(node.body, local, set(enclosing_modules) - shadowed_bindings, {k: v for k, v in enclosing_direct.items() if k not in shadowed_bindings},
                    node.name if function == '<module>' else function + '.' + node.name,
                    match.group(1).strip() if match else None)
                values.pop(node.name, None); modules.discard(node.name); direct.pop(node.name, None)
            elif isinstance(node, ast.ClassDef):
                enclosing = lexical if lexical is not None else (
                    dict(self.module_values if function == '<module>' else values), set(modules), dict(direct))
                class_values, class_modules, class_direct = enclosing if lexical is not None else (values, modules, direct)
                self.body(node.body, class_values, class_modules, class_direct,
                    node.name if function == '<module>' else function + '.' + node.name, lexical=enclosing)
                values.pop(node.name, None); modules.discard(node.name); direct.pop(node.name, None)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                self.calls(node, values, modules, direct, function, intent)
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                value = _string(node.value, values)
                for target in targets:
                    for name in ast.walk(target):
                        if isinstance(name, ast.Name):
                            values[name.id] = value
                            modules.discard(name.id); direct.pop(name.id, None)
            elif isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)):
                # Avoid claiming branch-dependent constants are statically known.
                uncertain = {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
                for name in uncertain:
                    values[name] = None; modules.discard(name); direct.pop(name, None)
                self.calls(node, values, modules, direct, function, intent)
            else:
                self.calls(node, values, modules, direct, function, intent)
                for name in ast.walk(node):
                    if isinstance(name, ast.Name) and isinstance(name.ctx, (ast.Store, ast.Del)):
                        values[name.id] = None; modules.discard(name.id); direct.pop(name.id, None)


def scan_sources(workspace: Path, code_paths: list[str]) -> dict:
    root = Path(workspace).resolve()
    files = set()
    limitations = [{'file': None, 'line': None, 'reason':
        'Static coverage supports direct requests/httpx GET/POST only; wrappers, runtime mutation and other methods are unsupported'}]
    for configured in code_paths:
        path = root / relative_path(configured)
        if path.is_symlink() or (path.resolve() != root and root not in path.resolve().parents):
            raise ValueError('unsafe scan path')
        if not path.exists():
            limitations.append({'file': configured, 'line': None, 'reason': 'Configured source path is absent from pinned revision'})
            continue
        files.update([path] if path.is_file() and path.suffix == '.py' else path.rglob('*.py'))
    sites, scanned = [], []
    for path in sorted(files):
        if path.is_symlink() or root not in path.resolve().parents:
            raise ValueError('unsafe Python source path')
        name = path.relative_to(root).as_posix()
        if any(part in {'tests', 'test', '__pycache__', '.venv', 'venv'} for part in path.relative_to(root).parts) or path.name == 'conftest.py' or path.name.startswith('test_') or path.name.endswith('_test.py'):
            continue
        try:
            source = path.read_text(encoding='utf-8')
            tree = ast.parse(source, filename=name)
        except (UnicodeError, SyntaxError) as exc:
            limitations.append({'file': name, 'line': getattr(exc, 'lineno', None), 'reason': f'Unparseable Python source: {exc}'})
            continue
        scanner = _Scanner(name, source)
        scanner.body(tree.body)
        sites.extend(scanner.sites); limitations.extend(scanner.limitations); scanned.append(name)
    return {'sites': sites, 'files_scanned': scanned, 'limitations': limitations}
