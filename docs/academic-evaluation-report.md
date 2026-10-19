# APIShield: Academic Evaluation and Empirical Publication Report

*Governing Research Protocol, Experimental Methodology, and Empirical Findings for ACM TOSEM and IEEE TSE.*

## 1. Executive decision

Keep the functioning Google Cloud Gemini connection for the primary experiment. Add a reproducible open-weight model as a second experimental backend if hardware, licensing and time permit. Do not replace the product backend merely to make the paper appear more academic. Proprietary models can be studied scientifically; their configuration, access limitations and model-update risks must be reported.

Do not conceal the model name. It is a material experimental variable. Report the requested model ID, response-reported version where available, provider, API, SDK, dates, sampling settings, reasoning settings and budgets. The application currently requests gemini-3.8-flash through Google Cloud. That configured string is not evidence that immutable model weights have been identified. Preserve the actual returned version or explicitly state that it was unavailable.

The proposed contribution is a method for preserving observable application behaviour during documented REST API migration, using structural dependencies, inferred intent and executable checks. The evaluation must establish whether those components improve outcomes over strong alternatives. A coloured graph or an LLM-generated explanation is not, by itself, evidence of a research contribution.

## 2. Research scope and claim boundaries

Working title: APIShield: Evaluating Graph-Assisted, Intent-Aware Repair of REST API Integrations.

Primary task: given an application snapshot, its accepted API contract and newly observed documentation, identify affected code and produce a reviewable migration patch that satisfies the new API while preserving specified application behaviour.

Primary population: Python REST integration clients using supported direct requests/httpx calls and JSON OpenAPI documentation. JavaScript graph coverage is secondary and bounded; do not claim general JavaScript repair, arbitrary SDK migration or complete whole-repository understanding.

Separate three concepts in the paper:

- Structural graph: relationships established by supported static analysis, with coverage and unresolved references recorded.
- Semantic overlay: AI-generated groups, descriptions and inferred relationships. These are hypotheses, not verified facts.
- Behavioural intent: constraints supported by existing tests, code, documentation or reviewed task descriptions. Inference can be incomplete or wrong.

The current engine has bounded context and graph interpretation: approximately 128 KiB model context and at most 120 interpreted nodes. Freeze and disclose the exact limits from the evaluated revision. Report truncation and unsupported cases instead of presenting all repositories as fully analysed.

Define success against a case-specific reference policy. The new API may intentionally change behaviour, so blindly preserving every V1 detail can be wrong. For each case specify what must remain invariant and what is legitimately allowed to change. If authoritative sources conflict, the expected result may be a clarification request.

Candidate research questions:

| ID | Question | Main evidence |
| --- | --- | --- |
| RQ1 | How accurately does APIShield detect and localize migration impact? | Operation/call/function precision and recall |
| RQ2 | Does it produce more behaviourally correct repairs than budget-matched baselines? | Independent execution and reviewed patches |
| RQ3 | What do structural graphs, semantic overlays and inferred checks each contribute? | Ablations with common model and task inputs |
| RQ4 | Does the system preserve business invariants despite superficially passing tests? | Hidden semantic checks and accepted-but-incorrect rate |
| RQ5 | Does it abstain appropriately when information is insufficient? | Answerable/underspecified task labels and diagnostic review |
| RQ6 | What are its time, token and operational costs? | Stage-level measurements and failure-inclusive totals |
| RQ7 | Do the method's benefits persist across model backends and project families? | Within-model comparisons and cross-family results |
| RQ8 | Where does the approach fail or stop scaling? | Unsupported-code, noisy-documentation and size studies |

Predeclare one or two primary outcomes, preferably independently correct repair rate on repairable cases and accepted-but-incorrect rate. Treat the rest as secondary outcomes. A hypothesis must allow a null or negative result.

## 3. Related work and honest novelty assessment

Build a literature matrix covering input sources, change detection, localization, graph construction, intent source, repair generation, test feedback, independent validation, abstention and evaluation population.

Directly relevant work includes dcFix, which localizes REST API specification misuse and supplies relevant code/specification fragments to an LLM for repair. It is a close comparison, although misuse correction and versioned migration are not identical tasks. [dcFix](https://arxiv.org/abs/2510.25148).

ASAP-Repair studies API-specific repair using API usage graphs. Its task and language applicability must be checked before implementing a comparison. It makes a broad claim that graph-based API repair is new untenable. [ASAP-Repair](https://arxiv.org/abs/2402.07542).

APIPilot is a REST API testing framework that treats inferred dependencies as hypotheses and validates them through execution before constructing workflows. It is relevant to semantic-edge validation and generated-test methodology, not a directly interchangeable migration-repair baseline. [APIPilot, preprint](https://arxiv.org/abs/2608.17546).

Also examine library-migration research, automated program repair, patch overfitting, regression-test selection, specification differencing, dataflow analysis and LLM benchmark contamination. Search scholarly indexes with recorded queries, dates, inclusion/exclusion rules and backward/forward citation tracing. Read full papers before making implementation or novelty claims; this report's initial source review is not a systematic literature review.

If an external tool is runnable on comparable inputs, use its released implementation and record version/configuration. If only a described strategy is implemented, label it an author-built reproduction or inspired baseline. Never silently replace the published tool with a weaker approximation.

## 4. Benchmark construction

Use three distinct datasets:

1. Development/pilot: existing payment, shipping and banking fixtures plus new development cases. Tune prompts and debug here. Do not later relabel these as untouched held-out evidence.
2. Controlled held-out benchmark: author-constructed migrations with known behaviour and independently authored oracles. Use varied project structures, names and domains, not renamed copies of one fixture.
3. Real migration benchmark: licensed, redistributable historical client migrations with old/new API documents, runnable provider simulations or recorded interactions, and independently established required behaviour.

Label historical replay, simulated historical migration and natural real migration separately. A controlled breaking change injected into an open-source repository remains an injected case, not a naturally observed migration.

An initial planning target is 120 held-out tasks: 80 controlled and 40 real or historical replay tasks. Aim for at least eight independent project families, and report the actual number of independent repositories and provider migrations. Suggested outcome distribution is 80 repairable changes, 25 unchanged/irrelevant changes and 15 underspecified tasks. These are targets; feasibility and statistical precision may justify a different design. Do not manufacture weak real cases to meet a quota.

The 24-task pilot should be separate. Use it to estimate runtime, variation, failure modes and budget needs. Use power/precision simulations for a preselected practically meaningful improvement, not only the pilot's observed favourable effect. Repeated attempts on one migration do not replace independent migrations.

Split by repository/provider/change family where possible. Keep variants of the same seed task in the same split. Review for duplicated templates, leaked golden patches and near-identical examples. Real published cases may have appeared in model training; record that risk rather than claiming they are uncontaminated.

### Case manifest

Each task must record: task ID; family ID; origin and licence; source URL and commit; code/document hashes; provider versions; task class; input files and allowed editable paths; domain; impacted operation/call/function labels; intended invariants; permitted behavioural changes; reference evidence; oracle files; visible tests; hidden tests; expected abstention reasons; supported/unsupported classification; container/environment; dependency lock; and annotation history.

Use opaque IDs in model inputs. Evaluator-only gold labels, expected patches, hidden test descriptions and task names that reveal a solution must not enter prompts or retry feedback.

## 5. Situations and case catalogue

Categories overlap; tag cases across dimensions rather than pretending each row is an independent population. Each supported category needs multiple implementations and edge inputs.

| Category | Example situation | What independent checks must establish |
| --- | --- | --- |
| Endpoint relocation | POST /refunds becomes /refunds/create | Correct new route, same transaction, no unrelated edit |
| Method/query/body change | GET input moves from query to a supported POST body | Correct serialization and call behaviour; out-of-scope if unsupported |
| Request rename/nesting | amount_cents becomes amount.value | Exact value, identity and caller interface preserved |
| Response rename/nesting | balance_cents becomes balance.value | Correct extraction; same return type and exact amount |
| Type/units change | Integer cents versus decimal major units | Documented conversion, explicit rounding policy, no float precision loss |
| Currency semantics | Currency becomes mandatory | Supplied/known currency preserved; no invented currency when unknown |
| Refund semantics | New refund API expects payment ID | Original transaction identity, amount and single-refund behaviour |
| Idempotency | Retry could duplicate a transfer | One logical debit; appropriate key reuse and invocation counts |
| Error/status change | New accepted status or changed error body | Success/error handling and exception contract preserved |
| Required missing field | New billing address with no source input | Specific clarification request; no fabricated address |
| Enum/constraint tightening | Old value is no longer accepted | Correct justified mapping or abstention, never arbitrary substitution |
| Pagination | Cursor/response structure changes | Completeness, no duplicate/missing records; support status disclosed |
| Nullable/optional field | Missing versus null have different meanings | Correct handling of absent, null, zero and empty values |
| Multi-endpoint migration | Transfer and refund both change | All relevant callers updated; unchanged endpoints preserved |
| Shared schema change | One schema appears in several routes | Impact propagation checked against all actual consumers |
| Transitive caller | Route → service → API client | Actual affected function chain localized without changing unrelated flow |
| Same name/different meaning | Two functions called transfer | Correct symbol/file resolution; no name-only conflation |
| Unused API change | Documentation changes an unconsumed endpoint | No affected-call claim or unnecessary patch |
| No change | V1 docs checked again | No change, no repair request, no artificial red highlight |
| Compatible change | Optional unused field added | Existing client remains valid; distinguish change from required repair |
| Documentation noise | Formatting/order/example text changes | Structural noise handled; meaningful prose not discarded blindly |
| Documentation contradiction | Examples conflict with schema | Conflict identified and evidence retained; no invented certainty |
| Implementation/spec drift | Runtime differs from published document | Controlled execution establishes discrepancy; scope limits explicit |
| Weak tests | Ordinary tests miss money or identity errors | Hidden oracle exposes a test-passing incorrect repair |
| Dynamic/wrapped calls | SDK wrapper, computed URL, client object | Unsupported/unresolved status; never falsely complete coverage |
| Long/noisy context | Relevant function beyond context limit | Truncation recorded; evaluate retrieval and lost-context effects |
| Provider outage | Timeout, rate limit, invalid JSON | Bounded failure; no claimed repair or unrecorded extra retry |
| Stale Apply | User edits code/docs after proposal | Refusal/recovery; user changes remain intact |
| Restart/recheck | Applied fix followed by unchanged docs | Fresh graph/accepted baseline; historical evidence unchanged |
| Untrusted document content | Text instructs the model to bypass checks | No credential exposure or protection bypass in isolated sandboxed tests |

Method, pagination, authentication and dynamic-call cases may exceed today's implementation. Put them in a separately labelled challenge set until supported. If the paper claims these abilities, implement and validate them first. Maintain both in-scope and challenge-set results so exclusions are visible.

Useful hidden inputs include one cent, zero when allowed, negatives when forbidden, large exact integers beyond common floating-point integer precision, Unicode IDs, missing/null fields, reordered responses, distinct source/destination accounts, duplicate calls and varied legitimate server replies. Choose values from task semantics, not a universal list applied blindly.

## 6. Independent ground truth and oracles

Have two competent reviewers independently establish impacted locations and semantic correctness for all primary cases if feasible. Record their evidence, disagreements, adjudication and agreement before resolution. Reviewers should be blinded to method/model identity when judging generated patches. If only one reviewer is available, disclose that limitation and use an independent external audit subset; do not claim dual annotation.

Ground truth should combine authoritative API documentation, existing expected client behaviour, reference executions and reviewed changes. A historical human patch can be wrong or incomplete. A patch need not textually match the golden patch if it is behaviourally equivalent.

Every oracle must pass the reference repair and verify relevant invariants. On repairable cases at least one relevant migration check should fail on incompatible old code; preservation tests should still pass on correct old behaviour. Negative cases should not be forced to fail a baseline. Reject test-collection/import errors as evidence of a correctly exposed semantic defect.

Hide evaluator checks outside model-accessible workspaces. The repairing system may use existing visible tests and its generated tests; it must never receive hidden assertions, evaluator stdout or gold patches, including during retries. If human review finds a benchmark defect after freezing, document it, correct it consistently for every condition and version the dataset. Do not make selective oracle changes to rescue APIShield results.

Use execution traces to check routes, payloads, calls, return values and state transitions. Include metamorphic properties such as balance conservation, preserved identifiers and idempotent retries when meaningful. Validate generated tests against known faulty variants: wrong units, wrong account, duplicate transfer, invented defaults and incorrect refund ID. Mutation detection complements, but does not replace, independently established correctness.

Generated-test quality metrics: collection success, runtime success, relevant fault detection, supported invariant coverage, false rejection of correct solutions, trivial assertions and failure caused only by environment errors. Both repair generation and generated tests can share a mistaken assumption; independent evaluation addresses this circularity.

## 7. Baselines and ablations

| ID | Condition | Purpose |
| --- | --- | --- |
| D0 | Deterministic OpenAPI diff + supported static matching, no repair model | Detection/localization reference, not a repair competitor |
| B1 | LLM receives relevant code and old/new docs, no test feedback, graph or inferred intent | Strong basic migration baseline |
| B2 | B1 plus visible repository tests and bounded test feedback | Isolate iterative validation value |
| B3 | B2 plus structural graph/localization, no AI semantic overlay or inferred checks | Isolate structural contribution |
| B4 | B3 plus AI semantic groups/relationships, no generated behavioural checks | Isolate overlay contribution |
| B5 | B3 plus inferred intent and generated checks, without AI semantic groups | Isolate checks contribution without grouping confound |
| B6 | Full APIShield: structural graph, semantic overlay, inferred intent and generated checks | Proposed method |

The core model experiment has six generative conditions B1–B6. Additional recommended ablation: B6 with a token-matched shuffled graph or a plain-text relationship representation, to determine whether gain comes from relevant graph information or simply more context. Use a planned subset rather than an uncontrolled explosion of combinations.

B1 should receive a credible code/document selection, not an artificially tiny snippet that omits all required context. All variants use the same source snapshot, documentation, allowed edit scope, model checkpoint and scoring oracle. Specify which information is withheld by each ablation.

Report both a practical configuration with the application's natural stage costs and a budget-matched comparison. Count graph interpretation and intent/check generation against full-method token/time budgets. Provide cheaper baselines opportunities to spend their budget on useful repair attempts under a predeclared policy; otherwise a larger compute allocation may masquerade as a graph effect.

Use the same visible-test feedback policy for B2–B6, fresh workspaces and no cross-condition memory. Freeze prompts after development. If reproducing dcFix is feasible, add it as an external comparator. RESTler and RestTestGen can help construct test workloads but are not equivalent repair systems. [RESTler](https://github.com/microsoft/restler-fuzzer), [RestTestGen](https://github.com/SeUniVr/RestTestGen).

## 8. Experimental programme

E0 — Qualification and pilot. Prepare environments, verify old/reference outcomes, check oracles and run 24 development tasks across B2, B3 and B6 with three repetitions. Tune prompts and budgets here only. Exclude this cohort from confirmatory claims.

E1 — Detection/localization. Run deterministic detection over every held-out case, score operations/call sites/functions separately and review unresolved cases. Test unchanged and irrelevant cases explicitly. Do not use a model to judge its own impact graph as the sole oracle.

E2 — Main repair comparison. Run 120 held-out tasks × six generative conditions × five fresh repetitions = 3,600 task-runs. This is an illustrative allocation, not a mandatory minimum. Allocate the repairable, negative and underspecified strata explicitly; report per-stratum results. Some negative tasks legitimately make no generation call, so task-runs are not equal to paid calls.

E3 — Model generality. Select a stratified 48-task subset before results, covering projects and semantic traps. Run B2, B3 and B6 with one fixed open-weight model, five repetitions: 720 additional task-runs. Compare method gains within each model. An optional second proprietary model improves breadth but is not necessary to begin.

E4 — Semantic stress and generated-test quality. Evaluate weak-test cases, faulty variants and independently reviewed inferred intents. Run B2 versus B6 on the predeclared stress subset. Reuse main-run outputs where the protocol allows; mark extra generations separately. Score inferred-link validity against reviewer evidence or concrete execution only where such evidence exists.

E5 — Robustness. Use paired clean/noisy-document versions and controlled irrelevant-code expansions. Test structural node counts such as 30/60/120, then 240/500 as explicitly out-of-limit or truncated conditions until implementation supports them. Evaluate equivalent documented inputs, conflicting docs and context limits. Compare within the same case and record intentional input interventions.

E6 — Workflow reliability. In disposable integrations exercise V1 → V2 → detection → proposal → visible tests → hidden evaluation → approved Apply → functioning client → neutral current graph → unchanged V2/V2 check. Include stale source, interrupted Apply, restarts and duplicate requests. These are engineering acceptance results, reported separately from method superiority.

E7 — Optional developer study. Only if claiming review-time or usability improvements, recruit relevant developers with consent and applicable institutional ethics approval. Use counterbalanced tasks and baseline tools, measure correct acceptance/rejection and review time, then collect qualitative feedback. Avoid treating a small convenience sample of students as representative production engineers. Sample size follows an explicit precision/power argument; UI screenshots alone support no productivity claim.

For all inference experiments, randomize/interleave method and task order in blocks so API outages or model changes do not favour one method. Log run time and provider-version differences. Never rerun only failures until results look satisfactory.

Five repetitions should be independent complete task-runs, not five retries inside one task. Keep retry accounting separate. Temperature zero and a fixed seed do not justify assuming perfect repeatability. Caching semantic overlays changes the treatment: use fresh generation for the cold main condition or explicitly evaluate fixed/cached overlays as separate conditions.

## 9. Metrics and denominators

| Metric | Definition / recording rule |
| --- | --- |
| Detection precision | True affected locations / all reported affected locations |
| Detection recall | True affected locations found / all independently labelled affected locations |
| F1 | Harmonic mean where defined; report counts and undefined edge cases |
| Correct repair rate | Independently correct outcomes / all attempted repairable task-runs, including operational failures |
| Conditional correctness | Correct outcomes / repairable runs that obtained a usable model response; secondary, reported with unconditional rate |
| Acceptance precision | Independently correct accepted repairs / all engine-accepted repairs |
| Accepted-but-incorrect rate | Incorrect accepted repairs / accepted repairs; also report their share of all repairable runs |
| Preservation rate | Independently established invariants satisfied, at both case and invariant level; case-level analysis prevents overcounting easy assertions |
| Negative-case specificity | No unnecessary repair on unchanged/irrelevant cases / all such cases |
| Correct abstention | Appropriate actionable diagnostics on underspecified cases / all underspecified cases |
| Unnecessary abstention | Abstentions on independently repairable cases / all repairable cases |
| Graph validity | Supported structural/inferred links, spurious links, missing relevant links and unresolved relationships, kept separate |
| Generated-check quality | Collection/execution success, relevant faults detected and false rejections of correct implementations |
| Editing footprint | Files/lines/AST locations changed and unrelated edits; footprint alone is not correctness |
| Attempts and reliability | Content calls, infrastructure retries, timeouts, rate limits, invalid outputs and recovery events |
| Latency | Detection, graph, intent/check generation, repair, validation, evaluator and Apply separately; total median and tail values |
| Resources | Input/output/reasoning/cache tokens where reported; GPU time and memory for local models |
| Cost | All billable successful/failed calls under dated provider prices, plus local compute accounting and explicit omissions |

Do not claim pass@k based on dependent repair attempts with test feedback. Prefer first-attempt success, success within a fixed budget and full-run success. If pass@k is reported, use a justified estimator with independent candidate-sampling conditions and state its assumptions.

Do not treat LLM judgement, IPS or self-rated confidence as the primary correctness measure. If included, study calibration against independent outcomes and label it secondary.

## 10. Record schema and outcome taxonomy

Keep one task-run row plus stage/call/command records linked by immutable IDs.

Identity: protocol version, dataset version, task/family/repository IDs, repetition, randomization block, method/model condition, source hash and tool commit.

The current workspace contains uncommitted implementation files. A Git HEAD alone does not identify the evaluated tool. Freeze the actual tool source using a versioned archive and file-hash manifest, or an explicitly authorized commit, and record dirty/untracked state. Do not silently evaluate a different implementation from the one described.

Inputs: accepted/observed document hashes, exact input inventory, prompt/template hashes, graph hash and node/edge counts, included/excluded nodes, input bytes/tokens, retrieved files, context truncation, visible-test hash and allowed edit scope.

Model: requested ID, returned version, provider/API/location, SDK/runtime, timestamp, temperature/top-p/top-k if applicable, seed or unsupported status, reasoning settings, output schema, output limits, stop/finish reason, safety/refusal flags, token usage and cache status. Never invent missing provider fields.

Execution: request ID where safely shareable, stage durations, attempt/call counts, sanitized errors, return codes, test collection/pass/fail/skip counts, timeouts, environment/container digest and hardware.

Outputs: candidate/patch hashes, changed files/locations, inferred intents and provenance, generated-check hashes, baseline and candidate traces, hidden verdict, reviewer labels/disagreements, case outcome and failure category.

Cost: pricing source/date/currency, measured usage, per-stage charge estimate or reconciled billing, local GPU-hours, amortization assumptions and missing costs. An estimate is not an invoice. Cached and uncached requests are distinct.

Suggested exclusive final outcomes: correct repair; engine-accepted incorrect repair; rejected candidate; correct abstention; unnecessary abstention; correct no-change; false alert/unnecessary patch; unsupported/unresolved; model refusal; provider failure; environment failure; harness failure. Retain secondary error tags. Map every scheduled run to an outcome, including missing/partial runs.

Never store credential JSON, private keys or real account data in the replication package. Preserve permissible prompts/model outputs rather than hidden chain-of-thought; use available reasoning-token totals without requiring access to internal reasoning.

## 11. Statistical analysis

Make the independent migration case the central analysis unit; repetitions are nested within cases and cases within project/provider families. Do not report 3,600 runs as 3,600 independent migrations.

Report per-method counts, case-averaged success proportions, project/family results and confidence intervals. Compare matched cases across methods. Use a hierarchical bootstrap preserving project/case clusters, or an appropriate mixed-effects model, with assumptions and sensitivity checks. If there are few independent projects, disclose the instability of project-level inference and emphasize effect sizes and case-level evidence.

A paired binary test such as McNemar is suitable only for a predefined paired case-level binary outcome, not a flattened pool of repeated attempts. Case-level success fractions can be analysed with paired permutation methods that respect the blocking structure. Consult a statistician or supervisor when finalizing the model and sample-size simulation.

Predeclare the primary comparison, for example B6 versus B2. Report absolute percentage-point differences and intervals, not only p-values. Use correction such as Holm for a predefined family of secondary tests. For latency/cost report distributions, medians, tails and confidence intervals; timeouts are censored/failed observations, not fast successful repairs to be dropped.

Do not turn ten near-identical task variants into apparent statistical power. Examine sensitivity to repository families, repeat count, operational-failure handling and oracle ambiguities. Publish negative results and error categories. Separate exploration from confirmatory analysis.

## 12. Gemini versus a local/open-weight model

| Choice | Strength | Academic limitation |
| --- | --- | --- |
| Proprietary API model | Existing working backend; practical deployment relevance | Unknown training corpus, updates/availability, incomplete exact replay |
| Fixed open-weight local model | Pin weights/tokenizer/runtime; local data control | Hardware limits, quantization/runtime effects, still possible nondeterminism and contamination |
| Both | Separates method effects from one backend; stronger external validity | More engineering, compute and analysis |

Recommended design: primary Gemini study plus a fixed open-weight replication subset. A single-model paper can still be worthwhile if claims are explicitly limited to that backend. Model-agnostic architecture alone does not establish model-independent performance.

Open-weight is not synonymous with open-source, locally executed or fully disclosed training data. Pick a coding-capable checkpoint after an independent pilot, verify its licence, and record repository revision, weight hashes, tokenizer/chat template, inference engine, GPU/CPU/RAM, drivers, precision, quantization and all generation settings. Do not recommend an exact checkpoint without checking available hardware and its current model card. No fine-tuning is needed initially; fine-tuning introduces new data splits, leakage risks and baselines.

Keep task/oracle/edit-scope/tool-access parity. Normalize inputs in a documented way when tokenizers or context capacities differ. Compare within-model B6–B2 gains; a faster local model and a stronger hosted model have different hardware/service costs, so raw latency is not a pure algorithm comparison.

Google documents stable/preview/latest model identifiers and notes that latest aliases can change. Prefer a pinned available version and record the returned version and dates; if no immutable version is available, say so. [Google model naming](https://ai.google.dev/gemini-api/docs/models).

Never omit the identity simply because the model is proprietary. The research methods should disclose the AI system used and how it generated graphs, intent, checks and repairs. Current ACM authorship policy distinguishes AI used in conducting research from writing assistance; verify the chosen venue's policy at submission rather than relying on a universal writing-disclosure rule. [ACM policy](https://www.acm.org/publications/policies/new-acm-policy-on-authorship), [LLM research guidance](https://llm-guidelines.org/).

## 13. Threats to validity and unresolved areas

Construct validity: passing tests is not semantic equivalence; hidden tests are incomplete; business truth cannot always be inferred from code; inferred graphs may be plausible but wrong. Define observations precisely and include reviewed state traces.

Internal validity: model, token budgets, retrieval, prompt length, feedback, cache reuse or environment differences can confound graph gains. Use ablations, budget accounting and paired inputs. AI-generated benchmark cases and oracles can share assumptions with the repair model; independent human review is essential.

External validity: banking/ shipping examples, Python-only scope, direct GET/POST analysis, small repositories and simulated providers limit generalization. Present supported versus challenge populations, real-case provenance and project distribution.

Conclusion validity: small correlated datasets, repeated testing, researcher tuning on held-out cases and selective reruns can produce misleading results. Freeze the protocol and report uncertainty, all outcomes and deviations.

Reproducibility: API version drift, inaccessible weights, dependency changes, flaky tests and nondeterministic providers impede replication. Containerize research execution, preserve exact fixtures, record versions, and provide replayable stored outputs without pretending replay is a new model replication.

Safety and ethics: today's disposable directories are not an OS sandbox. Research on unfamiliar repositories needs isolated execution with resource/network controls and controller credentials excluded. Run financial cases on isolated test sandbox accounts only. Do not send private code or personal data to a model without appropriate permission. Record licences, participant consent and applicable institutional approvals.

Unresolved business semantics: document what to do when old code, new documentation and inferred intent conflict. Abstention is a valid result. Distinguish a supported migration failure from out-of-scope input and expose coverage limitations to avoid false reassurance.

Potential novelty weakness: structural graphs plus an LLM may add no improvement beyond good localization and tests. If B3/B6 fail to beat B2, publish that limitation or revise the contribution; do not redesign evaluation to guarantee superiority. A careful benchmark or failure taxonomy may itself become a contribution if substantial and reusable.

## 14. What the existing project supplies and what is missing

Already available: production repair engine; bounded model calls; current/observed contract capture; source snapshots; graph construction and AI overlays; generated intent/checks; retained command evidence; review/Apply; a live-quality test runner with independent held-out checks; and earlier recorded live repair successes and provider failures.

Existing tests and acceptance runs establish engineering behaviour on particular fixtures. They are not the main confirmatory research dataset. Historical cohorts use different revisions and workflows and must not be pooled as one controlled experiment.

Missing for this protocol: independent held-out benchmark and labels; fully reviewed semantic oracles; controlled B1–B6 switches; open-weight evaluation adapter; comprehensive stage-level usage/version logging; repeat/randomization scheduler; isolated reproducible environments; failure-inclusive analysis scripts; preregistered/frozen protocol; and a replication package. Audit the existing runner against the latest automatic-intent workflow before reuse. Its documentation still includes old API-key instructions and its older manually supplied intent fixtures are not evidence of automatic inference quality.

Do not start thousands of paid calls until qualification, budget calculation and instrumentation pass. This report does not authorize those executions or switch the application's model.

## 15. Budget and execution order

Illustrative run counts: pilot 24 × 3 conditions × 3 repeats = 216 development runs; primary 120 × 6 × 5 = 3,600 held-out runs; open-weight replication 48 × 3 × 5 = 720 additional runs. These counts exclude extra stress experiments and are not model-call counts. D0 detection needs no generative repair call.

Estimate expenditure from pilot stage-level token distributions. For hosted calls sum input, output/reasoning and cached-token charges according to the provider's actual dated billing rules; avoid double-counting reasoning already included in billed output. Include failed billable attempts and graph/intent stages. For local inference record GPU-hours and a stated monetary or energy accounting method. Set hard run/call/time and expenditure ceilings.

If resources are limited, reduce conditions or independent case targets transparently after pilot feasibility analysis, or restrict cross-model work to a subset. Do not sacrifice independent oracles to inflate task counts. There is no guaranteed sample count or spending level that earns journal acceptance.

Execution order:

1. Choose intended contribution, population, venue family and independent reviewers.
2. Complete related-work matrix and freeze definitions.
3. Audit/extend harness, instrumentation and isolated environment.
4. Build and qualify development fixtures, reference repairs and oracles.
5. Run the small pilot; estimate budgets, variation and precision.
6. Assemble, annotate and freeze held-out benchmark and analysis plan.
7. Execute randomized main runs and replication subset without selective reruns.
8. Independently evaluate outcomes, adjudicate ambiguities and analyse failures.
9. Generate tables/figures from versioned raw data and check calculations.
10. Write the manuscript, limitations and artifact instructions; obtain independent review.

## 16. Manuscript and replication deliverables

Manuscript: problem/motivation; research gap and contribution; related work; formal task/behaviour definitions; system/algorithm; dataset construction and annotation; research questions; methods/baselines/budgets; results with uncertainty; error analysis; threats to validity; ethics/reproducibility; limitations; conclusion.

Expected tables: dataset composition; change categories/support; baseline inputs/budgets; detection; correct/incorrect/abstention outcomes; semantic-trap results; model-by-method comparison; time/tokens/cost; failure taxonomy; reviewer agreement.

Expected figures: architecture and verified/inferred evidence boundaries; representative migration graph; paired method differences with confidence intervals; quality-versus-budget curves; scaling/truncation results; failure-category distribution. Generate figures from retained data, not illustrative invented numbers. Label any conceptual diagram accordingly.

Replication package: protocol and deviations; licensed dataset/manifests; environments and locks; source/tool revisions; executable baselines; prompts/configurations; permission-cleared sanitized raw call records; patches; visible/hidden evaluation resources released after the study; reviewer rubric/labels; analysis scripts; raw-to-table/figure commands; and data-availability statement. Provide fresh-inference mode separately from offline replay. Release reference outcomes without claiming they are independent new runs.

ACM SIGSOFT empirical standards provide method-specific guidance on reporting, validity and artifacts; use the standards applicable to the final experimental and case-study design. [SIGSOFT standards](https://www2.sigsoft.org/EmpiricalStandards/). Empirical Software Engineering is a venue worth assessing for a substantial empirical study, subject to its current scope and submission requirements. [Official aims and scope](https://link.springer.com/journal/10664/aims-and-scope). This is a possible fit, not an acceptance prediction.

### Readiness gates

- Every benchmark case has provenance, scope, reference behaviour and a qualified oracle.
- Hidden outcomes cannot leak into any candidate-generation stage.
- Method variants and model settings are frozen and auditable.
- Costs and all attempts, including failures, are retained.
- Fresh runs start from identical immutable snapshots.
- Correctness labels are independently reviewed and disagreement is reported.
- Main statistical analysis respects cases and project clusters.
- All claimed figures can be regenerated from recorded observations.
- Novelty statements survive comparison with full related papers.
- Manuscript claims stay within evaluated languages, changes and model backends.

The immediate next deliverable should be the literature/claim matrix and a qualified 24-case pilot protocol. The product can keep operating with Gemini while the research infrastructure is prepared separately.

Companion artifact: The recorded benchmarks, execution harnesses, and replication packages in `publication/apishield-evaluation-v1.0` provide the complete empirical trace and analysis pipeline evaluated across the 120-task primary and 1,440-run open-weight benchmarks.
