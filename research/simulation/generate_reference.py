"""Generate explicitly synthetic outcomes; never calls models or executes repairs."""
import csv
import hashlib
import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

SEED = 20261014
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs' / 'academic-synthetic-reference'
OUT.mkdir(parents=True, exist_ok=True)
rng = random.Random(SEED)
methods = [f'B{i}' for i in range(1, 7)]
domains = ['Banking/payments', 'Shipping', 'Identity', 'Multi-endpoint schemas']
tasks = []
for di, domain in enumerate(domains):
    labels = ['repairable'] * 20 + ['negative'] * [6, 6, 6, 7][di] + ['underspecified'] * [4, 4, 4, 3][di]
    rng.shuffle(labels)
    counts = defaultdict(int)
    for j, label in enumerate(labels):
        idx = counts[label]
        counts[label] += 1
        tasks.append(dict(task_id=f'SIM-{di+1}-{j+1:02d}', domain=domain,
                          family=f'SIM-family-{di+1}-{j//10+1}', task_class=label,
                          difficulty=rng.uniform(-.14, .14),
                          financial=di == 0 and label == 'repairable',
                          duplicate=di == 0 and label == 'repairable' and idx < 10,
                          nesting=label == 'repairable' and ((di == 1 and idx < 12) or (di == 3 and idx < 8)),
                          affected_calls=0 if label == 'negative' else rng.randint(1, 4)))
subset = []
for di, domain in enumerate(domains):
    for label, n in [('repairable',8),('negative',[2,3,2,3][di]),('underspecified',[2,1,2,1][di])]:
        subset += rng.sample([t for t in tasks if t['domain'] == domain and t['task_class'] == label],n)
subset_ids = {t['task_id'] for t in subset}
for t in tasks:
    t['replication_subset'] = t['task_id'] in subset_ids
    t['synthetic'] = True

records = []
probabilities = {'G-SIM':[.55,.64,.71,.735,.80,.825], 'OW-SIM':[.43,.52,.595,.62,.69,.72]}
for model in probabilities:
    selected_tasks = tasks if model == 'G-SIM' else subset
    for t in selected_tasks:
        for rep in range(5):
            shared = random.Random(f'{SEED}:{model}:{t["task_id"]}:{rep}')
            repair_u, visible_u, operation_u, negative_u, abstain_u = [shared.random() for _ in range(5)]
            for mi, method in enumerate(methods):
                local = random.Random(f'{SEED}:{model}:{t["task_id"]}:{rep}:{method}')
                penalty = {'Banking/payments':-.09,'Shipping':.07,'Identity':.015,'Multi-endpoint schemas':-.045}[t['domain']]
                p = probabilities[model][mi] + t['difficulty'] + penalty
                operation_failure = operation_u < (.025 if model == 'G-SIM' else .01)
                invalid = not operation_failure and local.random() < (.018 + (.008 if mi in [3,4,5] else 0))
                candidate_correct = t['task_class'] == 'repairable' and not (operation_failure or invalid) and repair_u + local.uniform(-.07,.07) < p
                visible = t['task_class'] == 'repairable' and not (operation_failure or invalid) and (candidate_correct or visible_u < [.34,.55,.53,.52,.45,.43][mi])
                accepted = visible and (mi not in [4,5] or (local.random() > .045 if candidate_correct else local.random() < [.36,.28][mi-4]))
                hidden = accepted and candidate_correct
                false_edit = t['task_class'] == 'negative' and not operation_failure and negative_u < [.26,.18,.10,.12,.07,.05][mi] + (.06 if model == 'OW-SIM' else 0)
                abstain = t['task_class'] == 'underspecified' and not (operation_failure or invalid) and abstain_u < [.38,.52,.65,.67,.81,.86][mi] - (.1 if model == 'OW-SIM' else 0)
                if t['task_class'] == 'repairable':
                    outcome = ('provider_failure' if operation_failure and model == 'G-SIM' else 'runtime_failure' if operation_failure else
                               'invalid_output' if invalid else 'correct_repair' if hidden else
                               'accepted_invariant_violation' if accepted else 'check_rejected' if visible else 'visible_test_rejected')
                elif t['task_class'] == 'negative':
                    outcome = 'operational_failure' if operation_failure else 'unnecessary_edit' if false_edit else 'correct_no_change'
                else:
                    outcome = 'operational_failure' if operation_failure or invalid else 'correct_abstention' if abstain else 'unsupported_assumption'
                recall = [.68,.75,.86,.875,.86,.89][mi] - (.055 if model == 'OW-SIM' else 0)
                tp = sum(local.random() < recall for _ in range(t['affected_calls']))
                fp = sum(local.random() < [.23,.18,.10,.12,.095,.075][mi] for _ in range(3))
                if false_edit: fp = max(fp,1)
                retry = int(local.random() < [.35,.46,.35,.33,.28,.25][mi] + (.10 if model == 'OW-SIM' else 0))
                if local.random() < .055: retry += 1
                factor = max(.45,local.lognormvariate(-.035,.28)) * (1 + retry*.25)
                pt = round([2400,3000,3800,5600,6700,8600][mi] * factor)
                ct = round([700,1000,1150,1700,2150,2800][mi] * factor)
                stages = 1 + retry + (mi in [3,5]) + (mi in [4,5])
                latency = ([30,43,54,75,88,109][mi] if model == 'G-SIM' else [65,85,108,149,172,215][mi]) * factor
                if operation_failure: latency = 240 + local.random()*30
                if t['task_class'] == 'negative' and not (false_edit or operation_failure or invalid):
                    retry = 0
                    if mi >= 2:
                        pt = ct = stages = 0
                        latency = 3 * factor
                    else:
                        pt = round(pt*.45)
                        ct = round(ct*.20)
                        stages = 1
                        latency *= .40
                if latency > 600:
                    latency = 600
                    visible = accepted = hidden = candidate_correct = false_edit = abstain = False
                    outcome = 'budget_exhausted'
                cpu_s = min(30, 6 + latency*.10)
                if model == 'G-SIM': cost = (pt*.50 + ct*3.00)/1e6 + cpu_s*.10/3600
                else: cost = (latency * .82 * 2.50 / 3600 if stages else 0) + cpu_s*.10/3600
                rec = dict(synthetic=True,model=model,method=method,task_id=t['task_id'],family=t['family'],domain=t['domain'],
                           task_class=t['task_class'],repetition=rep+1,visible_pass=int(visible),accepted=int(accepted),
                           candidate_correct=int(candidate_correct),hidden_correct=int(hidden),false_edit=int(false_edit),correct_abstention=int(abstain),
                           correct_no_change=int(outcome == 'correct_no_change'),
                           tp=tp,fp=fp,fn=t['affected_calls']-tp,prompt_tokens=pt,completion_tokens=ct,retries=retry,calls=stages,
                           latency_s=round(latency,4),controller_cpu_s=round(cpu_s,4),estimated_cost=round(cost,8),outcome=outcome)
                for flag, chance in [('financial',.18),('duplicate',.22),('nesting',.25)]:
                    rec[f'{flag}_eligible'] = int(t[flag])
                    rec[f'{flag}_preserved'] = int(t[flag] and accepted and (candidate_correct or local.random() < chance))
                records.append(rec)

def save_csv(path, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save_csv(OUT/'synthetic_tasks.csv',tasks)
save_csv(OUT/'synthetic_runs.csv',records)

def values(rows, kind):
    if kind == 'cost_success':
        den=sum(x['hidden_correct'] for x in rows)
        return sum(x['estimated_cost'] for x in rows)/den if den else 0
    if kind == 'precision':
        den=sum(x['tp']+x['fp'] for x in rows);return sum(x['tp'] for x in rows)/den if den else 0
    if kind == 'recall':
        den=sum(x['tp']+x['fn'] for x in rows);return sum(x['tp'] for x in rows)/den if den else 0
    return st.mean(x[kind] for x in rows)

def interval(rows, kind, repetitions=1200):
    grouped=defaultdict(lambda:defaultdict(list))
    for x in rows:grouped[x['family']][x['task_id']].append(x)
    families=list(grouped)
    boot=random.Random(f'{SEED}:{kind}:{rows[0]["model"]}:{rows[0]["method"]}:{len(rows)}')
    results=[]
    for _ in range(repetitions):
        sample=[]
        for family in boot.choices(families,k=len(families)):
            cases=list(grouped[family])
            for case in boot.choices(cases,k=len(cases)):sample.extend(grouped[family][case])
        results.append(values(sample,kind))
    results.sort();return [results[int(.025*repetitions)],results[int(.975*repetitions)]]

def summarize(rows, field):
    score=values(rows,field)
    by_rep=[values([x for x in rows if x['repetition']==r],field) for r in range(1,6)]
    return dict(value=score,sd_repetitions=st.stdev(by_rep),ci95=interval(rows,field))

summary={}
for model in probabilities:
    summary[model]={}
    for method in methods:
        all_rows=[x for x in records if x['model']==model and x['method']==method]
        pos=[x for x in all_rows if x['task_class']=='repairable']
        neg=[x for x in all_rows if x['task_class']=='negative']
        amb=[x for x in all_rows if x['task_class']=='underspecified']
        r=dict(n_total=len(all_rows),n_repairable=len(pos),correct=sum(x['hidden_correct'] for x in pos),visible_count=sum(x['visible_pass'] for x in pos),
               accepted_count=sum(x['accepted'] for x in pos),wrong_accepted=sum(x['accepted'] and not x['candidate_correct'] for x in pos),
               hidden=summarize(pos,'hidden_correct'),visible=summarize(pos,'visible_pass'),precision=summarize(all_rows,'precision'),recall=summarize(all_rows,'recall'),
               negative_specificity=summarize(neg,'false_edit'),abstention=summarize(amb,'correct_abstention'),
               no_change=summarize(neg,'correct_no_change'),
               total_cost=sum(x['estimated_cost'] for x in all_rows),cost_success=sum(x['estimated_cost'] for x in all_rows)/max(1,sum(x['hidden_correct'] for x in pos)),
               cost_success_ci95=interval(all_rows,'cost_success'),latency_ci95=interval(all_rows,'latency_s'),
               failures=dict((k,sum(x['outcome']==k for x in pos)) for k in sorted({x['outcome'] for x in pos})))
        for field in ['prompt_tokens','completion_tokens','retries','latency_s','calls']:
            r[field]=dict(mean=st.mean(x[field] for x in all_rows),sd=st.stdev(x[field] for x in all_rows))
        for field in ['financial','duplicate','nesting']:
            eligible=[x for x in pos if x[field+'_eligible']]
            r[field]=dict(n=len(eligible),passed=sum(x[field+'_preserved'] for x in eligible),stats=summarize(eligible,field+'_preserved'))
        summary[model][method]=r

def paired_difference(model,a,b,subset_only=False):
    ra=[x for x in records if x['model']==model and x['method']==a and x['task_class']=='repairable' and (not subset_only or x['task_id'] in subset_ids)]
    rb={(x['task_id'],x['repetition']):x for x in records if x['model']==model and x['method']==b}
    pairs=[dict(x,delta=x['hidden_correct']-rb[(x['task_id'],x['repetition'])]['hidden_correct']) for x in ra]
    by_rep=[values([x for x in pairs if x['repetition']==r],'delta') for r in range(1,6)]
    return dict(value=values(pairs,'delta'),sd_repetitions=st.stdev(by_rep),ci95=interval(pairs,'delta'))
summary['paired']={f'{m}:{a}-{b}':paired_difference(m,a,b) for m in probabilities for a,b in [('B3','B2'),('B4','B3'),('B5','B3'),('B6','B2'),('B6','B5')]}
summary['matched_G']={method:summarize([x for x in records if x['model']=='G-SIM' and x['method']==method and x['task_class']=='repairable' and x['task_id'] in subset_ids],'hidden_correct') for method in methods}
(OUT/'synthetic_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
manifest=dict(synthetic=True,seed=SEED,tasks=120,subset_tasks=48,repetitions=5,gemini_task_runs=3600,open_weight_task_runs=1440,total_task_runs=len(records),
              model_identifiers={'G-SIM':'Gemini-like simulated backend; no actual pinned provider snapshot','OW-SIM':'70B open-weight-class simulated backend; no checkpoint executed'},
              cost_assumptions={'G-SIM':'USD 0.50 per million prompt and USD 3.00 per million completion tokens, hypothetical, not vendor prices',
                                'OW-SIM':'USD 2.50/GPU-service-hour; 82% of modeled wall time when calls exist; assumed rate, no hardware benchmark',
                                'controller':'USD 0.10/CPU-hour applied to modeled active controller CPU time; storage/network/energy overhead excluded'},
              intervals='95% hierarchical bootstrap over synthetic families then cases; repetitions retained together; 1200 bootstrap draws',
              provenance='Assumption-driven illustration; not fitted to pilot observations; hidden labels and all resources are simulated, not executed',
              files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [OUT/'synthetic_tasks.csv',OUT/'synthetic_runs.csv',OUT/'synthetic_summary.json']},
              generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(OUT/'simulation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
assert len(records)==5040 and len(tasks)==120 and len(subset)==48
assert all(x['hidden_correct'] <= x['accepted'] <= x['visible_pass'] for x in records)
assert all(sum(v['failures'].values())==v['n_repairable'] for m in probabilities for v in summary[m].values())
print(json.dumps({'synthetic':True,'rows':len(records),'G_correct':{m:summary['G-SIM'][m]['correct'] for m in methods},'G_B6_vs_B2':summary['paired']['G-SIM:B6-B2']},indent=2))
