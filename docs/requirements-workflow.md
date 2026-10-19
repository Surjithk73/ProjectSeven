# Business requirements in APIShield

A requirement records what your integration must preserve and which committed tests you selected to check it. A confirmed declaration is your review decision. A passing result means the selected tests actually passed on the candidate, not that the written sentence has been universally proved.

## Browser workflow

Select a connected project, then open **Settings → Project settings → Business rules**. Add a rule with an ID, description, repository-relative source file, exact scanner function name and one pytest reference per line. For example:

```json
{
  "id": "shipping-identity-weight",
  "description": "Preserve package identity and exact integer grams.",
  "scope": {"file": "src/parcel.py", "function": "create_label"},
  "origin": "developer",
  "confirmed": false,
  "checks": ["tests/test_parcel.py::test_shipping_preserves_package_and_weight"]
}
```

Save the draft, review the saved values and choose Confirm rule. Changed definitions become drafts again. Changing the repository, source directories or ordinary test directory also clears confirmation. A source-intent suggestion from a matching selected scan can seed a draft; inference never automatically establishes a confirmed rule. Source functions use the scanner's dotted lexical names, such as `Client.create_label` for a class method.

Examples and server-managed integrations expose read-only rules. Configure server-managed rules in their trusted integration JSON. The shipping example includes a confirmed rule and its real test. Original repository files and historical records are never changed by editing declarations.

## Validation and evidence

Only committed source/tests from the pinned revision are used. A repair first identifies affected calls and relevant confirmed rules. No linked checks, a missing file or an unresolved scope in an affected file yields needs_input. After configured setup, bounded pytest collection resolves the complete selected test function/class before any candidate generation. Missing selectors, collection errors or ambiguous capped output require input. This collection executes trusted test imports on the host; it shares the existing command/job budget and does not provide OS isolation.

Candidate validation runs ordinary configured tests and relevant selected checks separately. Selected checks must have exit zero, actual passing JUnit test records and no skips, failures or errors. Parameterized functions select all their cases. A skipped/xfailing check does not count. Cancellation or timeout cannot establish success. Protected source/test/config/contract inventories are checked after commands; candidate edits cannot target tests or rules.

Successful repair reports show Checks passed per rule and retain the patch. Failed checks prevent a validated patch. Unconfirmed statements remain non-binding, and unaffected confirmed rules are Not affected for that migration. Scan reports describe declarations and relationships but run no requirement checks.

Reports contain `requirements`, their canonical `requirements_hash`, a version-1 `requirement_graph`, and (for comparison/repair) `requirement_outcomes`. Attempts retain selected-check commands/results and discovery evidence; JUnit XML remains in the job evidence directory. Source operations are statically observed; scope/test edges are developer declarations. IDs are stable under unrelated line insertions, but endpoint changes and genuinely different calls can change identity. Current support is function/operation-level; field-flow, wrappers and transitive analysis remain pending.

## Configuration and API

Add a `requirements` list to config version 1; absent means empty. Each rule requires exactly the six keys in the example. IDs are unique, 1–64 letters/digits/hyphens/underscores; descriptions are nonempty and at most 2,000 characters. At most 100 rules and 30 distinct checks per rule are supported. Origins are `developer` or `source_intent`, with explicit boolean confirmation. Scopes must name Python files inside configured source paths. Checks accept a protected test file plus `::test_function` or `::TestClass::test_function`, without flags, traversal, absolute paths or parameter expressions.

The loopback-only browser endpoints are:

```text
GET /api/integrations/NAME/requirements
PUT /api/integrations/NAME/requirements
```

GET returns declarations, canonical `requirements_hash`, a full integration `edit_token` and editability. PUT accepts `{ "requirements": [...], "expected_hash": "GET edit_token" }`. The edit token includes integration context to reject stale editors after repository/settings changes, even when rule prose is unchanged. A conflict returns 409 and leaves your draft available; reload saved rules before retrying. New/changed rules save unconfirmed; a second request confirming the unchanged saved definition can set true. Browser-managed writes publish immutable config versions without changing past jobs or other integration settings. Server-managed configurations may declare their confirmation directly, under the existing trusted-admin boundary.

## Research and product limits

This mechanism makes developer declarations, localization and executable evidence traceable. It does not prove arbitrary prose, guarantee complete test coverage, establish a repair accuracy rate or demonstrate novelty. Controlled baselines/ablations and literature/prior-art assessment remain separate. No hosted monitoring, GitHub publication, Cloud migration or paid inference was added in this phase.
