"""Aggregate actual trace files. Fixture and live evidence cannot be pooled."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT=Path(__file__).resolve().parents[2]

def wilson(successes,total,alpha=.05):
    if not total:return None,None
    z=norm.ppf(1-alpha/2);p=successes/total;den=1+z*z/total
    middle=(p+z*z/(2*total))/den
    half=z*np.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return float(middle-half),float(middle+half)

def bootstrap_cases(frame,column,seed=42,draws=2000):
    values=frame.groupby('task_id')[column].mean().dropna().to_numpy(dtype=float)
    if not len(values):return None,None
    samples=np.random.default_rng(seed).choice(values,(draws,len(values)),replace=True).mean(axis=1)
    return [float(x) for x in np.quantile(samples,[.025,.975])]

def cliffs_delta(left,right):
    if not len(left) or not len(right):return None
    differences=np.asarray(left)[:,None]-np.asarray(right)[None,:]
    return float((np.sum(differences>0)-np.sum(differences<0))/differences.size)

def load(directory):
    columns=(ROOT/'docs/academic-run-record-template.csv').read_text(encoding='utf-8').strip().split(',')
    rows=[];seen=set()
    for path in sorted(directory.glob('B*_TASK-*_rep*.json')):
        trace=json.loads(path.read_text(encoding='utf-8'))
        if trace['run_id'] in seen:raise ValueError('Duplicate run ID')
        seen.add(trace['run_id'])
        if set(trace['record'])!=set(columns):raise ValueError(f'56-column schema mismatch: {path.name}')
        if trace['configuration'] != trace['record']['method']:raise ValueError('Configuration alias mismatch')
        if abs(sum(trace['phases_seconds'].values())+trace['overhead_seconds']-trace['record']['total_seconds'])>1e-7:
            raise ValueError('Phase ledger does not reconcile')
        rows.append({**trace['record'],'run_id':trace['run_id'],'record_kind':trace['record_kind'],
                     'classification':trace['classification'],'requested_model':trace['requested_model'],
                     'public_success':int(trace['visible_test_exit_code']==0) if trace['visible_test_exit_code'] is not None else np.nan,
                     'hidden_success':int(trace['hidden_oracle_exit_code']==0) if trace['hidden_oracle_exit_code'] is not None else np.nan,
                     'delivered_success':np.nan if trace['classification']=='NOT_EVALUATED' else int(trace['classification']=='PASS'),
                     'tp':trace['detection']['true_positive'],'fp':trace['detection']['false_positive'],'fn':trace['detection']['false_negative']})
    if not rows:raise ValueError('No raw traces found')
    frame=pd.DataFrame(rows)
    if frame['record_kind'].nunique()!=1:raise ValueError('Fixture replay and live model records must be analysed separately')
    return frame

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();frame=load(args.runs)
    ledger=pd.read_csv(args.runs/'resource_ledger.csv')
    if set(ledger.run_id)!=set(frame.run_id):raise ValueError('Ledger and trace run inventories differ')
    joined=frame.merge(ledger[['run_id','total_seconds','prompt_tokens','completion_tokens']],on='run_id',validate='one_to_one',suffixes=('','_ledger'))
    if not np.allclose(joined.total_seconds,joined.total_seconds_ledger,atol=1e-9):raise ValueError('Ledger time mismatch')
    if not np.array_equal(joined.input_tokens,joined.prompt_tokens):raise ValueError('Ledger input-token mismatch')
    if not np.array_equal(joined.output_tokens+joined.reasoning_tokens,joined.completion_tokens):raise ValueError('Ledger completion-token mismatch')
    args.output.mkdir(parents=True,exist_ok=False)
    frame.to_csv(args.output/'parsed_records.csv',index=False)
    summaries=[]
    for (kind,provider,model,method),group in frame.groupby(['record_kind','provider','requested_model','method'],dropna=False):
        row={'record_kind':kind,'provider':None if pd.isna(provider) else provider,'requested_model':None if pd.isna(model) else model,
             'configuration':method,'task_runs':len(group),'independent_tasks':group.task_id.nunique()}
        for metric,num,den in [('precision',int(group.tp.sum()),int((group.tp+group.fp).sum())),('recall',int(group.tp.sum()),int((group.tp+group.fn).sum()))]:
            lo,hi=wilson(num,den)
            row.update({metric:num/den if den else None,metric+'_numerator':num,metric+'_denominator':den,
                        metric+'_wilson_lo':lo,metric+'_wilson_hi':hi})
        for metric in ['public_success','hidden_success','delivered_success']:
            successes=int(group[metric].sum());observed=int(group[metric].notna().sum());lo,hi=wilson(successes,observed);blo,bhi=bootstrap_cases(group,metric)
            row.update({metric:successes/observed if observed else None,metric+'_successes':successes,metric+'_evaluated_runs':observed,metric+'_wilson_lo':lo,metric+'_wilson_hi':hi,
                        metric+'_case_bootstrap_lo':blo,metric+'_case_bootstrap_hi':bhi})
        row.update(mean_wall_seconds=float(group.total_seconds.mean()),sd_wall_seconds=float(group.total_seconds.std(ddof=1)) if len(group)>1 else None,
                   total_estimated_api_usd=float(group.estimated_cost.sum()) if group.estimated_cost.notna().all() else None,
                   plausible_incorrect=int((group.classification=='PLAUSIBLE_BUT_INCORRECT').sum()))
        summaries.append(row)
    effects=[]
    for (provider,model),block in frame.groupby(['provider','requested_model'],dropna=False):
        a=block[block.method=='B1'].groupby('task_id').delivered_success.mean().dropna()
        b=block[block.method=='B6'].groupby('task_id').delivered_success.mean().dropna()
        common=a.index.intersection(b.index)
        if len(common):
            delta=(b[common]-a[common]).to_numpy()
            draws=np.random.default_rng(42).choice(delta,(2000,len(delta)),replace=True).mean(axis=1)
            effects.append({'provider':None if pd.isna(provider) else provider,'requested_model':None if pd.isna(model) else model,
                'contrast':'B6-B1','paired_tasks':len(common),'mean_paired_difference':float(delta.mean()),
                'paired_case_bootstrap_95':[float(x) for x in np.quantile(draws,[.025,.975])],
                'cliffs_delta_B6_vs_B1':cliffs_delta(b[common].to_numpy(),a[common].to_numpy()),
                'cliffs_delta_note':'Marginal descriptive ordinal effect; paired difference and case bootstrap are the matched-task analysis.'})
    report={'record_kind':str(frame.record_kind.iloc[0]),'schema_columns':56,'summaries':summaries,'effects':effects,
        'interpretation':'Qualification traces exercise instrumentation only; no model-quality inference.' if frame.record_kind.iloc[0]=='fixture_replay' else 'Descriptive output; finalize preregistered family-cluster analysis before confirmatory claims.',
        'ci_caveat':'Wilson intervals treat counted units as independent and are descriptive only with repeated/correlated calls. Case bootstrap preserves repetitions; multi-project studies also need family-level clustering.'}
    (args.output/'metrics.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
    pd.DataFrame(summaries).to_csv(args.output/'aggregate_metrics.csv',index=False)
    print(json.dumps({'raw_traces':len(frame),'output':str(args.output),'record_kind':report['record_kind']}))

if __name__=='__main__':main()
