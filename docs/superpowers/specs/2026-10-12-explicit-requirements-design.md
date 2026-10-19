# Explicit business requirements and repair validation

Status: approved and implemented on 13 October 2026. See docs/requirements-validation.md for actual verification and the reviewed full-context concurrency refinement.

## Intent and scope

The user approved advancing explicit business requirements and their validation, while deferring Google Cloud migration and live AI testing. Developers must be able to state what an integration must preserve, confirm those requirements, connect existing tests to them, and inspect the resulting repair evidence in the browser. Keep the current local application, no authentication, existing Python/OpenAPI subset and unchanged original repositories.

Success is a complete offline browser workflow: save a requirement, associate it with consuming code and a committed test, compare contracts, validate a supplied repair, and see whether that requirement passed, failed or lacked evidence. Text is not an executable assertion. Confirmation means a developer accepts the rule, not that its behavior has been proved.

This increment supplies the requirement model, source/operation/test relationships and an acceptance gate. It does not claim complete program analysis, automatic synthesis of semantic checks, academic novelty or universal intent preservation.

## Approaches considered

1. **Requirements linked to existing pytest tests — recommended.** Reuses the current validator, protects tests from candidate edits and gives developers inspectable evidence. A developer must supply a meaningful test for a confirmed rule.
2. **Natural-language requirements supplied only to generation.** Cheap to add but does not enforce behavior; retain text as context, never as the acceptance mechanism.
3. **A new constraint language and generated tests.** Potential future research, but currently introduces a second validation system and requires proving the language/check generation sound. Defer until real requirements exceed existing tests.

## Stored requirement contract

Add an optional `requirements` array to integration configuration version 1. Missing means an empty array, preserving existing integrations and reports. Each entry contains:

| Field | Meaning |
| --- | --- |
| `id` | Developer-facing unique identifier within this integration; letters, digits, hyphens and underscores, maximum 64 characters |
| `description` | Nonempty business rule, maximum 2,000 characters |
| `scope.file` | Exact repository-relative Python source path inside configured source paths |
| `scope.function` | Exact function name from the supported source scanner |
| `origin` | `developer` or `source_intent`; inferred suggestions remain distinguishable |
| `confirmed` | Explicit boolean developer confirmation |
| `checks` | Zero or more restricted pytest node IDs referring to committed test functions |

Reject duplicate IDs, unknown keys, empty values, traversal, absolute paths, command options and malformed test references. Test references name a test file and test function, with an optional test class; they never accept shell commands, pytest flags or arbitrary expressions. Referenced files must be protected test files outside editable source targets. Validation against the exact pinned checkout occurs at execution, because local files may differ from the committed revision.

Changing a rule's description, scope or checks clears its browser confirmation and requires reconfirmation. The browser labels the confirmation as a developer declaration. Store the complete requirement configuration in each immutable job snapshot; editing an integration cannot alter past evidence. Record a canonical requirements hash in reports to identify the exact rule set.

## Linking requirements to code and operations

Build a small versioned evidence graph from the existing scan and requirement declarations, with no graph database or new visualization dependency. Nodes represent requirements, supported call sites, API operations and declared test references. Edges distinguish:

- Scanner-observed consuming call → operation, with file, function, line and source revision.
- Developer-declared requirement → matching source call, with origin and confirmation.
- Developer-declared requirement → test reference; declaration alone does not prove that the test checks the prose.

Use deterministic IDs from node kind and semantic identity; call identities exclude line numbers so inserting unrelated lines does not replace a call's identity. Distinguish repeated identical calls by ordinal within the function. Identities are scoped to an integration; endpoint changes can legitimately change operation/call identities across revisions. Keep line locations as evidence, not identity.

Unmatched scopes, unresolved URLs and missing tests produce explicit coverage notes rather than fabricated edges or numerical confidence scores. The first increment links whole operations and consuming functions. Automatic field-level data flow and transitive wrapper analysis remain outside the supported analysis subset.

Existing `Business Intent` comments may appear as unconfirmed suggestions in scan results. Never automatically convert prose into a trusted requirement. A developer can adopt a suggestion, edit its scope, connect tests and confirm it.

## Repair acceptance

1. Scan the pinned checkout and retain its evidence graph and requirement snapshot.
2. Compare contracts and identify affected call sites using the existing engine.
3. Select confirmed requirements whose scoped consuming functions intersect affected calls. Requirements on unaffected functions are reported as not applicable for this migration. A scope that cannot be resolved in an affected file must be reviewed rather than silently omitted.
4. Before attempting a repair, a relevant confirmed requirement with no checks, unresolved scope or missing committed test returns `needs_input`, identifying the rule and recovery action.
5. Apply an allowed candidate in a disposable checkout and run ordinary configured validation as today. Run each relevant requirement's selected tests separately through the existing bounded command runner. Candidate edits may not alter requirements, test files, contracts or configuration.
6. Preserve per-requirement command evidence. Require actual collected, passing checks: zero collected tests, skipped checks, errors, failures, timeouts or cancellation cannot satisfy a requirement. Use bounded pytest result evidence to distinguish these cases, rather than accepting exit code zero alone.
7. Publish a validated patch only when configured tests and every relevant confirmed requirement's checks pass. A failure names the rule and retains evidence without exposing a validated patch. Retry feedback includes failed checks within the existing attempt/deadline budget.

Relevant unconfirmed suggestions remain visible but are not acceptance gates. Reports clearly state which confirmed rules were checked and which statements remained unconfirmed. Existing integrations with no requirements retain ordinary test validation, labeled as such; do not imply semantic guarantees were added to historical jobs.

An explicit offline candidate returning a useful `needs_input` diagnostic demonstrates missing-customer-data handling without paid inference. A written requirement alone cannot detect unavailable real-world data or prove a generator will abstain; preserve that limitation.

## Browser experience

Preserve the current migration review desk visual system: white/slate surfaces, restrained violet actions, native controls and responsive layout. Add a Requirements section for the selected integration rather than redesigning the app shell.

- Empty state explains why rules matter and gives a concrete example: “Preserve the exact integer weight supplied by the caller.”
- Add/edit fields: ID, description, source file/function, existing test reference(s), explicit confirmation checkbox. Explain that a check must be committed and runnable with the app's pytest environment.
- Inferred source intent is visibly “Suggested — review required”; adopting it does not imply verification.
- Show saved rules with source scope, confirmation and linked tests. Rule editing/removal publishes a new integration snapshot and leaves previous runs intact.
- Browser-created integrations are editable. Server-managed integrations expose read-only requirements and guidance to update their trusted config; the browser cannot override the server allowlist.
- Read-only examples include a confirmed shipping identity/weight requirement linked to the shipped test. Existing installed example configurations require a safe configuration refresh, without changing the fixture's committed source or prior runs.
- Run reports show requirement outcomes (`passed`, `failed`, `needs_input`, `not_applicable`, `unconfirmed`) alongside the affected source and test evidence. Unchecked text never receives a green verified indicator.
- Long IDs, paths and diagnostic text wrap on mobile. Provide labeled controls, visible keyboard focus, loading, empty, save-error and validation-error states. Saving must finish successfully before closing the editor.

No arbitrary command editor, AI requirement generation, authentication or hosted operation is added.

## Offline completion checks

- Existing configurations, CLI and browser workflows remain compatible.
- A correct endpoint migration passes ordinary and explicitly linked requirement checks; original source remains unchanged and the patch applies independently.
- A unit-conversion candidate passing a deliberately weak ordinary suite fails the separate exact-integer requirement check.
- A refund-to-charge candidate passing ordinary schema checks fails the declared refund behavior check.
- Missing checks/scopes/files and skipped or empty selected tests cannot produce requirement-validated patches.
- Unconfirmed inferred intent never becomes a gate; relevant confirmed rules cannot be silently dropped.
- Malformed references, traversal, pytest options and protected test edits are rejected.
- Saved requirements survive restart; edits clear confirmation and do not change historical snapshots, graphs or evidence.
- Browser create/edit/confirm/report flows work at desktop and mobile widths; build, lint and relevant automated suites pass.
- The shared CLI/service engine performs the checks; no separate browser-only validator exists and normal tests make no model calls.

## Research interpretation and later work

This is a mechanism for traceable developer-declared constraints checked by independent executable tests. It enables later comparisons against schema/source-only and ordinary-test-guided repair. It does not establish those comparisons yet. Full benchmark expansion, automated field-level inference, literature/prior-art assessment, monitoring, GitHub proposals, hosting and live model evaluation remain separate milestones.

## Review notes

The existing architecture provides configuration snapshots, conservative source scanning, protected test files, immutable browser configuration versions and bounded commands. Reuse these mechanisms. The main trade-off is requiring developers to connect existing tests, in exchange for enforceable evidence rather than an unverified prose score. Self-review checked acceptance semantics, old integration compatibility, uncertainty, browser permission boundaries and skipped-test behavior; no placeholders or unresolved product choices remain in this specification.
