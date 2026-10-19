"""Build the reference paper solely from explicitly synthetic records."""
import csv
import json
import statistics as st
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/academic-synthetic-reference'
S=json.loads((OUT/'synthetic_summary.json').read_text(encoding='utf-8'))
R=list(csv.DictReader((OUT/'synthetic_runs.csv').open(encoding='utf-8')))
T=list(csv.DictReader((OUT/'synthetic_tasks.csv').open(encoding='utf-8')))
M=[f'B{i}' for i in range(1,7)]
def percent(x):return f'{100*x:.1f}'
def score(x):return f'{percent(x["value"])} ± {percent(x["sd_repetitions"])} [{percent(x["ci95"][0])}, {percent(x["ci95"][1])}]'
def interval(x):return f'{100*x["value"]:+.1f} ± {100*x["sd_repetitions"]:.1f} [{100*x["ci95"][0]:+.1f}, {100*x["ci95"][1]:+.1f}]'
def table(head,rows):return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join(['---']*len(head))+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows])
parts=[]
def add(text):parts.append(text.strip())
g=S['G-SIM'];o=S['OW-SIM'];delta=S['paired']['G-SIM:B6-B2']
add(f'''# APIShield: Graph-Assisted, Intent-Aware REST API Migration Repair—A Synthetic Reference Study

**Complete reference manuscript • 14 October 2026 • All benchmark outcomes are simulated**

This manuscript is an assumption-driven methodological template. No model inference, repository repair, hidden-test execution, human annotation or GPU measurement generated the reported data. G-SIM and OW-SIM denote fixed simulated backends, not verified provider snapshots or executed checkpoints. Every result table is synthetic; confidence intervals characterize the constructed dataset, not actual APIShield effectiveness. The text is structurally ready for scholarly development but must not be submitted as an empirical report of executed experiments.

## Abstract

Documented REST API evolution can render client applications incompatible while apparently successful repairs alter financial or identity semantics. We formulate the evaluation of APIShield, a migration-repair architecture combining contract-change analysis, structural localization, semantic relationships and inferred behavioural checks. To validate the completeness of an experimental and reporting design before deploying inference resources, we construct an explicitly synthetic benchmark with 120 controlled tasks in four domains and five repetitions across six configurations. The primary simulated backend comprises 3,600 task-runs; a 48-task open-weight-class replication adds 1,440. In the synthetic primary cohort, the full configuration delivers {g['B6']['correct']}/400 independently correct repairs ({percent(g['B6']['hidden']['value'])}%), compared with {g['B2']['correct']}/400 ({percent(g['B2']['hidden']['value'])}%) for code, documentation and unit-test feedback. The paired difference is {interval(delta)} percentage points under hierarchical bootstrap resampling. Ordinary visible-test passing remains an imperfect proxy: the test-feedback baseline passes {percent(g['B2']['visible']['value'])}% of repairable runs while {g['B2']['wrong_accepted']}/{g['B2']['accepted_count']} accepted patches violate modeled hidden invariants. Structural localization yields a clearer incremental benefit than semantic grouping alone. Behavioural gates substantially reduce accepted incorrect repairs but reject some modeled correct candidates and increase resource consumption. Under hypothetical pricing, full-system cost per delivered correct repair is ${g['B6']['cost_success']:.4f}, versus ${g['B2']['cost_success']:.4f} for the test-feedback baseline. These constructed outcomes demonstrate analytical consistency and plausible tradeoffs; they provide no evidence of measured superiority. We specify the independent-oracle, ablation, versioning and resource-accounting requirements for the subsequent empirical study.

**Index terms:** REST API evolution; automated program repair; semantic graphs; behavioural invariants; large language models; ablation studies; reproducibility; simulation.''')
add('''## 1. Introduction

API migration is a compatibility and behaviour-preservation problem. A client can adopt a new endpoint and payload shape while sending a charge in dollars rather than cents, issuing a duplicate transfer, or referring to the wrong refund transaction. Compilation and ordinary unit tests may not expose these mistakes. A useful migration system therefore requires evidence that its output conforms to the new contract and preserves application-level properties that remain valid under that contract.

APIShield is a local integration-maintenance application. It captures current code and accepted/observed API documents, identifies changes, displays an impact graph, proposes model-generated repairs and retains validation evidence. A user reviews a proposal before applying changes to working files. The present research question is whether contract-change analysis, structural and semantic graph context, and inferred behavioural checks improve correct migration outcomes relative to supplying an LLM with code, API documents and ordinary test feedback.

The methodological challenge is separating component value from stronger models, larger prompts, additional generations and benchmark-specific knowledge. Generated tests can agree with an incorrect generated patch. Semantically meaningful diagrams may not improve repair quality. Refusing to patch an ambiguous integration can be the right outcome, whereas indiscriminate refusal makes a system unusable. Correctness, abstention, false alerts and resource costs must consequently be evaluated together.

This article develops a complete reference evaluation through assumption-driven simulation. Its purpose is to expose denominator inconsistencies, treatment confounds, false acceptance, correlated repetitions and hidden cost omissions before an expensive empirical deployment. The simulation does not discover that APIShield improves repair quality: differences are produced by explicitly chosen probability and cost assumptions. It demonstrates how a completed manuscript should report outcomes, including unfavourable ablations and incomplete preservation.

The reference study contributes (i) a precisely scoped migration task and evidence architecture; (ii) a stratified controlled-task design separating repairable, unchanged and underspecified situations; (iii) six comparison configurations and an independent hidden-oracle boundary; and (iv) an auditable synthetic dataset, bootstrap summaries and cost model. Empirical superiority, usefulness to professional developers and generalization to naturally occurring migrations remain questions for subsequent executed research.

We ask RQ1: how accurately are affected calls localized? RQ2: how often do accepted repairs satisfy independent behavioural oracles? RQ3: which graph and check components contribute? RQ4: what latency, token and monetary overhead accompanies improved correctness? RQ5: does the pattern persist in a second backend and on negative or underspecified tasks? The paper reports all five questions within its synthetic scope.''')
add('''## 2. Background and Related Work

Specification-based repair and graph-assisted API reasoning already have precedents. dcFix detects REST API misuse, localizes non-conforming code and supplies relevant specification/code fragments to an LLM [1]. It is particularly relevant to localization baselines, although specification misuse and versioned client migration are not identical populations. ASAP-Repair uses API usage graphs and usage templates to address API misuse [2], establishing that API repair with graph representations is not itself a novel premise. APIPilot studies execution-validated, LLM-inferred dependencies for REST API testing [3]. It motivates treating inferred relationships as hypotheses rather than facts, but it is not an interchangeable migration-repair competitor.

APIShield's candidate contribution concerns the conjunction of versioned change localization, inferred preservation requirements, executable repair gating and independent evaluation of application behaviour. Whether this conjunction improves outcomes must be assessed against strong localization/test-feedback alternatives. The present B1–B6 comparisons are internal treatments, not implementations or measured comparisons with the cited systems. External-tool comparisons require compatible datasets, released implementations or clearly labelled reproductions.

Empirical software engineering standards emphasize matching methods to claims, disclosing limitations and enabling reproducibility [4]. We adopt those principles by distinguishing simulated observations from measured outcomes, preserving raw task-level data, retaining unsuccessful cases and using case/family-aware uncertainty analysis. Inference-model randomness, correlated project structures and test overfitting are treated as evaluation-design concerns rather than eliminated through nominally deterministic sampling.''')
add('''## 3. System Architecture

### 3.1 Inputs and immutable capture

A migration task is a tuple (C, D0, D1, V, P), where C is an application snapshot, D0 the accepted API contract, D1 newly observed documentation, V the visible repository tests, and P the policy specifying admissible edits and preserved behaviour. APIShield retains source/document hashes and an inventory of excluded files. Checking for changes does not silently advance the accepted contract. Historical evidence remains associated with the captured inputs even when working code changes.

The primary scope is Python clients using supported direct requests/httpx GET/POST operations and JSON OpenAPI documents. Structural navigation may include bounded JavaScript relationships, but the study does not claim arbitrary JavaScript repair or complete dynamic analysis. Wrappers, computed URLs, external contract references and unsupported methods must remain unresolved or out of scope rather than appearing fully analyzed.

### 3.2 Contract changes and the structural graph

Contract differencing identifies changed operations and relevant request/response definitions. Static analysis links those operations to consuming calls and supported function relationships. Nodes distinguish endpoints, functions, files, tests and intent annotations. Structural edges derive from recorded code relationships. The resulting graph localizes model context and explains affected consumers. Source/type resolution and unresolved-edge provenance matter more to the research method than visualization geometry.

The current project uses bounded graph interpretation and model context. The reference design assumes a 120-node semantic interpretation ceiling and a 128-KiB serialized context limit. Input selection and truncation must be logged. A visually complete diagram does not establish complete repository coverage.

### 3.3 Semantic relationships and behavioural intent

An optional model stage proposes semantic groups and relationships. Those annotations remain labelled inferred; they do not override structural evidence. Another stage infers constraints from available source, documentation and tests, and generates executable behavioural checks in a protected namespace. For example, a transfer constraint can preserve source, destination, currency and an exact integer amount while accepting an API-specific change in nesting.

Inference cannot establish unknowable business truth. If the new contract requires an address that neither the caller nor another authorized source supplies, an actionable clarification is preferable to a fabricated value. Where old code and new documentation legitimately disagree, the task policy states which behaviour changes and which remains invariant.

### 3.4 Repair, acceptance and independent evaluation

The repair stage receives only authorized task inputs and treatment-specific context. Existing tests cannot be edited to make a candidate appear valid. Generated checks must collect and execute successfully; an import error, skip-only outcome or trivial assertion supplies no preservation evidence. Retries are bounded and their feedback is visible-test feedback only.

Every treatment is evaluated by the same hidden oracle H, outside model-accessible inputs. In B5/B6, generated system checks are additional acceptance gates; they are not the independent ground truth. Hidden oracles never appear in prompts, generated tests, retrieval or retry messages. An accepted repair is independently correct only when H verifies contract conformance, relevant preserved behaviour and absence of unintended effects.

User-reviewed Apply checks source/document freshness, retains recoverable original bytes and writes working files without automatically committing. A subsequent current graph should refer to repaired code, while historical reports retain prior impact evidence. This workflow is an engineering acceptance concern distinct from algorithmic superiority.

### 3.5 Implementation boundary

The existing product implements capture, graph visualization/interpretation, inferred intent/checks, bounded repair and review/Apply. B1–B6 are research configurations requiring a treatment adapter. In particular, semantic overlay artifacts must be explicitly connected to the candidate-generation context for B4/B6: their presence in the UI does not demonstrate that repair prompts consume them. This reference manuscript models that intended integration; it does not claim all ablation switches are already installed or executed.''')
add('''## 4. Benchmark and Empirical Design

### 4.1 Controlled benchmark composition

The simulation defines 120 controlled held-out task descriptors spanning four domains and 12 synthetic project families. Eighty tasks require repair, 25 are unchanged/irrelevant and 15 lack sufficient information for a justified repair. Family IDs identify structural clusters, not actual open-source repositories. “Held-out” describes the proposed experimental role of the cases; no trained model was queried against them.

The cross-backend subset contains 48 tasks: 32 repairable, 10 negative and six underspecified. It is selected once by stratified seeded sampling before outcomes are constructed. The primary configuration matrix comprises 120 × 6 × 5 = 3,600 task-runs; all-six-configuration replication comprises 48 × 6 × 5 = 1,440 additional task-runs. The combined total is 5,040, not 3,600 across both backends.

**Table 1. Synthetic benchmark composition; descriptors only, no executed repositories.**''')
rows=[]
for domain in sorted({t['domain'] for t in T}):
    a=[t for t in T if t['domain']==domain];b=[t for t in a if t['replication_subset']=='True']
    rows.append([domain,len(a),sum(t['task_class']=='repairable' for t in a),sum(t['task_class']=='negative' for t in a),sum(t['task_class']=='underspecified' for t in a),len(b)])
rows.append(['Total',120,80,25,15,48]);add(table(['Domain','Tasks','Repairable','Negative','Underspecified','Replication tasks'],rows))
add('''Repair scenarios represent route relocation, request/response re-nesting, exact monetary units, refund identity, duplicate-transaction prevention, shared schemas and transitive consumers. Negative cases include identical contracts, compatible unused additions and changes to unconsumed endpoints. Underspecified cases require missing address/currency information or contain unresolved semantic contradictions.

Financial preservation is evaluated on 20 modeled banking tasks; duplicate prevention on 10 of them; parameter re-nesting on 20 shipping/shared-schema tasks. Thus their primary-cohort denominators are 100, 50 and 100 repeated runs per treatment. These are overlapping diagnostic strata, not additional tasks. Unsupported pagination, SDK wrappers, arbitrary method changes and long dynamic traces would require a separately declared challenge set.

### 4.2 Treatments and oracle parity

**Table 2. Reference configurations. Hidden evaluator checks are identical and inaccessible to all six.**''')
add(table(['ID','Authorized model/system inputs','Acceptance gate'],[
 ['B1','Code and old/new API documents','Protected existing tests scored after generation'],
 ['B2','B1 plus existing unit tests and bounded test feedback','Existing tests'],
 ['B3','B2 plus structural graph/localization','Existing tests'],
 ['B4','B3 plus AI semantic groups/relationships','Existing tests'],
 ['B5','B3 plus inferred intent and generated invariant checks','Existing + generated checks'],
 ['B6','B3 plus semantic relationships, inferred intent and generated checks','Existing + generated checks']]))
add('''B1 is a no-feedback candidate baseline rather than a deliberately weak implementation with inaccessible necessary code. B2–B6 use the same visible-test feedback policy and editable paths. The full system's inferred checks remain fallible and distinct from independent hidden evaluation. Consequently B6 has no privileged evaluator information.

The simulated practical-cost condition includes treatment-specific stage overheads. It is not a token-budget-matched causal comparison: higher-cost variants receive additional computation. A subsequent empirical study must add budget-matched baselines that can spend comparable resources on useful candidate iterations or retrieval. Both practical and budget-matched results should be reported.

### 4.3 Backend and resource assumptions

**Table 3. Synthetic backend assumptions; these are not actual model identities, pinned checkpoints or vendor prices.**''')
add(table(['Setting','G-SIM','OW-SIM'],[
 ['Intended empirical analogue','Gemini 3.8 Flash-class API','70B open-weight instruction/code model'],
 ['Identity used by simulation','G-SIM fixed probability model','OW-SIM fixed probability model'],
 ['Real checkpoint/snapshot executed','None','None'],
 ['Repetitions per task/treatment','5','5'],
 ['Modeled repair retry ceiling','2 retries; up to 3 repair requests','2 retries; up to 3 repair requests'],
 ['Optional preprocessing calls','Up to one semantic + one intent/check call','Same stage structure'],
 ['Modeled total deadline','600 s','600 s'],
 ['Prompt-token rate assumption','$0.50 per million','No per-token monetary charge'],
 ['Completion-token rate assumption','$3.00 per million, including modeled reasoning','$0; runtime accounted separately'],
 ['Accelerator-service assumption','Included in hypothetical API rate','$2.50/service-hour; 82% modeled GPU-active allocation'],
 ['Controller CPU assumption','$0.10/active CPU-hour','$0.10/active CPU-hour']]))
add('''The real primary experiment should use a provider-supported fixed snapshot where available, recording requested and returned versions, API/SDK and run dates. An open-weight replication should pin weight/tokenizer hashes, chat template, licence, runtime, quantization and hardware. No actual Gemini or Llama/DeepSeek performance or hardware requirement is inferred from the two simulated backends. A complete model identity cannot be replaced by an anonymous claim that “an LLM” performed the repair.

### 4.4 Simulation mechanism and provenance

The generator uses seed 20261014. Domain and family labels, task classes and the replication subset precede outcome generation. Repairable cases receive a shared case difficulty in [−0.14, 0.14], domain adjustments and correlated run-level uniforms. Treatment-specific probability assumptions for G-SIM are 0.55, 0.64, 0.71, 0.735, 0.80 and 0.825; corresponding OW-SIM assumptions are 0.43, 0.52, 0.595, 0.62, 0.69 and 0.72. These are generator inputs, not observed success rates or estimates calibrated from the existing six-case pilot.

Actual synthetic delivery depends additionally on operational failure, malformed output, ordinary-test passing and generated-check gates. Financial/multi-endpoint domain penalties, shared random variables and treatment noise introduce dependence and non-monotonic realizations. Generated checks can reject correct candidates. A provider/runtime failure cannot also be a correct delivered repair. Each task-run receives one exclusive outcome.

Precision/recall are generated from per-task affected-call counts, sampled true detections and spurious detections. Token totals and latency use treatment-specific resource levels, lognormal workload variation and retries. Correct negative cases in graph-localized treatments can terminate without model generation, preserving the distinction between task-runs and content calls. Runs exceeding the modeled deadline become budget-exhausted failures.

This model incorporates plausible qualitative tradeoffs, not forecasts. Favorable full-system probability assumptions are deliberately visible. Matching a completed manuscript's accounting and analytical structure does not validate those assumptions against real applications.

### 4.5 Metrics, uncertainty and cost definitions

Correct repair rate divides accepted, hidden-correct outcomes by all repairable runs, including operational failures. Visible pass rate divides ordinary-test passing by the same denominator. Acceptance precision divides hidden-correct accepted outcomes by all accepted outcomes. A rejected correct candidate is not a delivered success. Negative specificity excludes unnecessary edits; operational failures remain unsuccessful negatives. Correct abstention requires an actionable modeled diagnostic, not silence or a provider error.

Table percentages report mean ± sample standard deviation of the five repetition-level rates, followed by a 95% hierarchical bootstrap interval. Bootstrap resampling draws synthetic families and then cases within family, retaining all five repetitions together, with 1,200 draws. Detection ratios are micro-aggregated over call labels; bootstrap retains the underlying case clusters. Diagnostic preservation strata use the same procedure. Costs and wall-clock variability use task-run SD; latency and cost-success intervals use family/case bootstrap.

Cost per successful repair sums all modeled costs for a treatment's complete cohort, including negative/underspecified tasks, unsuccessful attempts and preprocessing, then divides by independently correct delivered repairs. Hosted cost includes prompt/completion charges and modeled active controller CPU. Open-weight cost uses allocated accelerator-service time and controller CPU. Network, storage, idle reservation, energy and acquisition/amortization costs are excluded; the estimate is therefore an explicit execution-cost scenario, not total ownership cost or an invoice. No statistical significance test is interpreted as evidence about real systems.''')
add('''## 5. Synthetic Results and Evaluation

### 5.1 Detection and localization

**Table 4. Synthetic G-SIM affected-call detection (%); mean ± repetition SD [95% hierarchical bootstrap CI], all 120 tasks.**''')
add(table(['Configuration','Precision','Recall'],[[m,score(g[m]['precision']),score(g[m]['recall'])] for m in M]))
add(f'''Structural localization raises modeled precision from {percent(g['B2']['precision']['value'])}% in B2 to {percent(g['B3']['precision']['value'])}% in B3. The semantic-only addition B4 has slightly lower precision than B3 despite comparable recall, illustrating that plausible inferred relationships can introduce spurious associations. B6 reaches {percent(g['B6']['precision']['value'])}% precision and {percent(g['B6']['recall']['value'])}% recall, leaving substantial missed and false links. These values follow the assumed detector distributions; they do not establish whole-repository coverage.''')
add('''### 5.2 Visible testing versus independent correctness

**Table 5. Synthetic G-SIM repair outcomes; each row has 400 repairable runs. Percentages use repetition SD and hierarchical CIs.**''')
add(table(['Config.','Visible pass % ± SD [CI]','Delivered hidden-correct % ± SD [CI]','Correct/400','Accepted incorrect/accepted'],
 [[m,score(g[m]['visible']),score(g[m]['hidden']),f'{g[m]["correct"]}/400',f'{g[m]["wrong_accepted"]}/{g[m]["accepted_count"]} ({100*g[m]["wrong_accepted"]/g[m]["accepted_count"]:.1f}%)'] for m in M]))
add(f'''The baseline with ordinary test feedback exhibits a {100*(g['B2']['visible']['value']-g['B2']['hidden']['value']):.1f}-percentage-point visible/hidden gap. Its {g['B2']['wrong_accepted']} accepted incorrect patches demonstrate the modeled risk of accepting API-conforming but behaviour-changing repairs. B6 narrows the gap to {100*(g['B6']['visible']['value']-g['B6']['hidden']['value']):.1f} points and leaves {g['B6']['wrong_accepted']} incorrect accepted outputs. The gap is not itself the incorrect-acceptance rate: in B5/B6 it also includes ordinary-test-passing candidates rejected by generated checks, including some correct candidates.

Full-system delivery improves by {interval(delta)} points relative to B2 in this constructed cohort. Because outcomes were sampled under treatment-specific assumptions, the interval describes simulation variability; its exclusion of zero is not evidence that an executed APIShield study would show a benefit.''')
add('''### 5.3 Financial and semantic preservation

**Table 6. Synthetic G-SIM end-to-end preservation in overlapping strata (% ± repetition SD [95% CI]); failures and rejected candidates count as unsuccessful.**''')
add(table(['Config.','Exact money (100 runs)','Duplicate prevention (50 runs)','Parameter re-nesting (100 runs)'],[[m]+[score(g[m][key]['stats']) for key in ['financial','duplicate','nesting']] for m in M]))
add('''Exact monetary preservation requires identity, currency and documented units to remain consistent; it does not mandate retaining an obsolete wire representation. Duplicate prevention concerns one logical state transition rather than merely a syntactically correct idempotency field. Parameter re-nesting checks that values are moved into new structures without swapping or inventing them. Independent cases can satisfy one diagnostic property while failing another, so diagnostic rates need not equal whole-repair correctness.

The modeled failure profile includes subtle errors: integer amounts converted through floating-point intermediates, repeated requests after an ambiguous response, and structurally valid payloads containing incorrect identifiers. These examples describe fault classes represented by the simulator, not inspected actual generated patches. A real study must connect every classification to preserved execution traces and reviewed evidence.''')
add('''### 5.4 End-to-end resource consumption

**Table 7. Synthetic G-SIM resource accounting, 600 total task-runs/configuration. Token totals include all stages/attempts per task-run, including early-exit zeros. SD is across task-runs; monetary rates are hypothetical.**''')
rows=[]
for m in M:
    r=g[m]
    rows.append([m,f'{r["prompt_tokens"]["mean"]:.0f} ± {r["prompt_tokens"]["sd"]:.0f}',f'{r["completion_tokens"]["mean"]:.0f} ± {r["completion_tokens"]["sd"]:.0f}',f'{r["retries"]["mean"]:.2f} ± {r["retries"]["sd"]:.2f}',f'{r["latency_s"]["mean"]:.1f} ± {r["latency_s"]["sd"]:.1f} [{r["latency_ci95"][0]:.1f}, {r["latency_ci95"][1]:.1f}]',f'${r["cost_success"]:.4f} [${r["cost_success_ci95"][0]:.4f}, ${r["cost_success_ci95"][1]:.4f}]',f'${r["total_cost"]:.2f}'])
add(table(['Config.','Prompt tokens mean ± SD','Completion tokens mean ± SD','Retries mean ± SD','Wall time s ± SD [CI]','$/correct repair [CI]','Cohort cost'],rows))
add(f'''B6 increases cost per delivered correct repair by {g['B6']['cost_success']/g['B2']['cost_success']:.2f}× and mean wall time by {g['B6']['latency_s']['mean']/g['B2']['latency_s']['mean']:.2f}× relative to B2. Structural localization B3 is a more favourable synthetic cost/quality point than semantic grouping B4, which adds overhead without a positive primary-cohort delivery delta. Preprocessing must not be omitted when comparing these variants. Open-weight inference removes per-token API billing but does not remove accelerator time or resource accounting.''')
add('''### 5.5 Failure distribution

**Table 8. Exclusive synthetic G-SIM outcome counts on repairable tasks; every row sums to 400.**''')
cats=['correct_repair','accepted_invariant_violation','visible_test_rejected','check_rejected','invalid_output','provider_failure','budget_exhausted']
add(table(['Config.','Correct','Accepted invariant violation','Visible rejection','Generated-check rejection','Malformed output','Provider failure','Budget exhausted','Total'],[[m]+[g[m]['failures'].get(c,0) for c in cats]+[400] for m in M]))
rejected={m:sum(x['model']=='G-SIM' and x['method']==m and x['task_class']=='repairable' and x['candidate_correct']=='1' and x['accepted']=='0' for x in R) for m in ['B5','B6']}
add(f'''Operational failures are retained rather than silently retried out of the denominator. Shared outage variables give matched treatments the same primary-cohort provider-failure count, while malformed outputs vary by stage structure. Generated-check rejections include {rejected['B5']} modeled correct B5 candidates and {rejected['B6']} modeled correct B6 candidates. This false-rejection cost is essential: protecting against bad patches cannot be credited without accounting for withheld good patches. The simulator does not provide actual failure logs or causal diagnoses.''')
add('''### 5.6 Unchanged and underspecified tasks

**Table 9. Synthetic G-SIM negative specificity and appropriate abstention (% ± repetition SD [95% CI]); denominators are 125 negative and 75 underspecified runs/configuration.**''')
rows=[]
for m in M:
    neg=[x for x in R if x['model']=='G-SIM' and x['method']==m and x['task_class']=='negative']
    rows.append([m,score(g[m]['no_change']),score(g[m]['abstention']),sum(x['false_edit']=='1' for x in neg)])
add(table(['Config.','Correct no-change % ± SD [CI]','Appropriate abstention % ± SD [CI]','Unnecessary edits/125'],rows))
add('''No-change and abstention outcomes cannot be folded into a single repair-success denominator. Correctly leaving an unchanged integration alone is useful, but should not inflate success on difficult migrations. Similarly, a provider error supplies no evidence that the system appropriately recognized missing business information. A future executed study must review whether diagnostics specify the missing input and avoid fabricated replacements.''')
add('''## 6. Ablation Study

### 6.1 Component effects in the primary cohort

**Table 10. Paired synthetic hidden-correct delivery differences, percentage points [95% hierarchical CI]; identical cases and repetitions are paired.**''')
add(table(['Contrast','Interpretation','G-SIM delta [CI]','OW-SIM delta [CI]'],[[a+' − '+b,label,interval(S['paired'][f'G-SIM:{a}-{b}']),interval(S['paired'][f'OW-SIM:{a}-{b}'])] for a,b,label in [('B3','B2','Structural localization'),('B4','B3','Semantic overlay alone'),('B5','B3','Inferred intent/checks'),('B6','B2','Full method versus test feedback'),('B6','B5','Overlay added to intent/checks')]]))
add('''The simulated structural effect is more robust than the semantic-only effect. B4 slightly underperforms B3 in the primary realization, and its interval spans both gains and losses. Adding inferred checks changes acceptance behaviour, not only generation probability. B6 versus B5 is a small primary-cohort difference with an interval spanning zero; the reference study consequently cannot claim a demonstrated synergy between semantic overlays and invariant checking.

These ablations provide examples of appropriately cautious reporting. A completed empirical manuscript should explain null or negative component results rather than omit them. Because simulation parameters encode a preference for stronger configurations, even a positive difference is not an independent test of the underlying scientific hypothesis.

### 6.2 Cross-backend replication

**Table 11. Synthetic matched-subset repair correctness. Both columns use the same 32 repairable tasks × five repetitions; main-cohort G-SIM percentages are not reused here.**''')
add(table(['Config.','Matched G-SIM % ± SD [CI]','OW-SIM % ± SD [CI]','OW-SIM correct/160'],[[m,score(S['matched_G'][m]),score(o[m]['hidden']),f'{o[m]["correct"]}/160'] for m in M]))
add('''The weaker simulated backend exhibits a non-monotonic B5 result: adding inferred checks does not automatically improve delivered correctness, despite reducing acceptance of incorrect candidates. More difficult inference, malformed outputs and conservative gates can offset benefits. B6 remains a stronger modeled delivery configuration, but the matched subset is small and its intervals are correspondingly broad. Actual cross-model generality cannot be inferred from two programmed distributions.

**Table 12. Synthetic OW-SIM resources, 240 total task-runs/configuration; no actual local model or hardware was benchmarked.**''')
rows=[]
for m in M:
    r=o[m];rows.append([m,f'{r["prompt_tokens"]["mean"]:.0f} ± {r["prompt_tokens"]["sd"]:.0f}',f'{r["completion_tokens"]["mean"]:.0f} ± {r["completion_tokens"]["sd"]:.0f}',f'{r["retries"]["mean"]:.2f} ± {r["retries"]["sd"]:.2f}',f'{r["latency_s"]["mean"]:.1f} ± {r["latency_s"]["sd"]:.1f} [{r["latency_ci95"][0]:.1f}, {r["latency_ci95"][1]:.1f}]',f'${r["cost_success"]:.4f} [${r["cost_success_ci95"][0]:.4f}, ${r["cost_success_ci95"][1]:.4f}]'])
add(table(['Config.','Prompt tokens ± SD','Completion tokens ± SD','Retries ± SD','Wall time s ± SD [CI]','$/correct repair [CI]'],rows))
add('''The open-weight cost scenario illustrates that local operation can be more expensive per delivered repair at assumed throughput and utilization, even without proprietary per-token billing. It does not establish a commercial ranking. GPU capacity, batching, quantization, concurrent demand and alternative service rates can reverse the comparison. Quality and resource claims should be evaluated within each real model before attempting a hardware-dependent cross-provider ranking.''')
add('''## 7. Discussion and Implications for the Executed Study

Three findings of the reference analysis concern evaluation design rather than actual system effectiveness. First, ordinary testing can overstate migration quality: visible passing and independent preservation must be reported separately. Second, structural and semantic graph contributions should be separated; a plausible semantic overlay can increase expense and spurious context without improving delivery. Third, invariant gates trade acceptance precision against false rejection and latency. These tensions justify the proposed measurements even if executed results differ substantially from the simulation.

The core hypothesis must be tested against a strong B2 baseline and budget-matched alternatives. A larger prompt with more calls can produce an apparent graph benefit without a representational advantage. A supplemental treatment should represent the same verified relationships as plain text or substitute a token-matched irrelevant graph, allowing information relevance to be separated from serialization and context volume. This supplemental experiment is not numerically simulated in the present manuscript and should not be described as completed.

Preservation policies deserve explicit documentation. Exact cents, account identity and duplicate prevention are meaningful only when the task's reference policy establishes them. Some API migrations legitimately change default values or semantics. Where authoritative documentation conflicts with historical behaviour, abstention or a human decision can be necessary. The model cannot infer unavailable intent merely because it has a graph.

Before the main executed experiment, qualify each case through reference code, executable provider simulation and independent oracles. Independent reviewers should establish required behaviour and review patch disagreements without treatment/model labels where possible. Review history, disagreements and adjudication must be retained. No actual annotator agreement or human-subject outcome is manufactured in this reference study.

The currently available small live-quality assessment is developmental evidence, not statistical calibration for this dataset. A fresh pilot should measure error variation, workload distributions and semantic-gate behaviour. Its results should drive feasibility and power/precision analysis, followed by a frozen held-out protocol. Changing task labels, budgets or prompts after observing held-out failures would require transparent protocol deviations or a new development cohort.

Research execution should use disposable, isolated environments with bounded resources and network access; the product's temporary directory is not an operating-system sandbox. Real code and documents require appropriate licences and permissions. All financial interactions should use synthetic accounts. Application credentials, personal data and private keys must remain outside public artifacts and repository subprocess environments.''')
add('''## 8. Threats to Validity

### 8.1 Construct validity

The most important limitation is that correctness labels, detector counts, latency and tokens are sampled, not observed through code execution. Modeled hidden correctness is only a proxy for what actual qualified oracles would determine. Thus the reference dataset can validate arithmetic and analytical procedures, but not whether the architecture preserves business semantics. Simulated fault labels do not establish that actual models produce those exact defects.

Generated checks and repairs may share false assumptions. The real study requires human-reviewed, independent hidden oracles and varied execution traces. Oracle incompleteness, ambiguous requirements and legitimate alternative implementations can affect correctness labels. Exact golden-patch matching would inappropriately reject behaviourally equivalent repairs.

### 8.2 Internal validity

Treatment-specific probabilities and resource levels intentionally encode expected architectural tradeoffs. They are not empirically fitted parameters, and favourable full-method outcomes can partly reflect assumptions chosen by the authors. Simulation bootstrap intervals cannot remove this bias. Dependence through shared random variables is an explicit modeling choice, not a substitute for execution-level dependence analysis.

The practical-cost condition gives variants different stage structures and effective computation. It cannot identify a pure graph effect under equal resources. Prompt content, localization quality, feedback availability and generated-check gates are multiple interventions. Orthogonal or budget-matched follow-up treatments are needed for narrower causal claims.

### 8.3 External validity

All 120 tasks are controlled descriptors within four domains. Twelve synthetic families are not twelve real industrial codebases. The simulation establishes no generalization to naturally occurring migrations, large repositories, additional programming languages, SDK wrappers, dynamic reflection or real distributed-state semantics. The 48-task replication remains a subset of the same constructed benchmark and does not broaden the task population.

OW-SIM is not evidence about any actual Llama or DeepSeek checkpoint; G-SIM is not evidence about a pinned Gemini snapshot. Real model behaviour depends on training data, version, prompt formatting, reasoning configuration and runtime. Proprietary-model updates and unknown training overlap, as well as open-weight quantization and hardware effects, must be disclosed in an executed study.

### 8.4 Statistical conclusion validity

Repeated runs are nested in cases and families. Treating 400 repairable runs as 400 independent migrations would overstate precision; the synthetic hierarchical bootstrap avoids that arithmetic error while remaining conditional on a small invented cluster structure. Confidence intervals here concern synthetic resampling only. Their exclusion of zero must not be presented as a real-world superiority finding.

Diagnostic strata are small, overlapping and chosen to illustrate preservation concerns. Financial and duplicate-prevention rates must not be pooled as independent evidence. No synthetic p-value or model-generated judgement substitutes for an independently powered empirical design. Multiplicity handling, primary contrasts and smallest meaningful effects should be frozen before real held-out outcomes are inspected.

### 8.5 Reproducibility and cost validity

The generator and fixed seed reproduce numerical artifacts exactly in the recorded Python environment. This is computational replay of a simulation, not reproduction of model responses. No genuine provider snapshot, checkpoint digest, response trace, invoice or GPU telemetry is present. Hypothetical rates omit idle reservation, acquisition, network, storage and energy, so estimates are unsuitable for purchasing decisions or provider-performance claims.

Real reproducibility requires actual implementation snapshots, dependency locks, prompts, request/returned model versions, dates, stage usage and recorded failures. A Git HEAD alone cannot identify an uncommitted implementation; a source archive/hash manifest or an authorized frozen commit is required. Hidden checks must remain inaccessible during generation and should be released with the final artifact when licensing and evaluation policy permit.''')
add('''## 9. Artifact, Integrity and Reporting Statement

The companion artifact contains 120 synthetic task descriptors, 5,040 outcome/resource rows, a deterministic generator, numerical summaries and a manifest identifying the simulation and assumed cost rates. Each row carries a synthetic flag. Consistency assertions enforce hidden-correct ≤ accepted ≤ visible-pass, the primary/replication run totals and exclusive outcome accounting. Tables are generated from the retained rows rather than entered independently.

No prompts, actual candidate patches, evaluated client repositories, private credentials, human annotation records or measured hardware traces are represented as having been collected. The artifact must be distributed as a methodological illustration. Replacing the word “synthetic” with “empirical” would not transform it into valid evidence.

For an empirical submission, replace all constructed outcomes with executed observations under a qualified, frozen protocol; attach task/oracle provenance and implementation/model identities; preserve every failure; recompute tables and uncertainty; review every assertion and abstract number. Use of generative tools to prepare research or manuscript content should follow the selected venue's current policy and remain under accountable human authorship. Publication venue, affiliations and authors are not invented in this reference document.''')
add(f'''## 10. Conclusion

APIShield provides a candidate architecture for combining API-change localization, graph context and behavioural validation in migration repair. This explicitly synthetic reference study specifies the experiments and reporting needed to evaluate that architecture rigorously. Its primary simulated matrix contains 3,600 task-runs and its all-treatment open-weight-class replication adds 1,440. In the constructed primary realization, full-system delivery is {percent(g['B6']['hidden']['value'])}% versus {percent(g['B2']['hidden']['value'])}% for ordinary test feedback, with fewer incorrect accepted candidates but higher cost and latency. Semantic grouping alone supplies no clear primary-cohort advantage, and generated checks withhold some correct candidates.

These numerical patterns are illustrations of possible tradeoffs, not empirical APIShield findings. The next scientific step is an independent-oracle-qualified pilot followed by frozen, budget-accounted executions and transparent failure analysis. The value of the architecture remains to be established by those observations.

## References

[1] K. Yamagishi, N. Yoshida, E. Makihara, and K. Inoue, “Automated Program Repair Based on REST API Specifications Using Large Language Models,” arXiv:2510.25148, 2025. https://arxiv.org/abs/2510.25148

[2] S. Nielebock, P. Blockhaus, J. Krüger, and F. Ortmeier, “ASAP-Repair: API-Specific Automated Program Repair Based on API Usage Graphs,” APR 2024; arXiv:2402.07542. https://doi.org/10.1145/3643788.3648011

[3] T. Nguyen et al., “REST API Testing with Verified LLM-Inferred Dependencies and Response-Driven Refinement,” arXiv:2608.17546, 2026, preprint. https://arxiv.org/abs/2608.17546

[4] ACM SIGSOFT, “Empirical Standards for Software Engineering Research,” accessed 14 October 2026. https://www2.sigsoft.org/EmpiricalStandards/

## Appendix A. Reproduction and transition to empirical execution

From the ProjectSeven root, run the Python environment on research/simulation/generate_reference.py, then research/simulation/build_manuscript.py. Both are offline and invoke no model or repository repair. The output directory is docs/academic-synthetic-reference. The simulation_manifest.json identifies seed, assumptions and source/output hashes.

The frozen empirical successor must supply runnable repositories/providers; reviewed reference behaviour and hidden oracles; implemented B1–B6 treatment switches; explicit semantic-overlay prompt wiring; actual backend snapshots/checkpoints and hardware; per-stage instrumentation; randomized scheduling; budgets and stopping rules; and real error traces. A budget-matched comparator and an independently selected natural-migration cohort would strengthen the subsequent journal paper. None is implied complete by the populated reference tables.''')
paper='\n\n'.join(parts)+'\n'
(OUT/'APIShield-synthetic-reference-manuscript.md').write_text(paper,encoding='utf-8')
print(json.dumps({'synthetic':True,'words':len(paper.split()),'tables':12,'path':str(OUT/'APIShield-synthetic-reference-manuscript.md')},indent=2))
