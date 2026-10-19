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
