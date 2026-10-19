# APIShield implementation plan

Status: Phases 1 and 2 completed. Local browser onboarding, job review and the revamped frontend are implemented on the attached worktree; see docs/browser-workflow-validation.md. Phase 3's explicit requirement declarations, function/operation/test links and acceptance checks are implemented; see docs/requirements-workflow.md. Local contract monitoring is complete, including scheduled comparison, immutable snapshots, change deduplication, explicit baseline acceptance and code rescans; see docs/local-monitoring.md. GitHub draft proposals, deeper supported field/caller analysis and per-integration environment setup remain pending. AI integration/live testing, controlled research evaluation, patent work, hosting and early trials are deferred by the user's current scope.
Prepared: 11 October 2026.

## 1. What we are building

APIShield will help a development team maintain REST API integrations. It will detect a changed API contract, identify the affected code and business behavior, prepare a repair in an isolated workspace, validate it, and propose a reviewed pull request.

Customer promise: **Understand which API changes affect your application and receive a tested migration proposal.**

Research objective: evaluate whether graph-linked, explicit behavioral constraints reduce incorrect repairs compared with schema-guided and test-guided repair.

A working product does not establish academic novelty or patentability. Literature and patent prior-art assessment remain separate workstreams. Research results will describe measured behavior and limitations rather than claim universal correctness.

## 2. First-release boundaries

Supported initially:

- GitHub repositories containing Python REST integrations.
- Direct `httpx` and `requests` GET/POST calls in a documented supported subset; unsupported wrappers and dynamic expressions produce an explicit limitation.
- OpenAPI contracts uploaded by a user or fetched from an approved URL.
- Configurable source directories, dependency setup, test commands, and monitoring intervals.
- Field renames, endpoint changes, payload nesting changes, and response nesting changes when the migration is sufficiently specified.
- Developer-confirmed behavioral requirements.
- Impact reports, validated patch proposals, and draft pull requests.

Changes requiring unavailable data or ambiguous semantics request developer input. The tool must not invent a billing address, silently change monetary units, or substitute a charge for a refund.

Later scope: additional languages, specification inference, production telemetry, proactive feature adoption, automatic merging/deployment, and fully self-hosted distribution. These are excluded from the first release to keep the initial result measurable.

SwiftPay and NexusPay become maintained examples and regression fixtures. APIShield becomes the customer-facing product.

## 3. Customer experience

1. A team signs in and authorizes APIShield for selected repositories.
2. They create an integration, provide its OpenAPI source, and configure installation and test commands.
3. APIShield scans the code and shows the discovered operations and workflows.
4. A developer confirms inferred requirements or supplies missing ones.
5. APIShield checks the contract periodically and on supported events.
6. A change produces an impact report. Irrelevant changes are recorded without opening unnecessary repair jobs.
7. A repair worker checks out a specific commit, prepares a candidate patch, and runs validation.
8. The team receives a draft PR or a clear explanation of what information is missing.
9. Their normal review, CI, and deployment processes handle acceptance and release.

Customers do not need to keep their laptops running. The hosted service schedules work. A later customer runner can execute jobs inside a company's CI or cloud infrastructure.

Checking a specification detects documented contract changes. Undocumented behavioral changes require other evidence; the first release must not advertise complete runtime coverage.

## 4. Architecture in plain language

| Part | Purpose | Implementation direction |
| --- | --- | --- |
| Web application | Setup, integration inventory, findings, requirements, jobs, and evidence | Adapt the existing React APIShield frontend |
| Service API | Validates requests, stores configuration, and exposes results | Refactor the existing FastAPI backend |
| Database | Remembers projects and job history after restarts | SQLite for local development; PostgreSQL before a shared hosted pilot |
| Scheduler | Checks approved contract sources at configured times | Background service with durable schedules and deduplicated change events |
| Job worker | Performs scans, analysis, repair, and validation | Extract reusable Python engine from the existing agent and SIG modules |
| Execution environment | Runs repository code without exposing other customers or service credentials | Disposable containers for hosted jobs; local temporary workspaces during development |
| GitHub adapter | Reads selected repositories and publishes reviewed proposals | GitHub App with scoped, short-lived installation tokens |
| Research harness | Runs repeatable experiments against the same engine | Versioned cases, baseline configurations, independent checks, and structured results |

The web service coordinates work; it does not execute a customer's test command in its own process. A temporary checkout prevents accidental edits to the original repository, but is not a security sandbox. Hosted execution requires container isolation, resource limits, restricted credentials, and controlled network access.

Persistent records: organization, project, integration, specification snapshot, graph snapshot, requirement, job, validation result, and PR reference. Every result records the source commit and relevant contract versions.

Proposed logical job states: queued, running, needs_input, failed, validated, pr_opened, cancelled. Validation success and PR publication success are separate outcomes. Passing available checks is reported as evidence, not proof of all possible behavior.

## 5. Implementation phases

### Phase 1 — Make the existing demo truthful and repeatable

Purpose: establish a reliable foundation before adding customer workflows.

Work:

- Preserve the current uncommitted work and account for the nested `client_app` Git repository; do not reset, flatten, or move either repository without a separately agreed migration.
- Correct the launcher, dependency declarations, environment examples, and Compose setup.
- Make the demo provider on port 8001 the canonical NexusPay provider. Keep dashboard/control operations on 8002 and the SwiftPay BFF on 8003. A development-only control endpoint switches the provider version; dashboard state reflects the provider's actual version.
- Align provider behavior, OpenAPI fixtures, service signatures, UI examples, and tests.
- Return failure after exhausted repairs; remove the fabricated IPS floor and unsupported success messages.
- Fix retry behavior and overlapping changes to the same file. Re-plan against the exact workspace state to which the candidate will be applied.
- Refresh or invalidate stale SIG snapshots when their source commit/content changes.
- Cover payment, refund, invoice, and analytics behavior with meaningful automated tests.
- Make the intent-blind experimental configuration actually omit intent from initial and revised planning.
- Make Gemini model/configuration selectable and record it in run results.

Completion checks:

- The V1 example passes its checks, the V2 change is reproducibly detected, and supported V2 repairs pass the relevant checks.
- A deliberately wrong repair produces a failure and cannot be reported as healed.
- Restarting or repeating the demo has documented behavior; no accidental paid model calls are required for ordinary regression tests.

Deliverable: trustworthy demonstration and setup instructions.

### Phase 2 — Extract a reusable engine and isolated local workflow

Purpose: support a repository supplied by the user rather than only SwiftPay.

Work:

- Introduce integration configuration for repository/ref, code paths, specifications, setup commands, tests, and execution budgets.
- Separate engine operations from dashboard globals, environment flags, and subprocess log parsing.
- Create a disposable checkout for each job and pin it to a source commit.
- Expose a CLI for scan, compare, repair, and report using the same engine as the dashboard.
- Persist structured job events and evidence; support bounded retries, timeouts, and cancellation.
- Treat schemas, repository content, and logs as untrusted inputs. Enforce file boundaries using resolved paths, validate patch structure, and prevent access to service secrets.
- Initially produce a local patch/report; publishing is a separate adapter action.

Completion checks:

- A second, unfamiliar fixture repository runs through the workflow without modifying SwiftPay or the user's original checkout.
- Failed/cancelled jobs leave the original repository unchanged and retain useful diagnostics.

Deliverable: configurable local engine that can later run in CI or hosted workers.

### Phase 3 — Build the research contribution: explicit intent constraints

Purpose: make intent something the system can inspect and test.

Work:

- Extend the SIG to connect operations and fields to consuming code, relevant tests, and behavioral requirements within the supported Python subset.
- Distinguish confirmed mappings from uncertain inference; report analysis coverage and unresolved expressions.
- Give graph nodes stable identities and record source locations, evidence, and version information.
- Add a small requirement schema: identifier, description, scope, origin, confirmation status, and executable check when available.
- Allow developers to review inferred requirements. Inference alone does not become a trusted acceptance condition.
- Derive candidate checks from requirements where practical and retain their origin. A repair may not weaken existing checks or confirmed requirements to make itself pass.
- Prefer structurally validated edits and re-parse changed files; reject ambiguous patch targets.
- Ask for missing information when a migration cannot preserve a confirmed requirement with available data.

Completion checks:

- A valid payment migration preserves the exact amount and user identifier.
- A schema-compatible cents-to-dollars mistake is rejected by behavioral checks.
- A refund-to-charge substitution is rejected.
- A missing required customer address yields `needs_input` rather than invented data.

Deliverable: versioned graph plus requirement-aware planning and validation.

### Phase 4 — Produce complete, reviewable GitHub proposals

Purpose: fit the product into the developer's existing workflow.

Work:

- Introduce a GitHub App adapter with selected-repository authorization and minimal permissions.
- Commit all related code and test changes to one branch and open a draft PR.
- Include contract changes, impacted workflows, source revision, requirement evidence, validation results, and unresolved limitations.
- Deduplicate repeat jobs and PRs for the same integration/change/revision.
- Recheck repository state before publication; rerun or mark stale if the target has advanced incompatibly.
- Keep merge/deployment under the customer's existing process. Missing CI is reported as missing evidence, not assumed success.
- Add a mocked integration test suite and a controlled test-repository exercise before enabling customer repositories.

Completion checks:

- One multi-file migration produces one complete PR.
- Repeated events do not create duplicate PRs.
- Failed validation cannot produce a PR labeled validated.
- GitHub publication failure preserves the validated local result and supports retry.

Deliverable: end-to-end repository-to-PR workflow.

### Phase 5 — Build reproducible research evaluation

Purpose: measure whether our method helps, before making academic claims.

Work:

- Create a versioned benchmark containing supported migrations, semantic traps, irrelevant changes, and cases requiring missing information.
- Begin with controlled fixtures, then expand with independently reviewed real migration cases where licensing and reproducibility permit.
- Keep evaluation checks independent from candidate generation. Development fixtures and held-out evaluation cases are separated.
- Compare schema+source, schema+source+test-feedback, inferred-intent, and graph+explicit-constraint configurations. Additional ablations can isolate localization and confirmation effects.
- Equalize model settings and repair budgets where possible; record token/context use so differences are visible.
- Repeat stochastic runs; record seeds where supported, model identity, prompts/configuration, commits, contract hashes, tool versions, and raw outcomes.
- Report behaviorally correct repair rate, incorrect test-passing repairs, localization, abstention, time, cost, and uncertainty. Report coverage and unresolved cases.
- Keep LLM IPS secondary and clearly separate from independently established correctness.
- Audit the existing literature document's citations and claims. Build a comparison against actual related methods before choosing a novelty claim.
- Prepare an internal invention disclosure describing the concrete mechanism and existing disclosures; seek institutional/professional assessment before public release if a patent is pursued.

Completion checks:

- A benchmark case can be rerun from its stored configuration.
- Results include negative outcomes, uncertainty, and limitations.
- The same engine used by the product runs the experiments; differences between modes are explicit.

Deliverable: experiment harness, baseline results, and paper-method outline. Publication acceptance and patentability are not promised.

### Phase 6 — Turn the engine into a hosted pilot

Purpose: customers use APIShield without an always-on laptop.

Work:

- Add sign-in, organization membership, repository authorization, and access checks.
- Store configuration and history in PostgreSQL and dispatch durable jobs to workers.
- Add restart recovery, retries, concurrency limits, cancellation, and event deduplication.
- Run customer setup/tests only in disposable execution containers with controlled network access, resource limits, separated credentials, and cleanup.
- Restrict contract fetching to approved destinations and prevent private-network access through user-supplied URLs in the hosted service.
- Separate organization data, redact secrets from logs/prompts, and define retention/deletion behavior. Explain when source content is sent to the selected model provider.
- Replace demo-first screens with Projects, Integrations, Requirements, Changes, Runs, and Settings. Show evidence and required actions before technical pipeline detail.
- Add initial contract baselining so first-time onboarding is not mistaken for a breaking change.
- Schedule checks for configured API sources and trigger rescans when relevant repository code changes.
- Deploy first to a controlled staging environment and exercise backup/recovery and authorization behavior before a customer pilot.

Completion checks:

- A connected test repository is monitored while the developer's laptop is off.
- Two test organizations cannot access each other's data or jobs.
- Service/worker restarts preserve jobs and do not duplicate proposals.
- The full change-to-draft-PR path works on the hosted staging deployment.

Deliverable: limited hosted pilot. External deployment is a separate concrete review point after the implementation is ready.

### Phase 7 — Validate with early users

Purpose: determine whether the workflow saves real engineering effort.

Work:

- Onboard a small set of teams with suitable Python/OpenAPI integrations.
- Track relevant findings, false alerts, repair acceptance, manual corrections, execution costs, and time spent reviewing.
- Interview users about trust, setup friction, missing behavior, and buying preference.
- Use those results to choose the next language, supported change classes, deployment options, and pricing model.

Completion checks:

- At least one unfamiliar integration produces a migration proposal its maintainer accepts.
- Feedback and limitations are documented; scope expands based on evidence.

Deliverable: pilot findings and the next product roadmap.

## 6. Sequence and review points

Build in order: **reliable demo → reusable engine → explicit constraints → complete PR workflow → research evaluation → hosted pilot → user validation**.

Research case collection and related-work review begin early, but full experiments depend on the stable engine. Each phase ends with a working demonstration and its completion checks.

The first development batch is Phase 1 only. Approval of the plan authorizes implementation in the agreed scope; publication, patent filing, production deployment, and changes to unrelated work are separate decisions. Dates and cost estimates follow the initial foundation work and confirmed hosting/model choices.

## 7. Proposed decisions for approval

1. Start with Python, GitHub, and OpenAPI REST integrations.
2. Preserve SwiftPay/NexusPay as demonstrations and evaluation fixtures.
3. Separate the provider onto port 8001 and dashboard operations onto 8002.
4. Deliver draft repair PRs; customer teams review and deploy.
5. Make explicit behavioral constraints the candidate research contribution.
6. Develop a shared CLI/service engine locally, then host it with isolated workers.
7. Implement Phase 1 first and review its results before expanding.

Open questions that do not block Phase 1: intended patent jurisdiction and prior public disclosures; target publication venue; pilot customer access; deployment provider and budget; customer model-provider/privacy requirements.
