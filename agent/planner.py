"""Schema-guided planning with an explicit intent ablation."""
import ast
import json


def use_intent() -> bool:
    from config import get_setting
    return get_setting('USE_SIG_CONTEXT', '1') == '1'


def strip_intent_docstrings(source: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    for node in ast.walk(tree):
        body = getattr(node, 'body', None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            expression = body[0]
            for index in range(expression.lineno - 1, expression.end_lineno):
                lines[index] = '\n' if lines[index].endswith('\n') else ''
    return ''.join(lines)


RULES = '''Rules:
1. Preserve numeric arguments exactly; never divide, convert units or invent unavailable data.
2. Preserve all existing function signatures and their behavior.
3. old_code_snippet must be an exact, unique substring of the CURRENT FILE.
4. Make only changes supported by the target schema. Missing required data or ambiguous migrations require developer input.
Return ONLY JSON: {"old_code_snippet":"exact original substring","new_code_snippet":"replacement"}.
If missing information prevents a correct repair return {"needs_input":"explanation"}.
'''


def _generate(prompt: str) -> dict:
    from contextlib import nullcontext
    from config import get_genai_client, get_model
    from google.genai import types
    raw = get_genai_client()
    cm = raw if hasattr(raw, '__enter__') else nullcontext(raw)
    with cm as client:
        response = client.models.generate_content(model=get_model(), contents=prompt, config=types.GenerateContentConfig(response_mime_type='application/json'))
    plan = json.loads(response.text.strip())
    if not isinstance(plan, dict):
        raise ValueError('Patch response must be a JSON object')
    return plan


def generate_patch_plan(api_diff: str, target_code: str, business_intent: str = '', trigger_reason: str = 'break_detected', schema_context: str = '') -> dict:
    aware = use_intent()
    code = target_code if aware else strip_intent_docstrings(target_code)
    intent = f'Business intent to preserve: {business_intent}\n' if aware else ''
    task = 'Adopt the developer-requested additive upgrade.' if trigger_reason == 'upgrade_available' else 'Repair the API contract migration.'
    return _generate(f'{task}\n{intent}API diff:\n{api_diff}\nBase and target API schemas:\n{schema_context}\nCURRENT FILE:\n{code}\n{RULES}')


def revise_patch_plan(failed_plan: dict, test_output: str, target_code: str, business_intent: str = '', api_diff: str = '', schema_context: str = '') -> dict:
    aware = use_intent()
    code = target_code if aware else strip_intent_docstrings(target_code)
    # Previous patches and tracebacks may quote removed labels and docstrings.
    feedback = f'Business intent to preserve: {business_intent}\nPrevious patch:\n{json.dumps(failed_plan)}\nTest failure:\n{test_output[-6000:]}\n' if aware else 'Previous candidate failed validation; generate a new candidate against the restored CURRENT FILE.\n'
    return _generate(f'Revise a failed API repair.\n{feedback}API diff:\n{api_diff}\nBase and target API schemas:\n{schema_context}\nCURRENT FILE:\n{code}\n{RULES}')
