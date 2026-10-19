"""MAPE-K loop with transactional candidates and explicit terminal outcomes."""
import datetime
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import TypedDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from langgraph.graph import StateGraph, START, END
from agent.monitor import get_api_diff, get_schema_context, is_breaking_change
from agent.analyzer import analyze_impact
from agent.planner import generate_patch_plan, revise_patch_plan, use_intent
from mcp_server import file_editor
from mcp_server.test_runner import run_tests_and_score_ips


def log_reasoning(stage: str, step: str, message: str, details: dict | None = None):
    entry = {'stage': stage, 'step': step, 'message': message, 'details': details or {}, 'timestamp': datetime.datetime.now().isoformat()}
    with (PROJECT_ROOT / 'agent/reasoning_log.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(entry) + '\n')


class AgentState(TypedDict, total=False):
    diff: str
    spec_diff: str
    schema_context: str
    impacted_sites: list[dict]
    patch_plans: list[dict]
    final_status: str
    healing_mode: str
    validation: dict
    ips_score: int | None
    ips_error: str | None
    pr_url: str
    pr_number: int
    error: str
    publication_error: str
    attempts: int
    config: dict


def run_config() -> dict:
    from config import get_model, get_setting
    trigger = get_setting('TRIGGER_REASON', 'break_detected')
    return {'model': get_model(), 'use_sig_context': use_intent(), 'trigger_reason': trigger, 'api_version': get_setting('API_VERSION', 'v3' if trigger == 'upgrade_available' else 'v2'), 'max_attempts': 3, 'ips_scoring': get_setting('ENABLE_IPS_SCORING', '0') == '1'}


def _validation_failure(message: str) -> dict:
    return {'tests_passed': False, 'test_output': message, 'ips_score': None, 'ips_error': None}


def _outcome(status: str, validation: dict | None = None, **extra) -> dict:
    evidence = validation or _validation_failure('Validation not run')
    return {'final_status': status, 'validation': evidence, 'ips_score': evidence.get('ips_score'), 'ips_error': evidence.get('ips_error'), 'config': run_config(), **extra}


def monitor_node(state: AgentState):
    from config import get_setting
    settings = run_config()
    log_reasoning('MONITOR', 'configuration', 'Starting contract comparison', settings)
    upgrade = settings['trigger_reason'] == 'upgrade_available'
    base = get_setting('BASE_SPEC', 'mock_provider/specs/v2_spec.json' if upgrade else 'mock_provider/specs/v1_spec.json')
    revised = get_setting('REVISED_SPEC', f'mock_provider/specs/{settings["api_version"]}_spec.json')
    try:
        raw = get_api_diff(base_spec=base, revised_spec=revised, mode='diff' if upgrade else 'breaking')
        if upgrade:
            report = json.loads(raw)
            changes = []
            paths = report.get('paths', {})
            for category in ('added', 'deleted', 'modified'):
                values = paths.get(category, {})
                for endpoint in values:
                    changes.append({'path': endpoint, 'type': f'path-{category}', 'details': values[endpoint] if isinstance(values, dict) else {}})
            diff = json.dumps(changes)
            if report and not changes:
                return _outcome('needs_input', error='Contract changed without an identifiable changed operation', spec_diff=raw, diff='')
        else:
            is_breaking_change(raw)  # validates the response structure
            diff = raw
        context = get_schema_context(base, revised)
        if not json.loads(diff):
            return _outcome('no_change', diff='', spec_diff=raw, schema_context=context)
        log_reasoning('MONITOR', 'oasdiff_result', 'Contract changes detected', {'diff': json.loads(diff)})
        return {'diff': diff, 'spec_diff': raw, 'schema_context': context, 'config': settings}
    except Exception as exc:
        log_reasoning('MONITOR', 'error', 'Contract comparison failed', {'error': str(exc)})
        return _outcome('failed', error=str(exc), diff='')


def analyze_node(state: AgentState):
    try:
        sites = analyze_impact(state['diff'])
        log_reasoning('ANALYZE', 'sig_query', f'Found {len(sites)} impacted call sites')
        return {'impacted_sites': sites}
    except Exception as exc:
        return _outcome('failed', error=f'Impact analysis failed: {exc}', impacted_sites=[])


def _group_sites(sites: list[dict]) -> dict:
    groups = {}
    for site in sites:
        path = file_editor.resolve_client_file(site.get('file'))
        groups.setdefault(path, []).append(site)
    return groups


def _intent(sites: list[dict]) -> str:
    return '; '.join(sorted({site.get('intent', '') for site in sites if site.get('intent')})) if use_intent() else ''


def plan_node(state: AgentState):
    if state.get('final_status') == 'failed':
        return {}
    plans = []
    try:
        groups = _group_sites(state.get('impacted_sites', []))
        if not groups:
            return _outcome('needs_input', error='No supported impacted call sites identified', patch_plans=[])
        for path, sites in groups.items():
            plan = generate_patch_plan(state['diff'], file_editor.read_source(path), _intent(sites), run_config()['trigger_reason'], schema_context=state.get('schema_context', ''))
            if plan.get('needs_input'):
                return _outcome('needs_input', error=str(plan['needs_input']), patch_plans=[])
            plan['file'] = str(path)
            plans.append(plan)
            log_reasoning('PLAN', 'patch_generated', f'Generated candidate for {path.name}')
        return {'patch_plans': plans}
    except Exception as exc:
        return _outcome('failed', error=f'Planning failed: {exc}', patch_plans=[])


def _client_files(root: Path) -> set[Path]:
    return {path for path in root.rglob('*') if path.is_file() and path.resolve().is_relative_to(root.resolve()) and not any(part in ('.git', '__pycache__', '.pytest_cache') for part in path.relative_to(root).parts)}


def _restore(root: Path, originals: dict[Path, bytes]):
    for path in _client_files(root) - originals.keys():
        path.unlink()
    for path, raw in originals.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def apply_github_patch(**kwargs):
    # Optional integration cannot make local startup depend on PyGithub.
    from mcp_server.github_editor import apply_github_patch as publish
    callable_publish = publish if callable(publish) else publish.fn
    return callable_publish(**kwargs)


def execute_node(state: AgentState):
    if state.get('final_status') in ('failed', 'needs_input'):
        return {}
    plans = state.get('patch_plans', [])
    if not plans:
        return _outcome('needs_input', error='No candidate patches were generated', attempts=0)
    root = file_editor.CLIENT_ROOT
    try:
        paths = {file_editor.resolve_client_file(plan.get('file')) for plan in plans}
        originals = {path: path.read_bytes() for path in _client_files(root)}
    except Exception as exc:
        return _outcome('failed', error=str(exc), attempts=0)
    validation = _validation_failure('Validation not run')
    intent = _intent(state.get('impacted_sites', []))
    for attempt in range(1, 4):
        log_reasoning('EXECUTE', 'attempt', f'Candidate attempt {attempt}/3', {'config': run_config()})
        try:
            _restore(root, originals)
            applied = file_editor.apply_patch_group(plans)
            if applied.startswith('Error'):
                validation = _validation_failure(applied)
            else:
                raw_validation = run_tests_and_score_ips(original_intent=intent, api_version=run_config()['api_version'])
                validation = {'tests_passed': raw_validation.get('tests_passed') is True, 'test_output': str(raw_validation.get('test_output', '')), 'ips_score': raw_validation.get('ips_score'), 'ips_error': raw_validation.get('ips_error')}
                score = validation['ips_score']
                if score is not None and (type(score) is not int or not 0 <= score <= 100):
                    validation['ips_score'] = None
                    validation['ips_error'] = 'Invalid IPS score from validator'
            log_reasoning('VALIDATE', 'evidence', 'Candidate validation completed', validation)
            if validation['tests_passed']:
                result = _outcome('validated', validation, attempts=attempt, patch_plans=plans)
                if state.get('healing_mode') == 'github':
                    if len(paths) > 1:
                        return _outcome('needs_input', validation, attempts=attempt, patch_plans=plans, error='Local candidate validated. Multi-file GitHub proposals require the Phase 4 publisher.')
                    try:
                        path = next(iter(paths))
                        published = apply_github_patch(file_path=str(path), patch_code=file_editor.read_source(path), original_intent=intent, ips_score=validation['ips_score'])
                        if published.get('status') == 'success' and published.get('pr_url'):
                            result.update(final_status='pr_opened', pr_url=published['pr_url'], pr_number=published.get('pr_number', 0))
                        else:
                            result['publication_error'] = published.get('message', 'GitHub publication failed')
                    except Exception as exc:
                        result['publication_error'] = str(exc)
                return result
        except Exception as exc:
            validation = _validation_failure(f'Candidate execution failed: {exc}')
        # Revisions always see the exact same restored base as application.
        try:
            _restore(root, originals)
            if attempt == 3:
                break
            groups = {}
            for plan in plans:
                path = file_editor.resolve_client_file(plan['file'])
                groups.setdefault(path, []).append(plan)
            revised = []
            for path, failed_plans in groups.items():
                new_plan = revise_patch_plan(failed_plan=failed_plans[0] if len(failed_plans) == 1 else {'patches': failed_plans}, test_output=validation['test_output'], target_code=file_editor.read_source(path), business_intent=intent, api_diff=state.get('diff', ''), schema_context=state.get('schema_context', ''))
                if new_plan.get('needs_input'):
                    return _outcome('needs_input', validation, error=str(new_plan['needs_input']), attempts=attempt, patch_plans=plans)
                new_plan['file'] = str(path)
                revised.append(new_plan)
            plans = revised
        except Exception as exc:
            _restore(root, originals)
            return _outcome('failed', validation, error=f'Replanning failed: {exc}', attempts=attempt, patch_plans=plans)
    _restore(root, originals)
    return _outcome('failed', validation, error='Repair exhausted its three candidate attempts', attempts=3, patch_plans=plans)


builder = StateGraph(AgentState)
for name, node in [('monitor', monitor_node), ('analyze', analyze_node), ('plan', plan_node), ('execute', execute_node)]:
    builder.add_node(name, node)
builder.add_edge(START, 'monitor')
builder.add_conditional_edges('monitor', lambda state: 'analyze' if state.get('diff') and not state.get('final_status') else END)
builder.add_conditional_edges('analyze', lambda state: END if state.get('final_status') == 'failed' else 'plan')
builder.add_conditional_edges('plan', lambda state: END if state.get('final_status') in ('failed', 'needs_input') else 'execute')
builder.add_edge('execute', END)
app = builder.compile()


def write_result(result: dict, path: Path | None = None):
    destination = path or PROJECT_ROOT / 'agent/result.json'
    descriptor, temporary = tempfile.mkstemp(prefix='.result-', suffix='.json', dir=destination.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    os.chdir(PROJECT_ROOT)
    (PROJECT_ROOT / 'agent/reasoning_log.jsonl').write_text('', encoding='utf-8')
    initial = {'diff': '', 'impacted_sites': [], 'patch_plans': [], 'healing_mode': sys.argv[1] if len(sys.argv) > 1 else 'webhook', 'pr_url': '', 'pr_number': 0, 'config': run_config()}
    try:
        result = app.invoke(initial)
    except Exception as exc:
        result = {**initial, **_outcome('failed', error=str(exc))}
    write_result(result)
    print('Final State Status:', result['final_status'])
    return 1 if result['final_status'] in ('failed', 'needs_input') else 0


if __name__ == '__main__':
    sys.exit(main())
