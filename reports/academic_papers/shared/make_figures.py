"""Rebuild the manuscript's vector plots from supplied aggregate results.

This script performs no repair execution, inference, statistical resampling,
or artifact verification. Values come from paper_submission_bundle/tables.md.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 9, "pdf.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
})
x = np.arange(6)
visible = np.array([76, 90, 93, 100, 105, 111]) / 120 * 100
hidden = np.array([26, 34, 36, 62, 87, 97]) / 120 * 100
low = np.array([15.2, 21.0, 22.5, 42.8, 63.9, 72.9])
high = np.array([29.9, 37.0, 38.7, 60.4, 79.7, 86.9])
labels = [f"B{i}" for i in range(1, 7)]

fig, ax = plt.subplots(figsize=(3.65, 2.65))
ax.bar(x - .18, visible, .35, label="Visible tests", color="#b8c8d8")
ax.bar(x + .18, hidden, .35, label="Hidden oracle", color="#167f82")
ax.errorbar(x + .18, hidden, yerr=[hidden - low, high - hidden],
            fmt="none", ecolor="#172a3a", capsize=2, lw=.7)
ax.set(xticks=x, xticklabels=labels, ylim=(0, 116), ylabel="Task success (%)")
ax.legend(frameon=False, loc="upper left", fontsize=8, ncol=2)
ax.grid(axis="y", alpha=.15)
ax.set_axisbelow(True)
for i, value in enumerate(hidden):
    ax.text(x[i] + .18, high[i] + 2, f"{value:.1f}", ha="center", va="bottom", fontsize=7.5)
fig.tight_layout(pad=.6)
for variant in ("ieee_conference", "ieee_access"):
    fig.savefig(ROOT / variant / "figures/correctness.pdf", bbox_inches="tight")
plt.close(fig)

cost = np.array([.4995, .612, .720, .8325, .954, 1.161]) / 120
fig, ax = plt.subplots(figsize=(3.65, 2.65))
ax.scatter(cost * 100, hidden, s=45, c=["#73899b"] * 5 + ["#167f82"], zorder=3)
for i, label in enumerate(labels):
    ax.annotate(label, (cost[i] * 100, hidden[i]), xytext=(5, 1),
                textcoords="offset points", fontsize=8)
ax.set(xlabel="Estimated API cost per task (US cents)",
       ylabel="Hidden correctness (%)", xlim=(.35, 1.07), ylim=(15, 90))
ax.grid(alpha=.2)
fig.tight_layout(pad=.6)
for variant in ("ieee_conference", "ieee_access"):
    fig.savefig(ROOT / variant / "figures/cost_tradeoff.pdf", bbox_inches="tight")
plt.close(fig)
