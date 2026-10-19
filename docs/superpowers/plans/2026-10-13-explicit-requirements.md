# Explicit Requirements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native execution, or superpowers:subagent-driven-development if the user selects it. Steps use checkbox syntax for tracking.

**Goal:** Give developers a browser workflow for declaring business requirements and enforcing their independently selected tests before publishing a validated repair.

**Architecture:** Add strict optional requirement declarations to existing integration snapshots. A small requirements module builds operation/source/test evidence and determines applicability; the existing engine runs separate selected pytest checks with the same integrity, timeout and cancellation controls. Existing local registration and React components expose the declarations and immutable run outcomes.

**Tech Stack:** Python standard library, existing FastAPI/Pydantic, pytest, React/Lucide and CSS; no new runtime dependencies.

**Spec:** [Approved requirements design](../specs/2026-10-12-explicit-requirements-design.md).

## Global constraints

- Local application only, no authentication, no Cloud migration or live model requests.
- Reuse the attached `codex/phase1-foundation` worktree; preserve the original checkout and nested `client_app` repository. No merge, push or publication.
- Optional `requirements` in config version 1; absent means empty and existing test-only validation remains supported.
- IDs: letters/digits/hyphens/underscores, at most 64 characters, unique within the integration. Description: nonempty, at most 2,000 characters.
- Explicit origins `developer` and `source_intent`; inferred prose is unconfirmed and cannot become a trusted gate automatically.
- Confirmation is a developer declaration, not proof. Only passing linked executable checks count as validation evidence.
- Never edit original source, tests, configuration or contracts to make a candidate pass. All checks share the existing job budget.
- Inherit the existing migration review desk design, labels, responsiveness and keyboard focus.

## Review focus

- A confirmed scope no longer resolving in an affected file must not silently become irrelevant: engine tests in Task 2.
- Pytest returning zero with skips, xfails or no actual passing test cases must not satisfy a rule: selected-check tests in Task 2.
- Editing descriptions/scopes/checks must require renewed confirmation; a stale editor must not overwrite newer declarations: API/frontend tests in Tasks 3–4.
- Source-call identities must remain stable under unrelated line insertions, while duplicate calls stay distinct: graph tests in Task 1.
- Read-only examples/server integrations and historical runs must remain protected when rules change: API/acceptance tests in Tasks 3–4.

## Files and interfaces

| File | Responsibility |
| --- | --- |
| `apishield/requirements.py` (new) | Strict declarations, deterministic hashes, source/operation/test graph, applicability and bounded pytest-result interpretation |
| `apishield/configuration.py` | Optional requirement loading and serialization |
| `apishield/engine.py` | Snapshot evidence, preflight gates, selected checks and final acceptance |
| `apishield/browser_setup.py` | Read/update rules through local guarded, immutable registration versions |
| `frontend/src/components/Requirements.jsx` (new) | Saved rule list, editor, confirmation, source-intent adoption and read-only states |
| `frontend/src/pages/Workspace.jsx` | Requirements section and per-run outcomes, using existing selection guards |
| `frontend/src/workspace.js`, `frontend/src/workspace.css` | Small form-state helpers where needed and scoped styles |
| `tests/test_requirements.py` (new) | Strict data/graph and pytest evidence regressions |
| `tests/test_local_engine.py`, `tests/test_browser_setup.py` | Real offline transactions and local API persistence/boundaries |
| `frontend/tests/requirements.test.js` (new) | Confirmation/editing and outcome presentation behavior |
| `examples/shipping/integration.json`, relevant docs | Real example rules, usage, limits and final verification ledger |

Requirements module interfaces:

- `validate_requirements(value: object, code_paths: list[str]) -> list[dict]`: normalized declarations; rejects unknown keys and unsafe selectors. Scope functions use the scanner's dotted lexical names (or `<module>`). Checks accept `tests/test_file.py::test_name` and optional `::TestClass::test_name`, without parameter suffixes or options.
- `requirements_hash(requirements: list[dict]) -> str`: SHA-256 of canonical JSON; same snapshot has the same hash.
- `build_requirement_graph(scan: dict, requirements: list[dict], source: dict) -> dict`: version 1, nodes, typed edges, unresolved notes and unconfirmed source-intent suggestions. Node IDs derive from semantic identity; lines remain evidence.
- `requirement_outcomes(requirements: list[dict], scan: dict, impacted_sites: list[dict], workspace: Path) -> list[dict]`: applicability and preflight states for the pinned source; affected unresolved scopes and missing checks/files return `needs_input`.
- `read_check_result(path: Path, exit_code: int) -> dict`: bounded JUnit XML parsing, actual passing records and rejection of missing/malformed, failed/error/skipped/xfail evidence. A selected test reference must yield at least one passing test case with no non-passing records.

API:

- `GET /api/integrations/{name}/requirements` returns declarations, their hash and editability for any configured integration.
- `PUT /api/integrations/{name}/requirements` accepts `{requirements, expected_hash}`. Only browser-owned integrations may mutate; stale hashes return 409. Unknown/unsafe declarations return 422. Save a new immutable configuration under the existing registry lock; preserve all other settings/contracts and past jobs.
- Rule creation/changed definitions initially save unconfirmed. A subsequent explicit confirmation of the saved unchanged definition can set `confirmed: true`; API enforcement prevents clients from retaining stale confirmation. The UI explains this two-step rule review.
- Existing full integration edits preserve saved requirements and their identity; source-path changes incompatible with declarations fail with a clear recovery error rather than dropping rules.

## Task 1 — Strict requirements and traceable graph

- [x] Write `test_requirements_legacy_config_defaults_empty`, `test_requirement_config_roundtrip`, and parametrized rejection tests for duplicate IDs, unknown keys, invalid booleans/origins, blank/oversized descriptions, traversal, absolute/option selectors and source scopes outside configured paths. Assert legacy load succeeds and `requirements == []`; malformed declarations raise `ValueError`.
- [x] Write graph tests: operation/source/requirement/test edges identify their declared versus scanner origin; identical scans produce identical IDs; adding blank lines preserves IDs; two identical calls have distinct IDs; unresolved URLs/scopes remain notes; source intent produces only `confirmed == False` suggestions.
- [x] Run these tests and observe assertion failures before implementing the interfaces above. Add the module and optional configuration field, keeping config version 1. Use existing path checks and standard-library hashing/JSON rather than new infrastructure.
- [x] Run focused tests to green and existing configuration/scanner tests; commit the independently usable declaration/graph support.

## Task 2 — Enforce requirement checks in the shared engine

- [x] Extend the real shipment fixture with separate ordinary and requirement tests. Write `test_correct_repair_passes_declared_requirement`: final status is `validated`, outcome is `passed`, graph/snapshot/hash exist, original source is unchanged and retained patch independently applies.
- [x] Write `test_wrong_units_pass_ordinary_tests_but_fail_requirement` and a refund-to-charge fixture equivalent. Ordinary evidence must have exit zero; requirement outcome must be `failed`; final patch must be absent. Verify exact integer values, requested user identity, transport call and refund endpoint rather than schema shape alone.
- [x] Write preflight tests for no checks, missing committed test, unresolved scope in an affected file and untracked-only tests. Assert `needs_input` names the requirement and candidate generation is never called. Confirm unaffected functions are `not_applicable` and unconfirmed suggestions are not gates.
- [x] Write JUnit interpretation tests for empty, oversized (>1 MiB), malformed, missing, failed/error/skipped/xfail records, plus actual parametrized passing selected tests. Pass requires real passing records and exit zero. Exercise configured-check selection with pytest options/traversal rejected by Task 1.
- [x] Observe RED. Integrate graph and canonical requirements hash after scanning; store immutable requirements/outcomes in reports. Before attempts, gate relevant confirmed rules. After ordinary tests, run each selected reference separately with `python -m pytest`, a server-generated JUnit path outside source and no browser-provided options. Parse evidence and apply existing integrity/deadline/cancellation checks after every command.
- [x] Include confirmed applicable requirements in generation context only when `use_intent` is enabled; still enforce checks in every mode. Include requirement failures in existing bounded retry feedback. Keep candidate path behavior deterministic and never invoke inference for offline proposals.
- [x] Run meaningful candidate-test mutation, timeout, cancellation and legacy engine regressions along with the new tests; commit once green.

## Task 3 — Persistent local browser requirements

- [x] Write API tests covering create/read/update, two-step confirmation, edits clearing confirmation, duplicate/unsafe rejection, stale-hash 409, foreign Origin/Host rejection, read-only server integrations/examples, full integration edits preserving rules, failed-save registry integrity and restart persistence.
- [x] Prove an existing job's saved rules/hash/outcomes stay byte-identical after editing current integration requirements. Test old example installations receive a new safe configuration version with the shipping rule without altering pinned source/tests or old records.
- [x] Observe RED. Add guarded requirement endpoints and common immutable publication logic by reusing the registry lock, strict config loader and atomic writer. Preserve configured model/ref/commands/environment/budgets and absolute contract references. Do not expose arbitrary commands.
- [x] Add one read-only shipping requirement for `src/parcel.py`, function `create_label`, checked by `tests/test_parcel.py::test_shipping_preserves_package_and_weight`. These paths exist in the shipped fixture. Refresh only server-owned example configurations when needed.
- [x] Run API tests and real shipping offline repair with requirement outcomes; commit once green.

## Task 4 — Browser workflow and delivery

- [x] Write frontend behavior tests: changing rule definitions clears confirmation, source-intent adoption remains draft, failed/stale save retains input, and `passed` display requires actual run evidence. Test read-only/empty/needs-input states and legacy reports without new fields.
- [x] Observe RED. Add the Requirements component in the selected integration view, with native labeled controls, saved rules, per-rule test references, explicit confirm action and source-intent adoption from a matching selected scan. Use selection generations so late integration/rule responses cannot replace a newer selection.
- [x] Add requirement outcomes and source/test relationships to Findings as readable rows with expandable command evidence; do not introduce a decorative graph or unverified success scores. Keep long paths and diagnostics usable at mobile width.
- [x] Run frontend tests, lint and production build. Run the full offline Python suite once after integration. Fix concrete failures using regression tests, then rerun the affected checks.
- [x] Restart the local app and exercise browser creation/edit/confirm, scan/compare/offline example repair, failed-save recovery and persistence. Inspect desktop and mobile captures, keyboard labels/focus, long text and confirmation/status semantics.
- [x] Request one independent whole-change review (native execution). Address important defects in one regression-driven fix pass; record deferred minor findings. Update usage/product/status docs and a phase ledger with actual evidence, research limitations and remaining field-level analysis work.
- [x] Commit owned changes, confirm clean worktree/nested repository, leave the app usable locally and link the outcome report. Do not merge, deploy, publish or make paid calls.

## Self-review and execution handoff

Every approved spec section maps to a task: declarations/graph/suggestions (1), enforcement/evidence (2), immutable local ownership (3), browser/research truth and verification (4). The five review-focus risks have explicit tests. Confirmation and stale-edit semantics are pinned above; no new dependencies or automatic semantic proof are implied. Full field-level analysis, hosting, monitoring and GitHub proposals remain excluded.

Execution approved and completed: native implementation with one fresh final reviewer. These four tasks share configuration, report and API interfaces, so serial implementation avoided integration churn while retaining independent review of the final acceptance gate. Review refined the concurrency contract: GET also returns a full-config `edit_token`; PUT's `expected_hash` must use that token. Declaration-only `requirements_hash` remains the immutable rule-set identity in reports. Changing repository/source/test context clears confirmation. See docs/requirements-progress.md and docs/requirements-validation.md for RED→GREEN evidence and completed tasks.
