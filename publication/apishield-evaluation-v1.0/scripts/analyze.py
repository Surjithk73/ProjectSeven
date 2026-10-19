"""Analyze primary benchmark evaluation dataset, financial invariants, and open-weight replication to produce academic tables."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]


def wilson(successes, total):
    """Compute two-sided 95% Wilson score confidence interval."""
    if total <= 0:
        return 0.0, 0.0
    z = norm.ppf(0.975)
    p = successes / total
    den = 1 + z * z / total
    mid = (p + z * z / (2 * total)) / den
    half = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return float(max(0.0, mid - half)), float(min(1.0, mid + half))


def paired_bootstrap(left, right, strata, draws=20000):
    """Paired domain-stratified bootstrap for risk difference on paired benchmark tasks."""
    rng = np.random.default_rng(42)
    groups = [np.flatnonzero(strata == s) for s in sorted(set(strata))]
    diffs = []
    for _ in range(draws):
        idx = np.concatenate([rng.choice(grp, len(grp), replace=True) for grp in groups])
        diffs.append(float((left[idx] - right[idx]).mean()))
    return np.quantile(diffs, [0.025, 0.975]).tolist()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=ROOT / "data/benchmarks/benchmark_execution_outcomes.csv")
    p.add_argument("--fin_data", type=Path, default=ROOT / "data/benchmarks/financial_invariant_evaluations.csv")
    p.add_argument("--ow_data", type=Path, default=ROOT / "data/benchmarks/open_weight_execution_outcomes.csv")
    p.add_argument("--output", type=Path, default=ROOT / "analysis")
    args = p.parse_args()

    # 1. Primary Benchmark Analysis (120 tasks x 6 configs)
    frame = pd.read_csv(args.data)
    frame["domain"] = frame.task_id.str.split("-").str[1]

    summaries = []

    for config, original in frame.groupby("configuration", sort=True):
        group = original.sort_values("task_id").copy()
        n = len(group)

        # Pure Estimated API Cost under Gemini 3.8 Flash rate card
        api_cost = (0.75 * group.prompt_tokens + 3.75 * group.completion_including_reasoning_tokens) / 1e6
        group["estimated_api_usd"] = api_cost

        v = int(group.visible_pass.sum())
        h = int(group.hidden_pass.sum())
        vlo, vhi = wilson(v, n)
        hlo, hhi = wilson(h, n)

        tp = int(group.true_affected_localized.sum())
        fp = int(group.unaffected_false_alarm.sum())
        fn = n - tp
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / n
        fpr = fp / n
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        attempts = group["repair_attempts"] if "repair_attempts" in group.columns else np.ones(n)

        summaries.append(
            dict(
                config_id=config,
                tasks=n,
                tp=tp,
                fp=fp,
                fn=fn,
                precision=float(prec),
                recall=float(rec),
                fpr=float(fpr),
                f1=float(f1),
                visible_successes=v,
                visible_rate=v / n,
                visible_ci_low=vlo,
                visible_ci_high=vhi,
                hidden_successes=h,
                hidden_rate=h / n,
                hidden_ci_low=hlo,
                hidden_ci_high=hhi,
                prompt_tokens_mean=float(group.prompt_tokens.mean()),
                prompt_tokens_sd=float(group.prompt_tokens.std(ddof=1)),
                completion_tokens_mean=float(group.completion_including_reasoning_tokens.mean()),
                completion_tokens_sd=float(group.completion_including_reasoning_tokens.std(ddof=1)),
                mean_repair_attempts=float(attempts.mean()),
                runtime_mean=float(group.wall_seconds.mean()),
                runtime_sd=float(group.wall_seconds.std(ddof=1)),
                api_cost_total=float(api_cost.sum()),
                cost_per_hidden_correct=float(api_cost.sum() / h) if h > 0 else 0.0,
            )
        )

    # Statistical Contrasts (B6 vs B2, B6 vs B3)
    effects = []
    for baseline in ["B2", "B3"]:
        paired = (
            frame[frame.configuration.isin(["B6", baseline])]
            .pivot(index="task_id", columns="configuration", values="hidden_pass")
            .sort_index()
        )
        left = paired["B6"].astype(int).to_numpy()
        right = paired[baseline].astype(int).to_numpy()
        strata = paired.index.to_series().str.split("-").str[1].to_numpy()
        rd_ci = paired_bootstrap(left, right, strata)
        rd = float((left - right).mean())

        effects.append(
            dict(
                contrast="B6-" + baseline,
                paired_tasks=len(paired),
                risk_difference=rd,
                paired_stratified_bootstrap_95=rd_ci,
                cliffs_delta_equivalent=rd,
                cliffs_delta_bootstrap_95=rd_ci,
                baseline_only=int(((left == 0) & (right == 1)).sum()),
                full_only=int(((left == 1) & (right == 0)).sum()),
                both_correct=int(((left == 1) & (right == 1)).sum()),
                neither_correct=int(((left == 0) & (right == 0)).sum()),
            )
        )

    # 2. Financial Invariants Analysis (60 tasks)
    fin_summaries = []
    if args.fin_data.exists():
        fdf = pd.read_csv(args.fin_data)
        fdf["all_three"] = fdf.minor_units_pass & fdf.idempotency_pass & fdf.destination_pass
        for config, grp in fdf.groupby("configuration", sort=True):
            n_fin = len(grp)
            m_pass = int(grp.minor_units_pass.sum())
            i_pass = int(grp.idempotency_pass.sum())
            d_pass = int(grp.destination_pass.sum())
            a_pass = int(grp.all_three.sum())
            fin_summaries.append(
                {
                    "config_id": config,
                    "financial_tasks": n_fin,
                    "minor_units_pass": m_pass,
                    "minor_units_rate": m_pass / n_fin,
                    "idempotency_pass": i_pass,
                    "idempotency_rate": i_pass / n_fin,
                    "destination_pass": d_pass,
                    "destination_rate": d_pass / n_fin,
                    "all_three_pass": a_pass,
                    "all_three_rate": a_pass / n_fin,
                }
            )

    # 3. Open-Weight Replication Analysis (120 tasks x 6 configs x 2 models)
    ow_summaries = []
    if args.ow_data.exists():
        owdf = pd.read_csv(args.ow_data)
        for (model_name, config), grp in owdf.groupby(["model", "configuration"], sort=True):
            n_ow = len(grp)
            v_ow = int(grp.visible_pass.sum())
            h_ow = int(grp.hidden_pass.sum())
            vlo, vhi = wilson(v_ow, n_ow)
            hlo, hhi = wilson(h_ow, n_ow)
            tot_cost = float(grp.total_local_cost_usd.sum())
            ow_summaries.append(
                {
                    "config_id": config,
                    "model": model_name,
                    "runs": n_ow,
                    "tasks": int(grp.task_id.nunique()),
                    "repetitions": 1,
                    "visible_successes": v_ow,
                    "visible_rate": v_ow / n_ow,
                    "visible_ci_low": vlo,
                    "visible_ci_high": vhi,
                    "hidden_successes": h_ow,
                    "hidden_rate": h_ow / n_ow,
                    "hidden_ci_low": hlo,
                    "hidden_ci_high": hhi,
                    "runtime_mean": float(grp.wall_seconds.mean()),
                    "runtime_sd": float(grp.wall_seconds.std(ddof=1)),
                    "gpu_vram_peak_gb": float(grp.gpu_vram_peak_gb.mean()),
                    "gpu_power_mean_watts": float(grp.gpu_power_mean_watts.mean()),
                    "decoding_throughput_tok_sec": float(grp.decoding_throughput_tok_sec.mean()),
                    "energy_consumption_kwh_per_task": float(grp.energy_consumption_kwh.mean()),
                    "total_local_cost_usd": tot_cost,
                    "cost_per_hidden_correct_usd": float(tot_cost / h_ow) if h_ow > 0 else 0.0,
                }
            )

    # Write CSVs and JSON
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summaries).to_csv(args.output / "comparison.csv", index=False)
    frame.to_csv(args.output / "benchmark_accounting.csv", index=False)
    if fin_summaries:
        pd.DataFrame(fin_summaries).to_csv(args.output / "financial_invariants_comparison.csv", index=False)
    if ow_summaries:
        pd.DataFrame(ow_summaries).to_csv(args.output / "open_weight_comparison.csv", index=False)

    report = {
        "benchmark_kind": "executed_multi_domain_benchmark_and_open_weight_replication",
        "schema_version": "2.0",
        "bootstrap_seed": 42,
        "bootstrap_draws": 20000,
        "primary_model": "gemini-3.8-flash",
        "open_weight_models": ["Meta-Llama-3.1-70B-Instruct", "Qwen2.5-Coder-32B-Instruct"],
        "total_evaluated_tasks": int(frame["task_id"].nunique()),
        "total_primary_runs": len(frame),
        "total_open_weight_runs": sum(r["runs"] for r in ow_summaries),
        "qualification_executable_tasks": 120,
        "domains": sorted(frame["domain"].unique().tolist()),
        "summaries": summaries,
        "effects": effects,
        "financial_invariants": fin_summaries,
        "open_weight_summaries": ow_summaries,
    }
    (args.output / "metrics.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")

    # Format Markdown Tables
    lines = [
        "# Executed Benchmark & Open-Weight Replication Results\n",
        "**Table 1: Primary Benchmark & Ablation Study (N=120, Model: Gemini 3.8 Flash).**\n",
        "| Config | Visible Pass; % [95% Wilson CI] | Hidden Correct; % [95% Wilson CI] | Mean Attempts | Prompt Tokens (mean ± SD) | Completion Tokens (mean ± SD) | Estimated API Cost ($) | Estimated USD / Correct Repair |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in summaries:
        lines.append(
            f"| {r['config_id']} | {r['visible_successes']}/120; {100*r['visible_rate']:.1f}% [{100*r['visible_ci_low']:.1f}, {100*r['visible_ci_high']:.1f}] | {r['hidden_successes']}/120; {100*r['hidden_rate']:.1f}% [{100*r['hidden_ci_low']:.1f}, {100*r['hidden_ci_high']:.1f}] | {r['mean_repair_attempts']:.2f} | {r['prompt_tokens_mean']:.0f} ± {r['prompt_tokens_sd']:.0f} | {r['completion_tokens_mean']:.0f} ± {r['completion_tokens_sd']:.0f} | ${r['api_cost_total']:.4f} | ${r['cost_per_hidden_correct']:.5f} |"
        )

    lines += [
        "\n**Table 2: Primary Paired Contrasts & Effect Sizes (N=120).**\n",
        "| Contrast | Risk Difference, pp [Stratified Bootstrap 95% CI] | Cliff's Delta Equivalent [95% CI] | Win / Loss Breakdown (Full-only / Baseline-only / Both / Neither) |",
        "|---|---|---|---|",
    ]
    for e in effects:
        lo, hi = e["paired_stratified_bootstrap_95"]
        lines.append(
            f"| {e['contrast']} | +{100*e['risk_difference']:.1f} pp [{100*lo:.1f}, {100*hi:.1f}] | {e['cliffs_delta_equivalent']:.3f} [{lo:.3f}, {hi:.3f}] | {e['full_only']} / {e['baseline_only']} / {e['both_correct']} / {e['neither_correct']} |"
        )

    if fin_summaries:
        lines += [
            "\n**Table 3: Domain Invariant Preservation on Financial Integration Corpus (N=60).**\n",
            "| Configuration | Minor Units Preserved (%) | Idempotency Key Preserved (%) | Destination Routing Integrity (%) | All Invariants Preserved (%) |",
            "|---|---:|---:|---:|---:|",
        ]
        for f in fin_summaries:
            lines.append(
                f"| {f['config_id']} | {f['minor_units_pass']}/60 ({100*f['minor_units_rate']:.1f}%) | {f['idempotency_pass']}/60 ({100*f['idempotency_rate']:.1f}%) | {f['destination_pass']}/60 ({100*f['destination_rate']:.1f}%) | {f['all_three_pass']}/60 ({100*f['all_three_rate']:.1f}%) |"
            )

    lines += [
        "\n**Table 4: Change Detection and Impact Localization Performance (RQ1, N=120).**\n",
        "| Configuration | TP / FP / FN | Precision (%) | Recall (%) | False Alarm Rate (%) | F1-Score |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in summaries:
        lines.append(
            f"| {r['config_id']} | {r['tp']} / {r['fp']} / {r['fn']} | {100*r['precision']:.1f}% | {100*r['recall']:.1f}% | {100*r['fpr']:.1f}% | {r['f1']:.3f} |"
        )

    if ow_summaries:
        lines += [
            "\n**Table 5: Open-Weight Model Replication & Hardware Telemetry (N=120 Tasks per Configuration, llama.cpp Q4_K_M GGUF).**\n",
            "| Model | Config | Visible Pass (%) [95% CI] | Hidden Correct (%) [95% CI] | VRAM (GiB) | Power (W) | Throughput (tok/s) | Energy (Wh/task) | Local Cost / Correct ($) |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
        for o in ow_summaries:
            lines.append(
                f"| {o['model']} | {o['config_id']} | {o['visible_successes']}/120 ({100*o['visible_rate']:.1f}%) [{100*o['visible_ci_low']:.1f}, {100*o['visible_ci_high']:.1f}] | {o['hidden_successes']}/120 ({100*o['hidden_rate']:.1f}%) [{100*o['hidden_ci_low']:.1f}, {100*o['hidden_ci_high']:.1f}] | {o['gpu_vram_peak_gb']:.1f} | {o['gpu_power_mean_watts']:.1f} | {o['decoding_throughput_tok_sec']:.1f} | {1000*o['energy_consumption_kwh_per_task']:.2f} | ${o['cost_per_hidden_correct_usd']:.4f} |"
            )

    (args.output / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Successfully generated all empirical and open-weight tables to {args.output / 'tables.md'}")


if __name__ == "__main__":
    main()
