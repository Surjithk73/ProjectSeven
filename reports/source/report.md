# CHAPTER 1
# INTRODUCTION
## 1.1 API evolution and client maintenance

An application rarely controls every service on which it depends. A payment client, for example, may continue using the same subscription function while its provider changes the shape of the request accepted by that function. The change can be small in source code and still affect a business operation. Moving an amount into a nested object is straightforward syntactically; preserving its unit and exact value requires additional care.

APIShield addresses maintenance of Python integrations when a provider publishes an updated OpenAPI contract. It identifies supported consuming calls, presents the affected code and prepares a migration proposal in a disposable workspace. The proposal is accepted by the engine only after configured validation and applicable confirmed business-rule checks succeed. A developer then reviews the retained patch or prepares a GitHub draft pull request.

The project is motivated by a practical gap between a contract difference and an acceptable application change. A difference report can identify that an endpoint has moved without explaining which subscription or refund workflow uses it. A patch can satisfy the new request schema while changing a monetary value. A passing test can also be misleading if its assertions do not check the behavior that matters.

The implemented system makes these relationships inspectable. Contract snapshots, source revision, discovered operations, declared requirements and test outcomes remain attached to a run. This supports review even when the engine cannot produce a repair. The intended user is a developer maintaining a trusted local Python repository. The implementation described here runs locally; operation as a shared hosted service is outside the delivered scope.

<!-- PAGE -->
## 1.2 Problem statement and motivating example

The maintenance problem can be stated as follows: given an existing integration, an old and an updated API contract, and executable validation, determine the supported affected code and propose an admissible migration while preserving declared application behavior. When the required behavior cannot be established from the available inputs, return an actionable diagnostic.

Consider a client that receives an integer number of cents. Version 1 sends that integer directly; version 2 requires an amount object containing a value and currency. A repair that divides by one hundred may appear reasonable if the author assumes that the new value is expressed in dollars. It is wrong when the updated contract still expects cents. Likewise, a refund migration must retain refund identity and must not substitute a newly available charge endpoint because its request happens to look similar.

These examples distinguish structural compatibility from application-level preservation. The relevant requirement must identify what should remain invariant and link that statement to tests that actually exercise the candidate. A description alone cannot determine acceptance, and a model's confidence cannot replace those checks.

[[TABLE:1.1|Representative changes and preservation obligations|Change type|Structural migration|Behavior to retain]]
Endpoint move|Use the updated path|Operation identity and returned response
Request nesting|Build the new object|Exact identifiers, units and values
Response nesting|Read the updated response|Actual provider reply and error handling
New required information|Supply a missing field|Do not invent unavailable customer data
[[ENDTABLE]]

Table 1.1 defines representative obligations used throughout the report. These are examples within the supported subset, not a claim that every contract change is repairable.

<!-- PAGE -->
## 1.3 Aim and objectives

The aim is to build an inspectable API migration workflow that connects documented provider changes to consuming code and independently checked repair proposals. The academic question is whether explicitly linking requirements to source operations and executable checks can reduce incorrect accepted repairs under a controlled evaluation.

The first engineering objective is reliable localization. The scanner should identify direct supported HTTP calls and state where it cannot resolve a URL or wrapper. A visible limitation is preferable to a falsely complete impact report because omitted code otherwise disappears from the developer's review.

The second objective is constrained candidate generation. The model receives selected source, contract context and relevant confirmed requirements. Its output must satisfy a strict patch or diagnostic format. Exact, unique replacement targets and syntax checks prevent ambiguous edits from silently changing an unrelated location.

The third objective is defensible acceptance. The engine runs configured validation and separately checks selected requirement tests. It records the command, outcome and associated evidence. Empty, skipped or unavailable requirement checks cannot establish that a requirement passed.

The fourth objective is practical review. A browser workspace should expose the original and updated contracts, impact relationships, code changes, validation and provenance. A validated multi-file patch should remain usable independently of remote publication. GitHub draft creation is a separate action with its own verification and recovery state.

The research objectives are narrower than a general claim of autonomous software repair. They concern a reproducible API migration task definition, explicit preservation constraints and a fair study of whether those constraints improve outcomes. Chapter 7 reports benchmark qualification and recorded inference, with the larger comparative study identified as incomplete. Historical acceptance evidence is analyzed separately in Chapter 6.

<!-- PAGE -->
## 1.4 Scope and supported assumptions

The current product accepts trusted local Git repositories containing Python REST integration code. Jobs capture committed source or a hashed working-tree snapshot. The current browser workflow includes uncommitted source and compares active documentation with the accepted baseline. Browser onboarding accepts JSON OpenAPI contracts, source paths and a test directory. Advanced command configuration remains available through trusted local configuration.

The repair scanner supports a conservative subset of direct requests and httpx GET and POST calls. It resolves supported literal and statically recoverable URL expressions. A client instance, wrapper, dynamically constructed host or unsupported lexical scope can prevent localization. Those cases are reported as limitations; the presence of a repository graph does not make the repair scanner complete.

[[TABLE:1.2|Current scope and deferred capabilities|Area|Implemented scope|Deferred extension]]
Repositories|Committed or captured working Python source|Additional languages and repository acquisition
Contracts|Supplied JSON OpenAPI and approved monitoring URL|Specification inference and undocumented behavior
Repair|Affected Python source and protected validation|General frontend and arbitrary refactoring
Execution|Disposable copies on a trusted local host|Hostile-code sandbox and shared tenant isolation
Publication|Explicit GitHub CLI draft workflow|GitHub App service and automatic merge
Research|Historical acceptance, fixture qualification and live inference records|Evaluated multi-task model benchmark
[[ENDTABLE]]

Local monitoring checks documented contract sources while the application is running. It is not an independent hosted scheduler. Similarly, successful test execution provides evidence for the selected assertions, not a guarantee that the contract or business description is complete. These assumptions define where the reported engineering observations can reasonably apply.

<!-- PAGE -->
## 1.5 Contribution and academic position

APIShield contributes an implemented workflow in which source localization, explicit behavioral requirements and validation provenance are connected to an API contract migration. Its proposed research contribution is the mechanism by which confirmed requirements select additional acceptance checks and remain traceable to operations, source scopes and historical evidence.

This claim does not require treating code graphs, language-model repair or intent extraction as new ideas. Those are established research directions. The report instead examines their application to a narrower maintenance setting with an external, versioned contract change and a developer-approved preservation obligation. Chapter 2 positions this mechanism against primary related work.

The engineering contribution includes a shared local engine used by the command-line and browser interfaces, disposable source snapshots, guarded Python edits, durable run records, local monitoring and complete draft-proposal preparation. These components make the research question testable because they provide a common execution path and retain the inputs needed to audit outcomes.

The expected benefit is improved accountability during migration review. A reviewer can inspect why a function was marked, which rule applied, which tests executed and which source revision was checked. Whether this improves behavioral repair success, reduces review effort or lowers the rate of incorrect accepted patches remains an empirical question. The experimental design measures those effects without equating a useful interface with demonstrated algorithmic superiority.

The evidence therefore supports a working prototype and selected behavioral cases. It does not establish a broadly superior repair method or an exhaustive novelty claim. An academically viable contribution can be precise about this boundary while still offering a useful artifact, a defined mechanism and a reproducible evaluation plan.

<!-- PAGE -->
## 1.6 Organization and evidence conventions

Chapter 2 reviews API contracts, repair agents, inferred intent, repository graphs and evaluation practice. Chapter 3 derives requirements and operational boundaries. Chapter 4 describes architecture and retained data. Chapter 5 explains localization, candidate generation and acceptance. Chapter 6 reports existing engineering evidence. Chapter 7 analyzes the benchmark harness, executed qualification candidates, invariant failures and live inference measurements. Chapter 8 states conclusions and future work.

Three kinds of statement occur in the report. An implemented capability describes behavior present in the inspected system. A recorded observation describes a dated project validation record. A proposed experiment specifies a method or metric that has not yet produced a measured result. Tables identify unmeasured results explicitly so that later measurements can be inserted without changing the meaning of earlier evidence.

Historical observations are kept in their original cohorts. The initial live assessment used different model and protocol configurations from subsequent Cloud acceptance. A follow-up money case supplies additional evidence for that category; it does not retroactively change the failures in an earlier run. Similarly, a historical full test-suite count describes that revision and environment, not every future source change.

The report uses APA author-date references for external literature and project records. The project records are unpublished technical documents, not independently replicated research publications. Their value is traceability: they identify tasks, artifacts and limitations that can be checked by a future reviewer.

All personal details and signature fields are placeholders. Experimental result cells marked NOT MEASURED should be replaced only after their associated protocol has been executed and reviewed. Appendices provide a result-record schema and an evidence index to support that update. This organization allows the final report to develop alongside the implementation without silently turning planned work into completed findings.

<!-- PAGE -->
# CHAPTER 2
# BACKGROUND AND RELATED WORK
## 2.1 Contracts and compatibility

OpenAPI describes HTTP interfaces through paths, operations, parameters, schemas, responses and related metadata. Its machine-readable structure makes it suitable for automated comparison and tooling (OpenAPI Initiative, 2021). A contract can identify a required property or response shape, but it may omit the business reason for a value or the downstream consequence of changing it.

Semantic Versioning provides a convention for communicating compatibility through version numbers (Preston-Werner, n.d.). A client still needs to inspect the actual change and its own usage. Two consumers of the same provider may depend on different operations, so the practical migration scope is specific to each application.

The APIShield task begins with two supplied contract snapshots. It does not infer an undocumented interface from traffic. This restriction reduces one source of uncertainty and permits provenance through hashes of the exact inputs. However, it also means that undocumented behavioral drift may escape detection even when both snapshots are syntactically valid.

Structural and behavioral compatibility should be evaluated at different levels. A new object may satisfy the required schema while carrying the wrong unit. An optional response field may become essential to one application's workflow even when the provider considers its removal minor. For this reason, a contract diff is an input to impact analysis rather than a complete account of client correctness.

This distinction motivates explicit requirements. A declaration such as preserving integer cents introduces an application obligation that the schema alone may not express. The obligation becomes useful for acceptance only when its scope and executable checks are known. APIShield's requirement records provide that connection while retaining the developer's role in deciding whether the checks reflect the intended behavior.

<!-- PAGE -->
## 2.2 API change detection and black-box testing

oasdiff compares OpenAPI descriptions and reports differences and breaking changes (oasdiff contributors, n.d.). APIShield uses its native executable for comparison evidence. The tool is a dependency within the proposed workflow, not an inferior baseline to be replaced. A difference report remains useful independently of automatic repair.

RESTler analyzes a service specification to generate stateful request sequences. Its central purpose is to exercise a service and discover reliability or security defects through sequences with producer-consumer dependencies (Atlidakis et al., 2019). This differs from migrating a consuming application's source after a published contract change. A stronger service-testing method could complement client repair by improving the evidence about provider behavior.

RESTTestGen generates black-box REST tests from Swagger descriptions and uses distinct checks for nominal and error scenarios (Viglianisi et al., 2020). RESTSpecIT uses LLM-assisted request mutations to infer documentation and test APIs with incomplete descriptions (Decrop et al., 2025). These tools can complement migration validation; their service-testing outcomes are not interchangeable with client-repair correctness.

Contract comparison identifies described differences; service testing probes runtime behavior; client migration changes consuming code. A fair comparison must respect those task boundaries. Combining these stages does not establish superiority over specialized tools on their own tasks.

For the present research question, the strongest direct baseline is the same migration engine with selected context or acceptance mechanisms removed. Such a baseline controls the model and execution budget while varying the mechanism of interest. Comparing APIShield's synthetic repair rate against a published service-fuzzing metric would not answer the question.

<!-- PAGE -->
## 2.3 Autonomous program repair

RepairAgent treats program repair as a tool-using language-model activity. A finite-state framework and dynamically updated prompts support information gathering, candidate construction and validation (Bouzenia et al., 2024). Its reported evaluation concerns general program defects. It establishes relevant precedent for model-guided repair and feedback, so the presence of an agent loop is not sufficient as a novelty claim for APIShield.

SWE-agent investigates how an agent-computer interface affects repository navigation, editing and execution. The system demonstrates that the interface available to a model can influence software-engineering performance (Yang et al., 2024). APIShield adopts a more restricted editing boundary: a candidate cannot freely alter tests or arbitrary repository files. This is a task-specific engineering choice whose effects require its own evaluation.

AutoCodeRover combines language models with structured code search for autonomous program improvement (Zhang et al., 2024). Its relevance lies in localization and repository understanding. APIShield also uses source structure, but begins from changed HTTP operations rather than only a natural-language issue description.

Closer API-specific work further narrows the contribution. dcFix localizes REST specification violations and supplies the relevant code and specification to an LLM (Yamagishi et al., 2025). ASAP-Repair uses API usage graphs and templates, while APIfix synthesizes library adaptations from migration examples and new-version usages (Nielebock et al., 2024; Gao et al., 2021). These establish specification-grounded repair, graph-based API repair and automated adaptation as prior work. APIShield investigates their migration-specific combination with inferred executable obligations and independent final evaluation.

The report does not compare headline success percentages across these studies. Their datasets, languages, task descriptions, models and validation rules differ. Any numerical claim of better repair quality would require a common task collection, equal resource budgets and an independent oracle. Chapter 7 defines such a local comparison without presenting the published systems' unrelated metrics as directly comparable scores.

<!-- PAGE -->
## 2.4 Intent inference and repository graphs

SpecRover studies code-intent extraction through iterative specification inference during code search and patch review. It uses inferred explanations to support repair and confidence assessment (Ruan et al., 2024). This is direct prior work on intent-aware repair. It prevents a defensible report from claiming that APIShield is the first system to consider intent.

RepoGraph provides repository-level structural guidance to software-engineering methods (Ouyang et al., 2024). It shows that repository graphs are an established way to expose relationships beyond a single file. APIShield's bounded graph likewise presents source structure and resolved calls, while adding external API operation nodes and developer-declared rule/test links for migration review.

Invariant inference also has established foundations. Daikon observes executions and reports likely properties such as ranges and relationships between values (Ernst et al., 2007). Such properties describe observed behavior, which may be incomplete or incorrect. APIShield's generated obligations likewise require independent checks; a plausible inferred rule cannot define its own ground truth.

APIShield labels those origins. Semantic interpretation can supply repair context, while acceptance still requires executed checks. A generated community name may help a reviewer understand a graph, but it does not establish that an affected requirement passed. Conversely, a confirmed declaration without a working test link can block repair acceptance even when the graph appears plausible.

The proposed research mechanism therefore concerns traceable use of explicit constraints rather than the invention of graphs or intent inference. To isolate its effect, the study must compare inferred context with confirmed context and must keep independent evaluation checks outside both. Merely adding more text to one condition would otherwise confound the proposed benefit with a larger prompt budget.

<!-- PAGE -->
## 2.5 Simpler repair pipelines and benchmark design

Agentless organizes software repair into localization, repair and validation without granting a model unrestricted control over the next action (Xia et al., 2024). It is relevant because an elaborate autonomous loop should not be assumed to improve outcomes simply by being more complex. APIShield's reusable engine similarly fixes important stages and enforces a finite attempt budget.

SWE-bench frames repository repair using real GitHub issues and corresponding code changes, with execution-based evaluation (Jimenez et al., 2023). It provides a precedent for reproducible software-engineering tasks, while the API migration setting additionally needs paired contract versions and explicit preservation obligations.

The existing APIShield fixtures are deliberately small. This helps diagnose errors such as changing cents, confusing refunds with charges or inventing a missing address. It also limits generalization: a direct call in a short Python file does not represent every production integration. An expanded benchmark should retain these diagnostic cases and add independently reviewed real migrations.

Patch plausibility and correctness must be distinguished. Qi et al. (2015) showed how weak acceptance proxies admit incorrect patches in generate-and-validate repair. APIShield's historical assessment similarly strengthened held-out checks to verify invocation count, destination, payload and propagation of varying replies, rather than accepting a hardcoded successful response (APIShield Project, 2026f).

The lesson for study design is that a test-passing repair rate is meaningful only in relation to the assertions used. The proposed evaluation records configured-test success separately from independent behavioral success. It also records outages and malformed outputs instead of discarding them from the end-to-end denominator. This makes the outcome distribution useful even when the model service is unreliable.

<!-- PAGE -->
## 2.6 Adaptation and security boundaries

The autonomic-computing literature describes systems that observe conditions and adapt behavior using feedback (Kephart & Chess, 2003). Monitor, analyze, plan and execute is a useful conceptual organization for API maintenance. APIShield's original demonstration follows that pattern; the newer product makes acceptance and publication explicit rather than treating every proposed change as self-healing success.

Tool-using models also consume untrusted material. InjecAgent studies attacks embedded in external content processed by agents (Zhan et al., 2024). AgentDojo provides an extensible environment for evaluating agents under untrusted tool data and adaptive attacks (Debenedetti et al., 2024). These studies motivate separating source data from instructions, but they do not establish that a particular prompt or filter is a complete defense.

The implemented engine restricts patch paths, strips controller credentials from repository subprocess environments and protects tests and contracts against candidate edits. A disposable workspace protects the original checkout against ordinary repair changes. It does not isolate hostile repository code from the host operating system.

This boundary affects the academic claim. The project can describe guarded edits and local recovery behavior. It cannot claim a secure hosted multi-tenant execution platform. Container isolation, resource governance, tenant separation and network controls would require additional implementation and adversarial validation.

Security is also relevant to evidence. Logs and prompts can expose secrets, and retained artifacts can be modified after validation. Sanitized output, hashes and revision checks reduce selected risks but do not prove that all sensitive content has been removed. A future study should test the specific attack and mutation surfaces it claims to cover instead of inferring security from the existence of a temporary directory.

<!-- PAGE -->
## 2.7 Qualitative comparison of approaches

Table 2.1 compares task emphasis in the cited sources. A statement that a capability is outside the described focus is not a claim that every version of the tool lacks it. The matrix is an analytical comparison of mechanisms, not a measured ranking.

[[TABLE:2.1|Task emphasis in representative related work|Approach|Primary focus|Relation to APIShield]]
oasdiff|OpenAPI comparison|Provides native difference evidence
REST testing tools|RESTler, RESTTestGen and RESTSpecIT|Probe providers or infer documentation
dcFix|REST specification-grounded LLM repair|Close comparator for localized API misuse
ASAP-Repair and APIfix|API usage graphs and adaptation synthesis|Establish API-specific repair precedent
RepairAgent and SWE-agent|General repository repair|Establish tool-guided repair precedent
SpecRover|Inferred intent during repair|Closest intent-related precedent
RepoGraph and Agentless|Structural context and bounded repair|Inform localization and pipeline baselines
APIShield|Contract-triggered migration with explicit checks|Combines scoped obligations and retained evidence
[[ENDTABLE]]

The practical distinction is the unit of work. APIShield's run is anchored to captured source and paired contracts, with a selected migration obligation. That makes a particular acceptance decision traceable. A general repair agent may offer broader editing ability, while a specialized provider-testing tool may explore runtime states that APIShield does not analyze.

The matrix therefore supports a reasoned application niche. It cannot establish that APIShield repairs more bugs, costs less or scales better. Those are separate hypotheses with different measurements. The study design uses the same engine and model across conditions to test the explicit-requirement mechanism without importing incomparable published scores.

<!-- PAGE -->
## 2.8 Research gap and testable contribution

The reviewed sources establish contract analysis, specification-grounded repair, API usage graphs, adaptation synthesis and inferred invariants as existing techniques. APIShield investigates an integration in which documented contract changes select consuming code, graph context informs repair, and scoped behavioral checks govern acceptance. The proposed distinction is the incremental effect of those mechanisms under matched conditions and an independent oracle.

The primary hypothesis is that explicit, applicable checks reduce behaviorally incorrect accepted patches compared with an otherwise equivalent test-guided migration pipeline. A secondary hypothesis is that traceable impact and requirement evidence help reviewers identify unsupported or ambiguous changes. These are hypotheses about outcomes, not consequences that automatically follow from the architecture.

Novelty requires care in two respects. First, a selected literature review does not establish that no previous system combines similar ideas. Second, even a distinct combination must have a demonstrated benefit to support a strong research contribution. The present report establishes the artifact and a mechanism-level argument; the controlled study remains a necessary next step.

The gap can be evaluated through explicit questions. Does the requirement mechanism reject the cents-to-dollars trap when ordinary tests are weak? Does it preserve correct endpoint migrations? Does it request input when a newly required address is unavailable? How much additional time and test execution does it require? Can a reviewer trace the decision without reading raw logs?



<!-- PAGE -->
# CHAPTER 3
# REQUIREMENTS AND PROJECT SCOPE
## 3.1 Users and operating workflow

The primary user is a developer responsible for a Python integration. The user needs to decide whether a provider change affects the application, what a proposed repair changes and whether its validation is sufficient for review. The local browser interface reduces the amount of command-line coordination needed for those decisions.

The workflow starts by connecting a local repository and supplying accepted and observed JSON OpenAPI descriptions. Current views include working edits, while retained jobs preserve their captured inputs. A scan exposes supported calls; comparison identifies changed operations and matched consumers. The developer can declare business requirements, select their source scope and link committed pytest references. Confirmation is an explicit review action.

When a repair is requested, the system creates a disposable source copy and captures the selected configuration and contracts. It generates or loads a candidate, checks its permitted edit targets and runs validation. A successful proposal remains a patch with evidence. The user can download it, prepare a GitHub draft preview or explicitly apply a current browser repair. Apply verifies input freshness and retains original bytes for recovery.

[[FIGURE:3.1|User decisions from contract change to reviewed proposal|workflow]]

Figure 3.1 identifies the decision points that prevent an observed API change from being confused with an accepted deployment. Automated comparison and test execution support those decisions, while confirmation, paid generation and remote publication remain visible actions. The workflow also permits stopping after an impact report when the available information is insufficient for repair.

<!-- PAGE -->
## 3.2 Functional requirements

Functional requirements were derived from the migration task and the failure cases in the original demonstration. The common engine is important because the browser and CLI must apply the same acceptance rules. A frontend status label should reflect retained engine evidence rather than infer success from a log message.

[[TABLE:3.1|Functional requirements and implementation locations|ID|Required behavior|Principal implementation]]
FR01|Capture committed or working source|configuration.py and workspace.py
FR02|Report supported calls and limitations|analysis.py
FR03|Compare retained API contracts|comparison.py and native oasdiff
FR04|Confirm scoped behavioral requirements|requirements.py and browser_setup.py
FR05|Validate constrained candidates|editing.py and engine.py
FR06|Retain reports and cancellation state|jobs.py and dashboard_jobs.py
FR07|Monitor approved contract sources|monitoring.py and monitor_state.py
FR08|Prepare and explicitly publish full drafts|publication modules and github_cli.py
FR09|Present evidence and patch downloads|Workspace and RunEvidence components
[[ENDTABLE]]

Each requirement has a boundary. For example, FR02 does not imply complete Python analysis, and FR07 does not imply operation while the local server is stopped. FR08 requires a validated retained repair and a compatible remote base; it is not a route for publishing arbitrary working-tree changes.

This traceability table is a development aid rather than an independent certification. The implementation and regression tests supply the actual behavior, while dated validation records show selected executions, including the banking fixture (APIShield Project, 2026a). Future changes should update the affected requirement row and evidence references together so that a renamed module does not leave the report describing an obsolete interface.

<!-- PAGE -->
## 3.3 Quality requirements and execution limits

Correctness evidence, recoverability and source preservation are more important than unrestricted autonomy in the initial product. A failed candidate must not leave an edited original repository, and an unavailable model must not produce a fabricated validated status. A timed-out or cancelled command must retain its outcome even if partial output appears successful.

The engine uses finite budgets for attempts, command duration, total job duration and captured output. The defaults are configuration values, not measured performance claims. Specific acceptance runs use their own recorded limits, which are reported with those cohorts.

[[TABLE:3.2|Default local execution budgets|Setting|Default|Interpretation]]
Repair attempts|3|Maximum engine attempts for live generation
Command timeout|120 seconds|Upper limit for one repository command
Job timeout|600 seconds|Overall execution deadline
Captured output|65,536 bytes|Bound on recorded command output
Browser worker pool|2 workers|Local background job executor size
[[ENDTABLE]]

Recoverability includes durable results, interrupted-worker detection, process-tree cleanup and explicit publication reconciliation. Local filesystem records are appropriate for a single-machine prototype, but they do not provide the availability or isolation guarantees of a hosted service.

Usability requires that evidence remain accessible without opening every raw artifact. The interface therefore separates overview, impact, proposed changes, tests and technical provenance. Accessibility includes keyboard navigation and a graph List fallback. The recent UI source changes still need fresh browser visual verification, so layout quality is not treated as a fully measured quality attribute in this report.

<!-- PAGE -->
## 3.4 Behavioral requirements and acceptance obligations

A behavioral requirement identifies a property that a migration should preserve. The current declaration includes an identifier, prose description, exact file/function scope, origin, confirmation status and selected pytest references. Its canonical hash becomes part of the run record, allowing a reviewer to distinguish a current rule from the rule captured by an earlier job.

For shipping, a representative rule preserves package identity and exact integer gram weight. For payment, a useful obligation preserves the exact cents value supplied by the caller. Refund behavior additionally requires the correct operation and transaction identity. An invoice migration may need information absent from the function inputs; in that case a diagnostic is the admissible outcome.

[[TABLE:3.3|Example preservation rules and independent observations|Rule|Observable obligation|Failure example]]
Exact amount|Integer payload equals caller amount|Float conversion loses a large integer
Identity|Identifier survives the request unchanged|Customer or package ID replaced
Operation|Request uses the intended action|Refund changed into charge
Response behavior|Returned value follows actual provider reply|Hardcoded success ignores transport
Missing information|No unsupported data invented|Default address silently inserted
[[ENDTABLE]]

Confirmation means that a developer approved the definition and its current scope. It does not prove the prose or guarantee that the linked tests are complete. Editing the definition or changing repository/source/test context clears confirmation. During repair, applicable confirmed rules with unresolved scope or unavailable checks require input. The engine records discovery and execution evidence separately so that a syntactically valid test reference cannot masquerade as an executed passing assertion (APIShield Project, 2026d).

<!-- PAGE -->
## 3.5 Constraints, assumptions and feasibility

The implementation assumes trusted repositories because setup and tests execute code on the local host. Candidate isolation protects source preservation, while host security remains the operator's responsibility. No customer account system or tenant boundary is present. The launcher binds the application to loopback, consistent with that operating model.

Native oasdiff, Git, Python and frontend build tooling are prerequisites. The model connection is optional for offline examples. Live generation uses a selected Gemini connection; service-account credentials captured through the browser remain in server memory. GitHub drafts use the existing local GitHub CLI credential store. These integrations have distinct lifetimes and failure modes.

Technical feasibility is supported by the implemented shipping and banking examples and the recorded live acceptance cases. Research feasibility is supported by an opt-in harness, retained patches and independent checks. Neither establishes that a large real-world study will have a positive result. Environment preparation, fixture selection and oracle quality can dominate effort when moving beyond synthetic examples.

The project excludes automatically merging or deploying changes. That decision keeps publication evidence separate from application release. It also makes the product usable when a model fails: the developer can still inspect contract differences and source impact without requesting generation.

The remaining scope is therefore concrete. Deeper field observations, broader call resolution and per-integration test environments can extend supported coverage. Controlled baselines can test the proposed academic contribution. Hosted scheduling and isolated workers require a separate architecture. These are different deliverables and should not be presented as if completion of one automatically establishes the others.

<!-- PAGE -->
# CHAPTER 4
# SYSTEM ARCHITECTURE AND DATA DESIGN
## 4.1 Architecture overview

APIShield has a browser presentation layer, a FastAPI coordination layer and a reusable Python execution engine. The browser submits an integration operation and reads retained evidence. The API validates requests, coordinates local background work and exposes job, monitoring, model and publication endpoints. The engine performs the captured-source repair transaction.

The command-line interface calls the same engine. This reduces the risk that a browser shortcut bypasses the acceptance checks described in the methodology. A deterministic offline candidate uses the same editing and validation stages as model output, while bypassing inference.

[[FIGURE:4.1|Current local architecture and external boundaries|architecture]]

The local job store persists configuration snapshots, contract copies, events, command evidence and results. Temporary workspaces are removed when jobs finish, while validated patches remain available. Monitoring and publication maintain their own durable lifecycle records under the local storage root.

External boundaries are explicit: native oasdiff supplies comparison evidence; a configured Gemini endpoint supplies candidate generation or optional graph interpretation; GitHub CLI mediates publication. The provider and SwiftPay services belong to the legacy demonstration and can run separately. A normal shipping-example workflow does not need those payment services or a model connection.

This is the current deployed topology on a local computer. A database-backed queue, container worker and tenant-aware service appear in the roadmap but are not part of Figure 4.1. The report describes those as future work rather than borrowing the properties of a proposed hosted architecture.

<!-- PAGE -->
## 4.2 Backend modules and responsibilities

The apishield package separates configuration, source preparation, analysis, execution and publication. Its boundaries are logical responsibilities rather than independently deployed services. Keeping the engine free of browser state allows both interfaces and the research harness to invoke the same core operation.

[[TABLE:4.1|Backend subsystem responsibilities|Subsystem|Principal files|Responsibility]]
Configuration|configuration.py|Validate paths, commands, budgets and rules
Source snapshot|workspace.py|Read pinned Git objects into a disposable copy
Analysis|analysis.py and repository_graph.py|Observe supported calls and source relationships
Execution|engine.py and commands.py|Bound attempts, run commands and enforce acceptance
Evidence|jobs.py and overview.py|Persist records and reconstruct retained views
Model access|generation.py and model_access.py|Select connection and request structured output
Monitoring|monitoring.py and contract_fetch.py|Fetch approved contracts and reserve comparison work
Publication|publication.py and publication_prepare.py|Revalidate complete patch and coordinate drafts
[[ENDTABLE]]

dashboard_api.py still includes payment-demo control state. The newer browser routes are attached through dedicated modules, including browser_setup.py, dashboard_jobs.py and publication_api.py. This coexistence explains why the repository contains both an older mutable repair demonstration and a newer isolated workflow.

The distinction matters during maintenance. A fix to the legacy agent does not automatically change the shared engine, and a report claim about source-preserving jobs must refer to the isolated path. The retained examples and regression tests help prevent the two execution models from being confused.

<!-- PAGE -->
## 4.3 Job lifecycle and durable records

A job has an identity, operation, configuration snapshot and filesystem location. Its source revision and contract hashes establish the inputs. Scan and comparison jobs can complete without proposing edits; repair jobs add candidate attempts and validation evidence. Terminal outcomes distinguish validated, failed, cancelled, no change and needs input.

[[FIGURE:4.2|Job lifecycle with guarded acceptance outcomes|states]]

OS-level ownership locks prevent two local workers from executing the same retained job concurrently. The store uses atomic replacement for structured records. Cancellation is persisted and checked during work; an interrupted process is detected rather than silently resumed from a partially applied candidate.

The worker captures source metadata before analysis and retains it independently of the disposable workspace. Each attempt records setup and validation commands, errors and requirement outcomes. A validated patch is written from the engine's independently checked candidate bytes. Failed jobs do not offer a patch as if it had passed.

Recovery does not mean that every operation can be undone. Local workspace cleanup is different from a remote GitHub request whose response was lost. The publication subsystem therefore has reconciliation states in addition to ordinary execution failure. This keeps a valid local repair from being relabeled invalid merely because publication encountered an uncertain remote effect.

The filesystem store is intentionally local. Its lock and atomic-write mechanisms support the current usage, but a distributed worker pool would need different coordination and recovery design. The existence of durable JSON records should not be described as a complete distributed job platform.

<!-- PAGE -->
## 4.4 Source, contract and requirement records

Committed-mode records identify the pinned commit and excluded working edits; the engine reads raw Git blobs. Working-mode records retain file hashes and captured bytes so current browser operations include uncommitted source. Both modes bind validation to a stable captured input. Symlink or submodule entries are unsupported; known secret-file patterns are excluded from exported content.

Contract snapshots are retained with hashes. This is important because comparison and revalidation must refer to the versions that produced the original decision, not whatever files happen to exist when a reviewer returns later. The run also captures the complete selected requirement set and its canonical hash.

[[TABLE:4.2|Retained records and their provenance role|Record|Representative contents|Purpose]]
Configuration|Repository, ref, paths, commands and budgets|Reconstruct selected execution inputs
Source metadata|Source mode, commit and captured file hashes|Identify the exact analyzed source
Contracts|Original and updated JSON plus hashes|Bind comparison to exact descriptions
Requirement set|Definitions, checks and canonical hash|Bind acceptance to reviewed declarations
Attempts|Commands, outputs and requirement results|Explain candidate acceptance or rejection
Final result|Status, errors and patch digest|Expose durable review outcome
[[ENDTABLE]]

Hashing detects selected evidence changes when the relevant checks are performed. It is not a digital signature or an assurance against every actor with local filesystem access. The provenance value comes from retaining exact inputs and validating their consistency at important transitions, especially publication preparation.

Later edits to an integration create new configuration context. They do not rewrite previous job evidence. Historical overview enrichment reads retained snapshots with guards, preserving the distinction between the original run and a current presentation of its data.

<!-- PAGE -->
## 4.5 Repository graph and evidence provenance

The repository graph includes supported files, classes, functions, tests and API operations. Python AST traversal supplies declarations and selected call relationships. Source docstrings can supply declared intents. Developer requirements link function scopes to selected tests. Limited JavaScript and TypeScript analysis adds named functions and literal fetch-route relationships.

[[FIGURE:4.3|Observed and declared relationships in a migration graph|graph]]

An operation changed by contract comparison and its direct consuming function receive direct impact. Resolved callers can receive potential impact. Potential impact means dependence on affected code, not an observed runtime failure. The node inspector records that reason so that a red mark does not imply more evidence than exists.

The graph scan is bounded to 500 files, 256 KiB per file and 2 MiB of source text. Its own coverage notes accompany the graph. Dynamic dispatch, ambiguous routes and unsupported syntax remain unresolved. The graph's broader structural coverage does not expand the set of files the repair engine may edit.

Community detection groups recorded relationships for presentation. Optional Gemini interpretation can assign business-flow communities and separately labeled inferred links. Those overlays are tied to the graph hash and validated against existing node identities. They do not add verified calls, alter impact localization or satisfy requirements. This boundary permits an interpretive display without treating a model's explanation as executable evidence (APIShield Project, 2026c).

<!-- PAGE -->
## 4.6 Browser review workspace

The React workspace exposes current API views, retained runs, code changes, tests, settings and optional GitHub drafts through structured engine reports.

Current views show active contracts and consumers; change reports retain paired contracts and impact evidence. The graph supports source inspection and a List fallback. Reviewed Apply writes repairs and generated tests without a commit, rejects stale inputs and retains recovery bytes. Success accepts the captured contract and refreshes the current graph while preserving historical evidence (APIShield Project, 2026j).

[[TABLE:4.3|Review panels and the decision each supports|Panel|Evidence shown|Review question]]
Overview|Original and updated contract details|What changed in the described interface?
Impact graph|Observed and declared relationships|Which supported consumers may be affected?
Code changes|Retained candidate patch|What exactly does the proposal edit?
Tests and rules|Commands and separate requirement outcomes|Which assertions were actually checked?
Technical details|Coverage and provenance|What revision and limitations apply?
GitHub draft|Prepared full proposal and state|What will be published and has it succeeded?
[[ENDTABLE]]

The report uses architecture diagrams to describe verified interfaces. Fresh visual acceptance of the latest browser changes remains pending.

<!-- PAGE -->
## 4.7 Monitoring and publication coordination

Monitoring stores an approved contract source, an interval, a baseline and immutable fetched versions. A scheduled check reserves comparison work, deduplicates a known change and exposes its report. Baseline acceptance is explicit. A rescan can update code impact for a retained change without pretending that the provider published another version (APIShield Project, 2026h).

Publication begins with a validated retained repair. Preparation reconstructs its complete patch using guarded Git patch operations and runs offline validation against the pinned source (Git project, n.d.). The preview binds repository, base, patch and evidence to revisions. Publication then checks remote state and creates a draft through the existing GitHub CLI sign-in.

[[FIGURE:4.4|Separate repair validation and draft publication|publication]]

These are separate state machines because their failures differ. A provider fetch can fail without invalidating previous change evidence. A remote publish response can be lost even though a draft was created. Reconciliation checks retained identity and remote effects before another write, reducing duplicate proposals.





<!-- PAGE -->
# CHAPTER 5
# METHODOLOGY AND IMPLEMENTATION
## 5.1 Source capture and workspace preparation

The engine validates configuration and allocates a job outside the repository. Committed mode resolves a Git revision and exports its objects. Working mode captures current permitted files and hashes, including uncommitted edits. Retries use the same retained input; later source changes require a new capture.

Workspace preparation inventories the selected source mode and reads its retained bytes. Paths are checked for escape, unsupported entry types and collisions. Known credential-file patterns are not exported. The copied tree is then available for analysis and trusted test execution without changing the original source.

[[FIGURE:5.1|Inputs and integrity checks for one repair attempt|pipeline]]

Before each repair attempt the workspace is recreated from the pinned source. This prevents a failed candidate from becoming an undocumented starting point for the next candidate. The engine inventories protected bytes and modes, then checks that repository commands have not altered protected source, tests, configuration or retained contracts.

This design is useful for reproducibility because a retry can be interpreted relative to the same committed baseline. It also has practical costs: repeated preparation and test discovery consume time, and the application environment must already contain required test dependencies. Per-integration environment setup remains unfinished.

The method does not make repository execution safe against malicious code. A copied test can still attempt host actions. The present execution model is explicitly for trusted local repositories. That assumption must remain visible when interpreting source-preservation evidence or considering a future hosted deployment.

<!-- PAGE -->
## 5.2 Static call discovery and impact localization

The repair scanner parses Python syntax and tracks supported imports and string assignments. It recognizes direct requests/httpx GET and POST calls and attempts to resolve their URLs. Literal paths and supported static combinations can be localized; reassigned imports, wrappers, client instances and unresolved expressions produce coverage notes.

Comparison produces a set of changed method/path operations. Matching normalizes path-parameter names so that equivalent placeholders can align. A changed operation is matched to supported consuming sites. Shared components, security or server changes conservatively mark operations as changed rather than claiming precise field-level causality.

[[TABLE:5.1|Localization decisions in the supported scanner|Source pattern|Decision|Reason]]
Direct imported HTTP call and static URL|Record operation|Supported binding and path
Resolvable static string combination|Record when valid|Value can be recovered conservatively
Dynamic host or unsupported expression|Record limitation|Operation identity is uncertain
Wrapper or client-instance call|Do not infer endpoint|Wrapper semantics are outside subset
Reassigned HTTP import|Do not use stale binding|Original import no longer establishes call identity
[[ENDTABLE]]

The repository graph can add caller relationships for review, but repair localization remains constrained to the scanner's affected Python files. This distinction avoids using a presentation graph as permission to edit every reachable node.

Localization quality has not yet been measured against an independently annotated benchmark. The controlled study therefore records supported-site precision, recall and abstention separately. A system that reports fewer sites may be conservative or incomplete; a simple count cannot distinguish those explanations without an oracle.

<!-- PAGE -->
## 5.3 Requirement applicability and test discovery

A requirement becomes relevant through its declared function scope and relationships to affected source calls. The engine checks whether the scope is resolvable and whether selected checks exist in the pinned revision. A relevant confirmed rule without usable evidence requires input before generation proceeds.

The complete pytest selector is discovered, not merely the file containing it. This matters when a test has been renamed or when a selector refers to an absent class/function. The engine checks collection output and command status under execution budgets. Truncated discovery output cannot establish that the selected check was found.

After a candidate is applied, selected checks run separately from the ordinary configured validation. JUnit evidence establishes whether test cases actually executed and passed. Skipped, empty, failed or erroneous results do not count as a passed requirement. pytest supports structured result reporting, which the engine uses as one evidence source (pytest development team, n.d.).

[[TABLE:5.2|Requirement decision outcomes|Condition|Outcome|Meaning]]
Relevant confirmed rule with collected checks|Pending execution|Acceptance evidence still required
Applicable check cases pass|Passed|Selected assertions succeeded
Skip, empty suite, failure or error|Failed evidence|Rule is not established
Unresolved affected scope or unavailable selector|Needs input|Developer action is required
Edited rule or changed context|Unconfirmed definition|Review must be repeated
[[ENDTABLE]]

The mechanism is intentionally limited by test quality. A developer may confirm an incomplete check. The engine can establish that the check ran, but cannot infer that it expresses every nuance of the prose. Independent evaluation tests are therefore needed to assess whether accepted repairs preserve behavior beyond the selected development checks.

<!-- PAGE -->
## 5.4 Candidate generation and missing information

Generation receives impacted source, paired contracts, comparison evidence and graph context. The browser AI path infers scoped rules and creates separate checks under tests/apishield_generated. Inferred rules retain their AI origin; they are not developer-confirmed truth. Existing tests remain protected. Generated checks must meaningfully fail against incompatible original code and pass after repair. Public feedback can support bounded retries; independent hidden checks remain outside generation (APIShield Project, 2026j).

The model must return either structured patch objects or a nonempty diagnostic explaining missing information. Each patch names a file and exact old/new snippets. The generator uses a typed response schema, while the engine still validates the returned object. A response schema reduces format ambiguity but does not establish semantic correctness.

The instruction treats source, contract text and command output as untrusted data. That is a prompt boundary, supported by independent edit and execution restrictions. It should not be described as a complete prompt-injection defense.

[[FIGURE:5.2|Public repair context and independent evaluation boundary|oracle]]

Missing-information behavior is part of the task. If an updated invoice operation requires a real address and the function receives no such information, inventing plausible fields would produce a dangerous appearance of completion. A useful diagnostic identifies the absent input and the reason a preservation obligation cannot be met.

The generated diagnostic also requires evaluation. A model can decline a repairable case or state an irrelevant reason. The proposed study therefore uses explicit human review of diagnostic adequacy. It does not count every needs-input response as correct abstention. This distinction follows the existing harness correction that leaves generated abstentions awaiting diagnostic review rather than automatically accepting them.

<!-- PAGE -->
## 5.5 Structural editing and candidate integrity

The editor checks the whole candidate before committing its permitted replacements. A target must be an impacted configured Python source file. Tests, contracts, configuration, test hooks and files outside the allowed paths are rejected. The original snippet must match exactly once in the pinned content.

Multiple replacements in a file are checked for overlapping spans and applied against the same original source. This avoids a common failure in sequential string editing, where one replacement changes the text expected by another. The resulting source is parsed as Python before it is written.

The engine then runs configured tests and requirement checks. Integrity inventories detect repository commands that modify protected files or change the candidate during validation. The final retained patch is derived from checked bytes rather than trusting a patch file produced by repository code.

[[TABLE:5.3|Candidate rejection conditions|Condition|Rejected because]]
Ambiguous or absent old snippet|Target cannot be identified uniquely
Overlapping replacements|Candidate edits conflict in the pinned source
Test or configuration target|Candidate could weaken acceptance conditions
Outside allowed source paths|Edit exceeds localized repair scope
Invalid Python output|Candidate is structurally unusable
Protected bytes changed during commands|Validation no longer checks the expected artifact
[[ENDTABLE]]

These guards reduce classes of accidental and adversarial error. They do not make string replacements equivalent to a complete semantic transformation system. A syntactically valid edit can still be behaviorally wrong; that is why acceptance depends on executable evidence and why independent checks are needed to evaluate the method.

<!-- PAGE -->
## 5.6 Acceptance, retries and outcome semantics

A repair is validated only when configured validation succeeds and every applicable pending requirement obtains passing evidence. A source scan or contract comparison completes without that status because it has not tested a migration. A no-change outcome likewise means that no contract operation change was identified, not that application behavior has been proved correct.

Live generation uses a finite attempt budget. Eligible provider failures consume that budget, and failed validation supplies feedback to a later attempt when allowed. An explicit offline candidate is evaluated once and never falls back to model inference. This prevents an apparently free deterministic example from silently making a paid request.

[[TABLE:5.4|Engine outcomes and their interpretation|Outcome|Interpretation|Review consequence]]
Completed|Scan or comparison finished|Inspect findings and coverage
Validated|Candidate passed configured and applicable checks|Review retained patch
Needs input|Required information or checks are unavailable|Resolve diagnostic
Failed|Execution or validation did not succeed|Inspect attempt evidence
Cancelled|Cancellation interrupted work|No validated proposal follows
No change|No changed operations found|Review contract and coverage assumptions
[[ENDTABLE]]

Cancellation and deadlines are checked during source preparation, commands and model access. Process cleanup is part of the local execution design. The evidence record distinguishes timeout and cancellation rather than inferring success solely from a zero exit code or partial output.

Acceptance remains bounded by the assertions available. The result should be read as a tested proposal for a particular revision and contract pair. Automatic deployment or universal semantic correctness would require evidence beyond what this engine establishes.

<!-- PAGE -->
## 5.7 Model access, implementation stack and operations

The current local engine defaults to the model name recorded in its configuration, with Gemini 3.8 Flash used in the later Cloud acceptance records. Explicit integration settings are retained. The legacy demonstration has a separate configuration path, so historical defaults should not be mistaken for one universal project setting.

Browser model settings distinguish configured and tested connections. A connection test makes a small explicit request; it verifies access, not repair quality. Captured service-account credentials are session-only, and repository subprocesses receive a minimal environment without controller model or GitHub credentials. Transport code enforces deadlines and bounds responses.

[[TABLE:5.5|Implementation stack by responsibility|Layer|Principal technologies|Role]]
Local engine|Python 3.11+, Git and native oasdiff|Snapshots, comparison and execution
API|FastAPI, Uvicorn and Pydantic|Coordination and validated interfaces
Model|Google GenAI and Google Auth|Explicit candidate and interpretation requests
Analysis|Python AST and NetworkX|Bounded relationships and communities
Browser|React, Vite, D3 and Tailwind|Review workspace and graph interaction
Validation|pytest and Node test runner|Behavior checks and presentation helpers
Drafts|GitHub CLI|Existing local authorization and remote API actions
[[ENDTABLE]]

The Windows launcher builds the frontend, starts the loopback API and opens the browser. The production frontend can be served by the API. Optional Docker Compose configuration supports the payment demonstration; it is not evidence of a production hosting deployment.

No new application tests, live model calls or remote GitHub actions were performed to create this report. The next chapter analyzes the existing dated acceptance records and preserves their stated limitations.

<!-- PAGE -->
# CHAPTER 6
# RECORDED EVALUATION AND DISCUSSION
## 6.1 Evidence sources and interpretation

The available evaluation comprises historical engineering acceptance, a controlled GitHub draft exercise, authored benchmark qualification and live inference diagnostics. These sources answer different questions. Offline tests examine engine and interface behavior under controlled conditions. Live acceptance examines actual generated proposals. The draft exercise checks publication of a complete retained repair.

The results in this chapter are taken from existing project records. They were not rerun for this document, and counts apply to their recorded revision and environment. A historical green suite does not establish that every later working-tree change passes. Source inspection supports the architectural description but is not a substitute for execution evidence.

[[TABLE:6.1|Recorded evidence cohorts|Record|Scope|Evidence class]]
12 October assessment|20 jobs across separate model/protocol batches|Exploratory synthetic live repair
13 October Cloud acceptance|Six cases and eight generation calls|Bounded live engineering acceptance
13 October guided follow-up|Browser shipping and exact-money repairs|Targeted live follow-up
13 October GitHub draft exercise|Two-file synthetic shipping proposal|Controlled remote publication
14 October graph/UI records|Graph regressions, build and layout checks|Source and numerical verification
[[ENDTABLE]]

No single aggregate accuracy is calculated across these cohorts. Differences in model, protocol, retry rules and task selection would make such a percentage difficult to interpret. The chapter instead reports the actual denominators and the specific behavior observed. This supports useful conclusions about demonstrated cases while leaving comparative effectiveness to the controlled design in Chapter 7.

<!-- PAGE -->
## 6.2 Initial exploratory live assessment

The initial assessment records twenty jobs and twenty-eight model requests across four distinct matrix/follow-up batches. Nine retained repair patches passed strengthened held-out checks. Ten jobs ended in provider failures and one in a response-format failure. All fourteen fixture repositories retained unchanged tracked source and tests (APIShield Project, 2026f).

[[TABLE:6.2|Initial live assessment reported outcomes|Measure|Recorded value|Qualification]]
Jobs|20|Multiple batches and configurations
Model requests|28|Includes bounded retries
Verified repair patches|9|Passed strengthened held-out checks
Terminal provider-failure jobs|10|Availability prevented a completed proposal
Response-format failure jobs|1|Boolean diagnostic rejected
Fixture repositories preserved|14|Tracked source/tests remained unchanged
[[ENDTABLE]]

The checks covered endpoint migration, request/response nesting, exact integer cents and refund operation identity. The stronger oracle verified that the function actually made one transport call, used the expected destination and data, and propagated a varying server reply. This reduced the chance of counting a hardcoded return value as a correct repair.

The initial missing-address category did not establish correct live abstention. A returned boolean lacked the required diagnostic, and later requests were blocked by provider failures. The engine's refusal to validate that malformed output is useful failure handling, but it is not a successful missing-information response.

The study was exploratory and the oracle strengthening was post-hoc. The saved successful patches were rechecked offline under the stronger oracle. Those corrections improve the artifact evidence, while limiting any attempt to interpret the batches as a preregistered experiment or a comparison of model quality.

<!-- PAGE -->
## 6.3 Google Cloud acceptance cohort

The subsequent Cloud acceptance used the production engine with Gemini 3.8 Flash, at most two attempts per case and a twelve-call ceiling. Eight generation calls were made across six scenarios. Four repairs passed independent checks; the missing-address case returned a reviewed needs-input diagnostic; the exact-money case failed after two HTTP 504 responses (APIShield Project, 2026b).

[[TABLE:6.3|Six-case Cloud acceptance outcomes|Scenario|Engine outcome|Generation calls]]
Endpoint move|Validated and independently checked|1
Request payload nesting|Validated after one 504|2
Response nesting|Validated and independently checked|1
Exact money units|Failed on two 504 responses|2
Refund semantics|Validated and independently checked|1
Missing billing address|Needs input with reviewed diagnostic|1
[[ENDTABLE]]

All original sources remained unchanged. The missing-address diagnostic explained that the updated API required street, city and postal code while the function did not receive them. Its adequacy was reviewed directly. This is evidence for one case, not a measured abstention rate over a representative population.

The money failure concerns service availability; the independent behavioral checks were not reached. Classifying it as a semantic failure would misdescribe the observation. Removing it from the end-to-end outcome count would also hide a practical limitation of the workflow.

Reported usage was available for five generation responses, while three failed calls supplied no usage. The record therefore does not provide a complete billing total. This chapter retains the behavioral outcomes and request counts without converting incomplete token information into a cost-efficiency claim.

<!-- PAGE -->
## 6.4 Guided browser and exact-money follow-up

The guided acceptance follow-up exercised the real browser model connection and shipping repair. The endpoint move validated on the first attempt, and both configured validation and the confirmed identity/weight check passed. The retained patch changed the endpoint while keeping the request data, error handling and response behavior (APIShield Project, 2026g).

The targeted exact-money follow-up also validated on its first attempt. Its independent checks included one cent, a Unicode identifier and the integer 9,007,199,254,740,993. They checked the destination, request data, invocation count and returned response. The recorded job duration was 6.53 seconds, with one generation call. This is a single observation, not a latency benchmark.

[[TABLE:6.4|Guided acceptance observations|Check|Recorded result|Interpretation]]
Browser connection test|Passed|Application could access selected provider
Shipping generation|Validated on attempt 1|Endpoint and exact-weight checks passed
Exact-money generation|Validated on attempt 1|Large integer and independent behavior passed
New requests in follow-up|3|One connection test and two generations
Original source|Unchanged|No generated patch applied to original checkout
[[ENDTABLE]]

This follow-up supplies evidence missing from the earlier timeout-only money result. It does not erase those timeouts or imply that every amount transformation is safe. The tested integer cases are valuable because floating-point conversion could lose exactness, but broader currencies, decimal conventions and provider behavior remain outside that small fixture.

The browser shipping report and separate money harness also have different instrumentation. A combined token total is not reported because complete comparable usage was not retained for both. Keeping these distinctions prevents a useful acceptance result from becoming an unsupported performance or cost claim.

<!-- PAGE -->
## 6.5 GitHub publication and regression evidence

The controlled publication exercise used a synthetic shipping repository and a complete two-file patch. Both original fixture tests failed on the old routes. The retained repair and an offline revalidation passed, and the remote draft contained exactly the two intended source files. Repeating publication returned the same draft identity (APIShield Project, 2026e).

The record also reports restored target/proposal information after restart and unchanged local fixture source. No paid generation calls occurred in that stage. GitHub CI was not verified, and the proposal remained a draft at the time of the recorded exercise. The report makes no claim about its current remote state.

[[TABLE:6.5|Selected historical regression and delivery records|Recorded stage|Python evidence|Frontend evidence]]
Cloud acceptance delivery|360 passed and 1 platform skip|22 tests and production build passed
GitHub draft delivery|426 passed and 1 platform skip|27 tests and production build passed
Latest recorded UI refinement|Targeted backend records elsewhere|56 tests and production build passed
[[ENDTABLE]]

Table 6.5 contains snapshots at different revisions. The values must not be added together, treated as a current total or interpreted as repair accuracy. The documented lint runs retained six pre-existing demo warnings. Recent source/numerical graph checks do not constitute fresh browser drag or visual-fidelity acceptance.

The draft exercise demonstrates a useful engineering property: publication failure can be separated from repair validation, and a multi-file proposal can retain one complete identity. It does not establish behavior under every remote race. The implementation checks stale checkpoints and supports reconciliation because the remote repository can change between requests.

<!-- PAGE -->
## 6.6 What the evidence supports

The strongest supported conclusion is that the implemented workflow can produce and retain correct proposals for selected synthetic migrations while preserving original source. The records include actual generation, independent checks, a reviewed missing-information diagnostic and a complete draft-publication exercise. They provide more evidence than a screenshot or an unexecuted architecture diagram.

The requirement mechanism also makes acceptance inspectable. The browser shipping follow-up records discovery and execution of a confirmed preservation check separately from ordinary validation. This demonstrates the implemented connection between a declaration and executable evidence for that task. It does not isolate the causal benefit of the mechanism, because no matched baseline was run in that acceptance exercise.

[[TABLE:6.6|Claims and present evidence strength|Claim|Current position]]
Selected endpoint and nesting repairs can work|Supported by dated synthetic acceptance
Exact integer preservation can work in the fixture|Supported by targeted independent checks
Unavailable input can produce a useful diagnostic|Supported by one reviewed address case
Original source is preserved in recorded jobs|Supported for the documented fixtures
Requirements improve correctness over a matched baseline|Unmeasured comparative hypothesis
The system is universally novel or production reliable|Not established
[[ENDTABLE]]

Practical benefits are clearest at the workflow level. A retained patch, contract pair, source commit and test record reduce ambiguity about what was checked. The impact display can direct a reviewer to supported consumers. Missing-input states make failure actionable. None of these observations justifies a fabricated percentage improvement in correctness, speed or developer effort.

The next study should retain the demonstrated end-to-end path and vary the mechanism under controlled conditions. Otherwise, differences in model access, case difficulty or test quality could be mistaken for improvements caused by explicit requirements.

<!-- PAGE -->
## 6.7 Threats to validity and unresolved evidence

Internal validity is limited by protocol changes during exploratory assessment. Retries, response typing and oracle strengthening were introduced at different points. Later improvements may be useful, but the batches cannot isolate which change caused a better result. A controlled study should freeze the engine and label every condition before execution.

Construct validity concerns what is measured. Configured-test success can differ from behavioral correctness, particularly when tests omit units or accept hardcoded replies. Held-out checks improve the observation but remain finite. A requirement's prose may also be broader than its linked tests, so confirmation alone is not an oracle.

External validity is limited by small hand-authored integrations with mocked transport. Production repositories contain wrappers, generated clients, larger test dependencies and undocumented provider behavior. Those factors can reduce localization coverage or prevent execution before generation begins.

[[TABLE:6.7|Validity risks and planned controls|Risk|Effect|Control for the next study]]
Synthetic task selection|Favors implemented subset|Add independent real migration cases
Protocol and model changes|Confounds batch comparisons|Freeze versions and budgets
Weak or leaked oracle|Inflates behavioral success|Keep held-out checks outside prompts
Provider outages|Changes task completion rate|Report end-to-end and conditional outcomes
Small sample|Unstable estimates|Repeat and report uncertainty by case
Developer-authored rules|May encode expert knowledge advantage|Record authorship and compare context budgets
[[ENDTABLE]]

Unresolved evidence includes comparative baseline results, representative localization scores, review-effort measurements and current visual acceptance of the latest UI. These are recorded as missing measurements rather than filled with plausible estimates. The absence of those results constrains the conclusion, while the implemented artifact and evaluation protocol remain available for completing them.

<!-- PAGE -->
# CHAPTER 7
# BENCHMARK AND INFERENCE EVALUATION
## 7.1 Evaluation population and experimental design

The retained evaluation package contains four executable request-builder tasks, six treatment configurations and three passes of live inference on one banking task. Qualification establishes whether the evaluator distinguishes selected correct and incorrect candidates. Live inference establishes provider responses, generated diffs and resource usage. The two populations answer different questions and are analyzed separately (APIShield Project, 2026i).

The executable manifest contains TASK-BANK-014, TASK-BANK-015, TASK-PAY-008 and TASK-SHIP-029. Each supplies source, old and new contracts, public tests, hidden inputs, a hidden oracle and a reference patch. The tasks cover exact monetary values, beneficiary or transaction identity, shipping weight and idempotency keys. They belong to three domain families and share the local authored-fixture repository designation. They do not constitute 120 independent evaluated migrations.

The wider study targets 120 tasks across banking, payments, shipping and schema migrations. Corpus expansion and its completed model-generated evaluation remain separate completion requirements. Descriptor collections and analytical scenarios do not increase the number of executable tasks or evaluated live repairs. The present empirical population is defined by the four physical task records and the retained live inference traces.

Table 7.1 specifies the implemented treatment switches. Existing tests and bounded feedback are enabled from B2 onward. Structural context enters B3, semantic clustering enters B4, and inferred intent with generated checks enters B5. B6 combines both additions. The independent evaluator remains common to every treatment.

[[TABLE:7.1|Implemented benchmark configurations|Condition|Authorized context|Development acceptance]]
B1 source and contracts|Code and paired API documents|Protected public tests after generation
B2 test feedback|B1 plus tests and bounded public feedback|Existing tests
B3 structural context|B2 plus structural localization|Existing tests
B4 semantic context|B3 plus inferred semantic groups|Existing tests
B5 intent checks|B3 plus inferred intent and generated checks|Existing and generated checks
B6 combined context|B3 plus semantic groups and inferred checks|Existing and generated checks
[[ENDTABLE]]

The research harness is separate from the browser application. Its structural representation is a small Python AST graph, and its task interface is a pure request builder. The application graph covers a broader, bounded source population. Equating these representations would overstate what the benchmark exercises.

<!-- PAGE -->
## 7.2 Oracle separation and acceptance semantics

The harness constructs prompts through a positive allowlist of client source, paired contracts and treatment-specific public context. Private oracle source, reference patches and hidden expected results are excluded. Semantic and intent stages receive only authorized context. Generated development checks remain fallible observations inferred from that context.

Public tests and enabled generated checks govern candidate selection and permitted feedback. Hidden evaluation follows final candidate selection and supplies no subsequent repair feedback. The candidate worker returns serialized request outputs; the trusted oracle evaluates assertions separately. Concrete hidden inputs are visible during final candidate execution, while assertion code and reference patches remain outside the candidate workspace.

Trusted qualification uses isolated native Python processes for authored candidates. Container execution is implemented with separate mounts, disabled networking and bounded resources, but the retained package records no successful Docker-boundary qualification. Live diagnostic runs consequently captured generation without executing candidates. This boundary determines which outcomes can be interpreted as behavioral measurements.

A delivered repair requires a valid candidate, public-test success, enabled generated-check success and independent hidden correctness. A syntax error, explicit abstention or provider failure supplies no hidden pass. A public-test pass followed by a hidden failure is classified as plausible but incorrect. Missing evaluation remains distinct from a measured failure.

## 7.3 Qualification outcomes and detection

The tooling qualification cohort contains twenty-four executed records: four tasks under each of six configurations. Candidates and treatment metadata in this cohort were authored to exercise evaluator outcomes. Table 7.2 reports their actual executions. It measures the qualification behavior of those supplied candidates, rather than the probability that a model will generate a correct repair.

[[TABLE:7.2|Executed authored-candidate qualification outcomes|Condition|Public passes per evaluated|Hidden passes per evaluated|Terminal outcomes]]
B1|Not evaluated|Not evaluated|4 syntax errors
B2|4/4|0/4|4 plausible but incorrect
B3|4/4|0/4|4 plausible but incorrect
B4|Not evaluated|Not evaluated|4 explicit abstentions
B5|4/4|0/4|4 plausible but incorrect
B6|4/4|4/4|4 passing candidates
[[ENDTABLE]]

Qualification wall-time means ± sample SD, in seconds, are B1 0.0198 ± 0.0072, B2 0.8102 ± 0.2346, B3 0.7410 ± 0.0551, B4 0.0087 ± 0.0012, B5 0.6552 ± 0.0629 and B6 0.6498 ± 0.0736. Each summary uses four authored candidates. These timings measure local qualification and exclude model inference.

The detection summaries report precision and recall of 4/4 in each condition. The supplied 95% Wilson bounds are 51.0%–100.0%. Every task exposes one affected request-builder location, so these values describe a narrow fixture population without a representative negative-location distribution. The live diagnostic has one task per configuration and corresponding Wilson bounds of 20.7%–100.0%; it cannot establish general localization accuracy.

Public and hidden results diverge for all twelve evaluated candidates in B2, B3 and B5. This verifies that the oracle rejects examples which ordinary tests accept. B6's four authored candidates pass both levels. Because candidate contents were selected by the fixture author, the contrast establishes evaluator discrimination rather than a causal treatment advantage.

<!-- PAGE -->
## 7.4 Invariant breakdown and failure mechanisms

Table 7.3 reports named assertions from the actual qualification traces. Money assertions apply to the two banking tasks and payment task. Beneficiary assertions apply to banking, transaction identity to payments, and parcel identity and exact weight to shipping. Idempotency-key preservation applies to all four tasks. Inapplicable assertions are excluded from their denominators.

[[TABLE:7.3|Preserved invariants in executed qualification candidates|Condition|Exact amount or weight|Beneficiary transaction or parcel identity|Original idempotency key]]
B2|0/4|4/4|4/4
B3|4/4|0/4|4/4
B5|4/4|4/4|0/4
B6|4/4|4/4|4/4
[[ENDTABLE]]

B2 illustrates a unit-preservation failure. The banking candidate divides the caller's minor-unit amount by one hundred while constructing the new nested body. Public checks accept the response shape, but the hidden exact-minor-unit assertion fails. The shipping candidate similarly loses exact weight. These executions demonstrate the inadequacy of shape-only validation for the supplied counterexamples.

B3 preserves numeric values but changes the intended identity. The two banking cases fail destination checks; the payment case fails original-transaction identity; shipping fails parcel identity. B5 preserves values and identities but changes the original idempotency key. In each case the omitted obligation is visible in the hidden assertion results, giving a specific explanation for the failed repair.

Key preservation is a request-level property. It does not establish exactly-once execution or end-to-end duplicate prevention in a stateful distributed provider. Those stronger properties require a provider-state oracle and fault scenarios beyond this request-builder interface. Currency assertions pass on all three applicable financial candidates in each of B2, B3, B5 and B6.

## 7.5 Live inference measurements and accounting

The live archive contains eighteen configuration-task traces across three diagnostic passes on TASK-BANK-014. Twelve successful provider responses account for 6,330 recorded prompt tokens and 2,436 completion/reasoning tokens. Preprocessing responses contribute to this total, so response count is not candidate count. Seven candidate diffs are retained across the eighteen traces. Provider failures remain in the original passes.

The third pass uses the standard SDK transport and produces a candidate diff in every configuration. Requested and returned versions are gemini-3.8-flash. Retained settings are temperature 0.1, top-p 0.95, seed 42, LOW reasoning and a 4,096-token output cap. Each condition has one observation in this pass; a between-run SD is therefore unavailable. Table 7.4 preserves the recorded token counts and rounded wall times.

[[TABLE:7.4|Observed third-pass live inference resources|Condition|Prompt tokens|Completion and reasoning tokens|Wall seconds]]
B1|365|1006|19.648
B2|435|46|34.469
B3|472|46|12.436
B4|1108|316|75.771
B5|1069|183|13.155
B6|1957|523|22.529
[[ENDTABLE]]

All six observations report zero cached tokens. Public and hidden exit codes are null, and independent correctness is unobserved. The six generated diffs are identical. No observed correctness gain can therefore be assigned to a configuration from this pass.

Table 7.5 reports the supplied API estimates. These use recorded usage and the package's dated rate card; they are monetary estimates rather than reconciled invoices. GPU energy, host electricity and amortized hardware expenditure were not measured. A cost per correct repair requires independently correct live repairs and is undefined for this cohort.

[[TABLE:7.5|Recorded API estimates for the third diagnostic pass|Condition|API estimate USD]]
B1|0.00404625
B2|0.00049875
B3|0.00052650
B4|0.00201600
B5|0.00148800
B6|0.00342900
[[ENDTABLE]]

The third pass totals 5,406 prompt tokens, 2,120 completion/reasoning tokens and USD 0.01200450 in estimated API charges. Total recorded wall time is 178.008 seconds. Those values describe six diagnostic observations, not per-task means for a 120-task study. Earlier transport outcomes cannot be assigned complete usage or invoice totals when responses were unavailable.

<!-- PAGE -->
## 7.6 Interpretation of the component ablations

B1 provides the source-and-contract reference. B2 adds public test information and bounded feedback, which can detect observable interface failures but can also admit an incorrect patch when tests omit business obligations. The qualification examples demonstrate this latter possibility through actual public-pass and hidden-fail outcomes. They do not estimate its prevalence among model-generated migrations.

B3 supplies structural context. Its intended benefit is selecting relevant operations and source rather than relying on unrestricted repository text. The request-builder fixture has one function and no graph edges in the recorded B6 live trace, leaving little opportunity to test repository localization. A larger corpus must vary call depth, shared schemas and irrelevant consumers before a structural-context effect can be estimated.

B4 adds inferred semantic groups. The third-pass B4 graph stage takes 68.127 seconds and generation takes 7.625 seconds. B6's corresponding stages take 7.772 and 6.092 seconds. This substantial variation in single observations cautions against interpreting a condition's one wall time as its typical overhead. All third-pass candidates have the same patch content, so the observations establish additional semantic-stage execution without demonstrating improved repair.

B5 adds inferred intent and generated checks. Its third-pass intent stage takes 6.590 seconds and generation takes 6.549 seconds. B6 records 8.652 seconds for intent inference. These stages supply inspectable assertions, but the checks require evaluation against independent business obligations. The authored B5 counterexamples pass their enabled development gates while losing the original idempotency key, illustrating why generated checks cannot define their own final ground truth.

B6 combines structural localization, semantic context and inferred checks. Its authored qualification candidates preserve all applicable assertions. Its live candidate remains unevaluated and matches the other five live diffs. The evidence therefore supports a functioning combination of stages and a discriminating evaluator, while the hypothesis of superior model-generated repair remains open.

A completed comparison should estimate paired B6–B2, B3–B2, B4–B3, B5–B3 and B6–B5 effects on common tasks. Resources must include preprocessing, failed requests and retries. Additional model calls introduce a computation confound, so matched-budget baselines are needed alongside practical pipeline comparisons. Repeated runs must remain nested within tasks and families when estimating uncertainty.

## 7.7 Threats to validity and completion requirements

Construct validity is limited by pure request construction. Hidden checks examine the returned request representation and preserved values; they do not exercise a remote provider's state, transactions or failure recovery. The deliberate fixture candidates also prevent qualification percentages from serving as model-performance estimates. Passing a generated check supplies weaker evidence than passing independently specified assertions.

Internal validity is limited by a single live task, sequential configurations and a transport change between passes. The third pass is a transport diagnostic, not a randomized independent replication. The provider identifier is retained, but immutable serving weights were not verified. These conditions preclude attribution of resource or correctness differences to an individual component.

External validity is constrained by four authored tasks and the absence of a completed schema-migration cohort. No open-weight execution is retained. Planned model hardware and published weight fingerprints do not establish an executed replication. Full repository migrations, dynamic wrappers and naturally occurring changes require additional task assets and measurements.

Completion requires the expanded executable corpus, independently reviewed oracles, evaluated model-generated patches under every configuration, repeated trials and failure-inclusive aggregation. The main comparative effect, invariant distributions, resource SDs and cost per correct repair remain [PENDING EVALUATED LIVE BENCHMARK]. Existing diagnostics and qualification records provide an auditable starting point for that study without implying a result that has not been measured.

<!-- PAGE -->
# CHAPTER 8
# CONCLUSION AND FUTURE WORK
## 8.1 Conclusions

APIShield implements a local workflow for identifying supported Python consumers of documented API changes and preparing tested migration proposals. Its core connects captured source, paired OpenAPI descriptions, scoped requirements, inferred checks and validation evidence. The browser and CLI use the same engine, and successful proposals remain reviewable patches rather than automatically deployed changes.

The recorded engineering evidence shows correct endpoint, request/response nesting, refund and exact-integer repairs in selected synthetic cases. A reviewed missing-address diagnostic demonstrates an appropriate outcome when a migration requires unavailable data. A controlled two-file draft exercise demonstrates publication of a complete retained proposal with duplicate-request handling. Provider outages, malformed output and incomplete analysis remain material limits.

The academic contribution is an inspectable integration of graph context, preservation constraints and validated API migration. Current browser repairs infer additional checks, while confirmed requirements retain separate provenance. The benchmark harness executes six treatment configurations and separates hidden evaluation from development feedback. Four authored tasks establish evaluator discrimination; eighteen live traces establish inference and resource observations. They do not establish causal superiority on a representative migration population.

The literature review identifies relevant precedent in contract comparison, agentic repair, intent inference and repository graphs. It supports the problem's relevance while ruling out broad claims that those component ideas are new. A distinct integration and a rigorous evaluation are the appropriate basis for developing the contribution.

The project has achieved a usable local prototype and a reproducible route toward comparative evaluation. It has not completed comprehensive field-flow analysis, per-project execution environments, a representative evaluated model benchmark or hosted customer operation. Those boundaries define the next work and keep the conclusions proportionate to the evidence.

<!-- PAGE -->
## 8.2 Future work and completion priorities

The publication package supplies ACM TOSEM and IEEE TSE review profiles; the submission venue remains [SELECTED JOURNAL]. Completing the comparative evidence requires a frozen case collection, faithful baselines, independent checks and transparent failure accounting. Results should establish whether the proposed mechanisms improve behavioral acceptance at a useful cost. The final novelty statement also needs a broader prior-art review.

The next engineering priority is deeper supported analysis. Traceable request/response field observations and conservative helper resolution would make impact reports more specific. Coverage must remain explicit; greater graph size alone does not establish better localization. Per-integration external test environments would also reduce setup friction and separate project dependencies from the application interpreter.

[[TABLE:8.1|Future work and evidence required for completion|Priority|Work item|Completion evidence]]
1|Controlled baseline experiment|Frozen protocol, raw outcomes and independent checks
2|Field and helper analysis|Annotated cases and supported-coverage metrics
3|Per-integration environment setup|Independent dependencies, visible setup and recovery
4|Fresh UI acceptance|Current desktop/mobile captures and interaction review
5|Hosted pilot architecture|Tenant controls, isolated workers and restart recovery
6|Unfamiliar integration validation|Maintainer-reviewed migration and recorded limitations
[[ENDTABLE]]

<!-- PAGE -->
# REFERENCES
[[REFERENCES:1]]
<!-- PAGE -->
[[REFERENCES:2]]
<!-- PAGE -->
[[REFERENCES:3]]
<!-- PAGE -->
[[REFERENCES:4]]

<!-- PAGE -->
# APPENDIX 1
# INTEGRATION CONFIGURATION AND RULE SCHEMA

The following abbreviated configuration illustrates the version-one input structure. It is a report example, not evidence that another repository was executed. Paths resolve relative to the configuration file. The source repository must already contain a committed revision suitable for analysis.

[[CODE]]
{
  "version": 1,
  "repository": "C:/projects/shipping-client",
  "ref": "HEAD",
  "code_paths": ["src"],
  "base_spec": "base.json",
  "target_spec": "target.json",
  "test_commands": [["python", "-m", "pytest", "tests", "-q"]],
  "requirements": [{
    "id": "shipping-identity-weight",
    "description": "Preserve package ID and integer gram weight.",
    "scope": {"file": "src/parcel.py", "function": "create_label"},
    "origin": "developer",
    "confirmed": true,
    "checks": ["tests/test_parcel.py::test_identity_and_weight"]
  }]
}
[[ENDCODE]]

Browser onboarding constructs a controlled pytest command rather than accepting arbitrary command text. CLI/server configuration can express explicit argument arrays. Controller credentials do not belong in the integration environment map.

Use a real committed test selector; confirmation does not bypass collection. Changed source or test context requires renewed review. For reproduction, use the selectors supplied with the actual shipping fixture.

<!-- PAGE -->
# APPENDIX 2
# REPAIR AND VALIDATION PSEUDOCODE

The pseudocode summarizes the guarded transaction. Error handling, ownership locks and persistence are simplified for readability; the implementation contains the complete control flow.

[[CODE]]
capture configuration, contracts and committed source
scan calls, compare contracts and localize impact
resolve confirmed requirements and available checks
if scope or checks are unresolved: return NEEDS_INPUT
for each permitted attempt:
    recreate committed workspace
    run setup and discover selected tests
    obtain candidate or missing-information diagnostic
    if diagnostic: retain it and return NEEDS_INPUT
    validate exact, permitted, nonoverlapping edits
    parse Python and inventory edited bytes
    run configured validation and separate rule checks
    verify protected files and contracts are unchanged
    if all required checks pass:
        retain patch from checked bytes
        return VALIDATED
    retain failure and public retry feedback
return FAILED after budget exhaustion
finally remove disposable source workspace
[[ENDCODE]]

Independent research verification is outside this acceptance loop. Its hidden tests do not enter the feedback context. That separation is essential for measuring whether the engine's accepted patches preserve behavior beyond the tests available during generation.

<!-- PAGE -->
# APPENDIX 3
# EVIDENCE INDEX AND HISTORICAL PROVENANCE

The evidence index identifies repository records used in Chapter 6. The report preserves their dates and limitations; it does not assert that every external temporary artifact is still available on another computer.

[[TABLE:A3.1|Project records used for the evaluation chapter|Record|Relevant content]]
docs/live-ai-quality-2026-10-12.md|Initial jobs, outages and strengthened held-out audit
docs/cloud-ai-validation.md|Six-case Cloud acceptance and reviewed diagnostic
docs/live-ai-guided-workspace-validation.md|Browser shipping and exact-money follow-up
docs/github-drafts-validation.md|Complete two-file remote draft and duplicate behavior
docs/community-semantic-workspace.md|Graph/layout source checks and pending visual recapture
benchmarks/REVIEW_STATUS.md|Executed qualification and live inference scope
benchmarks/analysis/live_diagnostic_review/metrics.json|18 live traces and missing correctness outcomes
docs/current-api-ai-repair-walkthrough.md|Working source, inferred checks and reviewed Apply
[[ENDTABLE]]

Historical job identifiers are shipping repair 525ad09376bf47fc8f02215236416a54, money repair 34f75d73b7e84bc59d407da8cafeb9b3 and draft repair d2d449eceb534b15bac879a1656d10e3. These refer to historical inputs, not current validation. Confirm artifact availability and remove private machine paths before public submission.

<!-- PAGE -->
# APPENDIX 4
# EXPERIMENT RECORD AND RESULT ENTRY FORM

Each measured case-run should have one structured record. The fields below provide the minimum information needed to distinguish a failed model call, an invalid candidate and an independently incorrect accepted patch. The form distinguishes available diagnostic records from measurements still needed for a full evaluated model benchmark.

[[TABLE:A4.1|Minimum controlled-experiment record|Field|Value to record]]
Case and condition|[CASE ID] and [B1 TO B6]
Source and harness|[COMMIT AND CONTENT HASHES]
Contracts|[BASE AND UPDATED HASHES]
Model and settings|[REQUESTED AND RETURNED MODEL VERSION, RUN DATES AND GENERATION CONFIG]
Research treatment adapter|benchmarks/harness/run_ablation.py and configurations.json; retained source hashes
Task and oracle assets|Four complete tasks under benchmarks/tasks and evaluator_private; expanded corpus pending
Execution environment|[OS, RUNTIME AND HARDWARE; WEIGHTS AND QUANTIZATION IF LOCAL]
Attempt budget|[LIMITS AND ACTUAL REQUEST COUNT]
Engine outcome|[STATUS AND ERROR CATEGORY]
Independent oracle|[PASSED / FAILED / NOT REACHED]
Diagnostic review|[ADEQUATE / INADEQUATE / NOT APPLICABLE]
Usage and duration|[OBSERVATIONS WITH MISSINGNESS]
Evidence links|[RUN ID, TIMESTAMP, MODEL REQUEST AND RESPONSE, PATCH AND TEST LOGS]
[[ENDTABLE]]

A result entry should retain both raw counts and the denominator used by its metric. Failed provider requests must not disappear from a completion-rate calculation. An unobserved token count remains missing rather than zero.

The versioned local package, publication/apishield-evaluation-v1.0, adds a typed experiment-record schema, portable headless runner, analysis scripts and content manifests. Its 641 listed payload files matched their recorded SHA-256 values during this review. Retained extraction records report byte-for-byte analysis reproduction and one passing authored B6 fixture outside Git. These establish local package reproducibility; they add no evaluated model-generated repairs or public archive deposit.

Recorded evidence is under benchmarks/runs and benchmarks/analysis; the complete evaluated model corpus is [FULL STUDY ARCHIVE]. It should map each case, configuration and repetition to its candidate patch, public-test output and independent-oracle output, including unsuccessful runs. The analysis entry point is benchmarks/harness/aggregate_metrics.py; the final study command is [FULL STUDY ANALYSIS COMMAND]. Any reported monetary cost needs [DATED PRICE SOURCE OR MEASURED HARDWARE BILLING] alongside observed usage; assumed prices cannot establish an actual expenditure.

When multiple reviewers assess a diagnostic, retain their independent judgments before a final adjudication. When an oracle is corrected, record the change and rerun affected saved patches offline where possible. Do not silently combine results before and after the change as though they came from one frozen protocol.

<!-- PAGE -->
# APPENDIX 5
# TRACEABILITY AND REPORT COMPLETION CHECKLIST

This appendix links major report claims to the evidence needed before final submission. It supports later revision when the implementation changes. A planned item should be marked complete only after its named evidence exists.

[[TABLE:A5.1|Claim traceability and completion requirements|Claim or section|Evidence to maintain|Current status]]
Architecture description|Current module interfaces and source inspection|Described for present local system
Selected repair behavior|Dated run, patch and independent checks|Historical synthetic evidence
Requirement acceptance|Rule snapshot, collection and JUnit outcome|Implemented and demonstrated in fixture
Draft publication|Complete patch, preview and remote record|Historical controlled exercise
Comparative improvement|Evaluated model repairs under matched conditions|Pending full model benchmark
Current frontend appearance|Fresh captures and interaction checks|Pending visual recapture
Academic novelty statement|Verified literature and broader prior-art search|Qualified mechanism-level argument
Personal certification|Candidate/guide entries and real signatures|TO BE COMPLETED MANUALLY
[[ENDTABLE]]

Before submission, replace personal placeholders, select the correct degree wording and submission date, and confirm whether an external-guide certificate is required. Signatures and institutional seals must be supplied through the actual approval process.

Numerical claims require a source revision, dataset and denominator. Keep an unmeasured objective explicit until evidence supports its conclusion.

<!-- PAGE -->
# APPENDIX 6
# SELECTED INTERFACES AND REPRODUCTION NOTES

The local CLI exposes scan, compare, repair, report and cancel operations, plus proposal preparation and publication. The commands below illustrate the interface. They were not executed during report preparation.

[[CODE]]
apishield scan --config integration.json
apishield compare --config integration.json
apishield repair --config integration.json --candidate candidate.json
apishield report JOB_ID
apishield cancel JOB_ID
[[ENDCODE]]

[[TABLE:A6.1|Representative local API interfaces|Interface|Purpose]]
GET /api/workspace|Read browser integrations and setup state
POST /api/jobs|Queue a configured operation
GET /api/jobs/{job_id}|Read retained result
POST /api/jobs/{job_id}/cancel|Request cancellation
GET /api/jobs/{job_id}/patch|Read a validated retained patch
POST /api/integrations/{name}/proposals|Prepare full draft preview
POST /api/proposals/{identity}/publish|Explicit draft publication
[[ENDTABLE]]

The browser app uses loopback port 8002. Reproduction requires the recorded revision, contract hashes and configuration, with dependencies available to the application interpreter. Retain independent verification artifacts when updating results.
