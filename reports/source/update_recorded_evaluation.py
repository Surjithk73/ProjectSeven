"""Integrate retained benchmark observations without changing experiment artifacts."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'reports/source'
path = SRC / 'report.md'
text = path.read_text(encoding='utf-8')

def replace(old, new):
    global text
    assert text.count(old) == 1, old[:100]
    text = text.replace(old, new)

start = text.index('# CHAPTER 7\n')
end = text.index('# CHAPTER 8\n', start)
text = text[:start] + (SRC/'recorded_evaluation.md').read_text(encoding='utf-8').rstrip() + '\n\n<!-- PAGE -->\n' + text[end:]

replace("Jobs inspect a committed revision rather than the user's uncommitted working files.",
        'Jobs capture committed source or a hashed working-tree snapshot. The current browser workflow includes uncommitted source and compares active documentation with the accepted baseline.')
replace('Repositories|Committed local Python source|Additional languages and repository acquisition',
        'Repositories|Committed or captured working Python source|Additional languages and repository acquisition')
replace('Research|Synthetic acceptance records and study design|Controlled baseline and real-world benchmark results',
        'Research|Historical acceptance, fixture qualification and live inference records|Evaluated multi-task model benchmark')
replace('The controlled study is specified in Chapter 7; its results remain unmeasured. Existing acceptance evidence is analyzed separately in Chapter 6.',
        'Chapter 7 reports benchmark qualification and recorded inference, with the larger comparative study identified as incomplete. Historical acceptance evidence is analyzed separately in Chapter 6.')
replace('disposable committed-source snapshots, guarded Python edits', 'disposable source snapshots, guarded Python edits')
replace('Chapter 7 specifies the controlled study needed to test the comparative hypotheses.',
        'Chapter 7 analyzes the benchmark harness, executed qualification candidates, invariant failures and live inference measurements.')
replace('The workflow starts by connecting a committed repository and supplying current and updated JSON OpenAPI descriptions.',
        'The workflow starts by connecting a local repository and supplying accepted and observed JSON OpenAPI descriptions. Current views include working edits, while retained jobs preserve their captured inputs.')
replace('The user can download it or separately prepare a GitHub draft preview.',
        'The user can download it, prepare a GitHub draft preview or explicitly apply a current browser repair. Apply verifies input freshness and retains original bytes for recovery.')
replace('FR01|Pin and snapshot committed source|configuration.py and workspace.py',
        'FR01|Capture committed or working source|configuration.py and workspace.py')
replace('The engine performs the committed-source transaction.', 'The engine performs the captured-source repair transaction.')
replace('The source record identifies the pinned commit and whether the original checkout contained dirty changes that were excluded. The engine reads raw Git blobs, avoiding transformations that an archive export could introduce.',
        'Committed-mode records identify the pinned commit and excluded working edits; the engine reads raw Git blobs. Working-mode records retain file hashes and captured bytes so current browser operations include uncommitted source. Both modes bind validation to a stable captured input.')
replace('Source metadata|Commit, dirty flag and excluded files|Identify analyzed committed tree',
        'Source metadata|Source mode, commit and captured file hashes|Identify the exact analyzed source')
replace('## 5.1 Committed source preparation', '## 5.1 Source capture and workspace preparation')
replace('The engine first validates the integration configuration and allocates a job outside the source repository. It resolves the configured Git ref to a commit and records whether the checkout is dirty. Uncommitted changes are excluded, which gives the analysis a stable source basis and avoids accidentally mixing an unfinished edit into an experiment.',
        'The engine validates configuration and allocates a job outside the repository. Committed mode resolves a Git revision and exports its objects. Working mode captures current permitted files and hashes, including uncommitted edits. Retries use the same retained input; later source changes require a new capture.')
replace('Workspace preparation inventories the committed tree and reads raw object bytes.',
        'Workspace preparation inventories the selected source mode and reads its retained bytes.')
replace('After a failed candidate the workspace is recreated from the pinned source.',
        'After a failed candidate the workspace is recreated from the captured source.') if 'After a failed candidate the workspace is recreated from the pinned source.' in text else None
replace('APIShield labels those origins and keeps optional AI interpretations outside the acceptance logic.',
        'APIShield labels those origins. Semantic interpretation can supply repair context, while acceptance still requires executed checks.')
replace('The practical distinction is the unit of work. APIShield\'s run is anchored to a source commit and paired contracts, with a selected migration obligation.',
        'The practical distinction is the unit of work. APIShield\'s run is anchored to captured source and paired contracts, with a selected migration obligation.')
replace('Generation receives selected impacted source, old and new contracts, comparison evidence and relevant context. When intent context is enabled, confirmed applicable requirements are included. Public validation feedback can inform a bounded retry. Independent held-out checks remain outside the generation context.',
        'Generation receives impacted source, paired contracts, comparison evidence and graph context. The browser AI path infers scoped rules and creates separate checks under tests/apishield_generated. Inferred rules retain their AI origin; they are not developer-confirmed truth. Existing tests remain protected. Generated checks must meaningfully fail against incompatible original code and pass after repair. Public feedback can support bounded retries; independent hidden checks remain outside generation (APIShield Project, 2026j).')
replace('The paired Overview retains original operations and source calls before presenting changes. A user can inspect request and response definitions, shared schemas and metadata. The Impact graph provides community navigation, source inspection, pan/zoom, node dragging and a searchable List fallback. Smaller screens can use List mode when a graph would be difficult to navigate.',
        'Current endpoint browsing shows the active contract and consumers without comparison badges. Change reports retain paired contracts and impact evidence. The graph supports community navigation, source inspection and a searchable List fallback. After review, Apply writes the repair and generated tests without a commit, rejects stale inputs and retains recovery bytes. A successful current repair accepts the captured contract and refreshes the current graph; historical reports retain their prior evidence (APIShield Project, 2026j).')
replace('The available evaluation consists of engineering regression records, synthetic live-model acceptance and a controlled GitHub draft exercise.',
        'The available evaluation comprises historical engineering acceptance, a controlled GitHub draft exercise, authored benchmark qualification and live inference diagnostics.')
replace('The academic contribution is best stated as a testable mechanism: explicit requirements select additional acceptance checks and remain traceable to affected operations and source. This differs from merely placing an inferred intent sentence in a prompt. The implemented relationship and evidence model make that mechanism inspectable, but the present records do not establish its causal superiority over matched baselines.',
        'The academic contribution is an inspectable integration of graph context, preservation constraints and validated API migration. Current browser repairs infer additional checks, while confirmed requirements retain separate provenance. The benchmark harness executes six treatment configurations and separates hidden evaluation from development feedback. Four authored tasks establish evaluator discrimination; eighteen live traces establish inference and resource observations. They do not establish causal superiority on a representative migration population.')
replace('Its core connects a committed source revision, paired OpenAPI descriptions, scoped requirements and validation evidence.',
        'Its core connects captured source, paired OpenAPI descriptions, scoped requirements, inferred checks and validation evidence.')
replace('It has not completed comprehensive field-flow analysis, per-project execution environments, a controlled benchmark or hosted customer operation.',
        'It has not completed comprehensive field-flow analysis, per-project execution environments, a representative evaluated model benchmark or hosted customer operation.')
replace('Identifiers and values are placeholders until the controlled study is performed.',
        'The form distinguishes available diagnostic records from measurements still needed for a full evaluated model benchmark.')
replace('Research treatment adapter|[CODE PATH, COMMIT AND ENABLED STAGES]',
        'Research treatment adapter|benchmarks/harness/run_ablation.py and configurations.json; retained source hashes')
replace('Task and oracle assets|[REPOSITORIES, PUBLIC TESTS, HIDDEN TESTS AND REFERENCE PATCHES]',
        'Task and oracle assets|Four complete tasks under benchmarks/tasks and evaluator_private; expanded corpus pending')
replace('The evidence package is [RAW RUN DIRECTORY OR ARCHIVE].',
        'Recorded evidence is under benchmarks/runs and benchmarks/analysis; the complete evaluated model corpus is [FULL STUDY ARCHIVE].')
replace('The analysis entry point is [ANALYSIS SCRIPT AND COMMAND].',
        'The analysis entry point is benchmarks/harness/aggregate_metrics.py; the final study command is [FULL STUDY ANALYSIS COMMAND].')
replace('Comparative improvement|Matched baselines and independent oracle|NOT MEASURED',
        'Comparative improvement|Evaluated model repairs under matched conditions|Pending full model benchmark')
replace('docs/project-folder-transfer.md|Current source location and transfer verification',
        'benchmarks/REVIEW_STATUS.md|Executed qualification and live inference scope\nbenchmarks/analysis/live_diagnostic_review/metrics.json|18 live traces and missing correctness outcomes\ndocs/current-api-ai-repair-walkthrough.md|Working source, inferred checks and reviewed Apply')
path.write_text(text, encoding='utf-8')

refs_path = SRC/'references.json'
refs = json.loads(refs_path.read_text(encoding='utf-8'))
refs[8:8] = [
    {'author':'APIShield Project','year':'2026i','title':'Recorded benchmark qualification and live inference diagnostics','type':'Unpublished project evaluation record','url':'benchmarks/REVIEW_STATUS.md; benchmarks/analysis/live_diagnostic_review/metrics.json'},
    {'author':'APIShield Project','year':'2026j','title':'Working source API repair and reviewed Apply workflow','type':'Unpublished project implementation and validation record','url':'docs/current-api-ai-repair-walkthrough.md'},
]
refs_path.write_text(json.dumps(refs, indent=2), encoding='utf-8')
print('Updated report source and 27 references')
