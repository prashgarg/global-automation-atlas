#!/usr/bin/env python3
"""Combined 6-panel main figure: RF covariate SHAP (a-c) over rationale pooled families (d-f).

Top row  a/b/c : mean absolute TreeSHAP for exposed share / substitution-only / augmentation-only
                 (68-country RF), bar colour = one-dimensional ALE local direction.
Bottom row d/e/f : pooled rationale-concept families for the same three contrasts, points =
                 heldout signed difference (pp) with 95% CI, colour/marker = condition class.

Single Nature-style canvas, editable text (pdf.fonttype 42), ~180 mm full width.
"""
from __future__ import annotations

import csv
import os
import sys
import textwrap
import types
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-codex")

# Homebrew python plistlib/pyexpat shim used by the existing panel script.
_stub = types.ModuleType("plistlib")
_stub.load = lambda *a, **k: {"_items": []}
_stub.loads = lambda *a, **k: [{"_items": []}]
_stub.InvalidFileException = ValueError
sys.modules.setdefault("plistlib", _stub)

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

PKG_ROOT = Path(__file__).resolve().parents[2]
SHAP_CSV = PKG_ROOT / "outputs/source_data/country_predictors/country_covariate_rf_mean_abs_shap.csv"
RAT_CSV = (
    PKG_ROOT
    / "outputs/source_data/rationale_concepts/current_paper"
    / "rf_companion_rationale_panel_source.csv"
)
OUTDIR = PKG_ROOT / "reproduced/figures"

TEXT = "#172232"
MUTED = "#627284"
GRID = "#e8eef5"
ZERO = "#a8b4c2"

# --- top row (RF): ALE local direction ---
DIR_COLORS = {"positive": "#5B84B1", "negative": "#C46C3A", "mixed": "#8C95A1"}
FEATURE_LABELS = {
    "log_gdp_per_capita": "Log GDP per capita",
    "pwt_human_capital_index": "Human capital",
    "barro_lee_years_schooling_15_64": "Years of schooling",
    "pwt_log_real_capital_stock_per_worker": "Capital intensity",
    "gross_fixed_capital_formation_pct_gdp": "Investment (% GDP)",
    "wgi_government_effectiveness_score": "Government effectiveness",
    "wgi_regulatory_quality_score": "Regulatory quality",
    "internet_users_pct": "Internet users (%)",
    "goods_trade_openness": "Goods trade (% GDP)",
}
TOP = [
    {"outcome": "share_exposed", "letter": "a", "title": "Exposed share", "sub": "across all tasks"},
    {"outcome": "substitution_within_exposed", "letter": "b", "title": "Substitution-only", "sub": "within exposed tasks"},
    {"outcome": "augmentation_within_exposed", "letter": "c", "title": "Augmentation-only", "sub": "within exposed tasks"},
]

# --- bottom row (rationale): condition class ---
CLASS_COLORS = {
    "Country context": "#2B75B8",
    "Task-specific": "#D98A19",
    "Country/task interaction": "#139B7D",
    "Mixed/unclear": "#5C6673",
    "Mixed": "#5C6673",
}
CLASS_MARKERS = {
    "Country context": "o",
    "Task-specific": "^",
    "Country/task interaction": "D",
    "Mixed/unclear": "s",
    "Mixed": "s",
}
CLASS_DISPLAY = {
    "Country context": "Country context",
    "Task-specific": "Task-specific",
    "Country/task interaction": "Country/task interaction",
    "Mixed/unclear": "Mixed/ambiguous",
    "Mixed": "Mixed/ambiguous",
}
BOT = {
    "d": {"title": "Exposure", "sub": "Non-exposed (-); exposed (+)", "xlabel": "Exposed minus non-exposed (pp)", "xlim": (-60, 60), "xticks": range(-60, 61, 20)},
    "e": {"title": "Substitution", "sub": "Other exposed (-); substitution (+)", "xlabel": "Substitution-only minus other exposed (pp)", "xlim": (-37, 12)},
    "f": {"title": "Augmentation", "sub": "Other exposed (-); augmentation (+)", "xlabel": "Augmentation-only minus other exposed (pp)", "xlim": (-6, 21)},
}


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def setup():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "font.size": 7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
    })


def read_shap():
    by_out = {t["outcome"]: [] for t in TOP}
    with open(SHAP_CSV, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["spec"] != "main68" or r["outcome"] not in by_out:
                continue
            by_out[r["outcome"]].append({
                "variable": r["variable"],
                "shap": f(r["mean_abs_shap"]) * 100.0,
                "ci": f(r["mean_abs_shap_ci"]) * 100.0,
                "dir": r["direction_flag"],
            })
    for k in by_out:
        by_out[k].sort(key=lambda d: d["shap"])  # ascending -> largest on top
    return by_out


def read_rat():
    by_panel = {"d": [], "e": [], "f": []}
    with open(RAT_CSV, newline="") as fh:
        for r in csv.DictReader(fh):
            p = r["panel"]
            if p not in by_panel:
                continue
            by_panel[p].append({
                "label": r["display_label"],
                "eff": f(r["family_effect_pp"]),
                "lo": f(r["family_ci_low_pp"]),
                "hi": f(r["family_ci_high_pp"]),
                "cls": r["condition_class"],
            })
    for k in by_panel:
        by_panel[k].sort(key=lambda d: d["eff"])  # ascending
    return by_panel


def draw_bars(ax, rows, spec, xlim):
    y = range(len(rows))
    ax.axvline(0, color=ZERO, lw=0.9, zorder=0)
    ax.grid(axis="x", color=GRID, lw=0.55, zorder=0)
    ax.set_axisbelow(True)
    for i, r in enumerate(rows):
        color = DIR_COLORS.get(r["dir"], "#8C95A1")
        ax.barh(i, r["shap"], height=0.66, color=color, edgecolor="none", alpha=0.95, zorder=2)
        ax.errorbar(r["shap"], i, xerr=r["ci"], fmt="none", ecolor=TEXT, elinewidth=0.7, capsize=1.6, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels([FEATURE_LABELS.get(r["variable"], r["variable"]) for r in rows], fontsize=6.0, color=TEXT)
    ax.tick_params(axis="y", length=0, pad=2.0)
    ax.tick_params(axis="x", labelsize=5.9, colors=TEXT, pad=1.5)
    ax.set_xlim(*xlim)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#a7b3c0")
    ax.set_title(f"{spec['letter']}  {spec['title']}", loc="left", fontsize=7.4, fontweight="bold", color=TEXT, pad=12)
    ax.text(0.0, 1.03, spec["sub"], transform=ax.transAxes, ha="left", va="bottom", fontsize=5.7, color=MUTED)
    ax.set_xlabel("Mean absolute SHAP (pp)", fontsize=5.8, color=TEXT, labelpad=3)


def wrap(label, width=24):
    if "\n" in label:
        return label
    return "\n".join(textwrap.wrap(label, width=width, break_long_words=False))


def draw_forest(ax, rows, letter, spec):
    if letter == "d" and any(r["lo"] < spec["xlim"][0] or r["hi"] > spec["xlim"][1] for r in rows):
        raise RuntimeError("Exposure family CI falls outside the configured x-axis limits")
    ax.axvline(0, color=ZERO, lw=0.9, zorder=0)
    ax.grid(axis="x", color=GRID, lw=0.55, zorder=0)
    ax.set_axisbelow(True)
    for i, r in enumerate(rows):
        color = CLASS_COLORS.get(r["cls"], "#5C6673")
        marker = CLASS_MARKERS.get(r["cls"], "s")
        ax.plot([r["lo"], r["hi"]], [i, i], color=color, lw=1.15, alpha=0.78, zorder=2)
        ax.scatter(r["eff"], i, s=32, marker=marker, color=color, edgecolor=TEXT, lw=0.38, zorder=3)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([wrap(r["label"]) for r in rows], fontsize=5.9, color=TEXT)
    ax.tick_params(axis="y", length=0, pad=2.5)
    ax.tick_params(axis="x", labelsize=5.9, colors=TEXT, pad=1.5)
    ax.set_xlim(*spec["xlim"])
    if "xticks" in spec:
        ax.set_xticks(list(spec["xticks"]))
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#a7b3c0")
    ax.set_title(f"{letter}  {spec['title']}", loc="left", fontsize=7.4, fontweight="bold", color=TEXT, pad=12)
    ax.text(0.0, 1.03, spec["sub"], transform=ax.transAxes, ha="left", va="bottom", fontsize=5.7, color=MUTED)
    ax.set_xlabel(spec["xlabel"], fontsize=5.8, color=TEXT, labelpad=3)


def main():
    setup()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    shap = read_shap()
    rat = read_rat()

    # shared x-axis for top panels b & c (matches the *_bc_common_axis figure)
    a_max = max(r["shap"] + r["ci"] for r in shap["share_exposed"]) * 1.12
    bc_max = max(r["shap"] + r["ci"] for o in ("substitution_within_exposed", "augmentation_within_exposed") for r in shap[o]) * 1.12
    top_xlims = {"share_exposed": (0, a_max), "substitution_within_exposed": (0, bc_max), "augmentation_within_exposed": (0, bc_max)}

    fig = plt.figure(figsize=(7.1, 6.0))
    gs = GridSpec(2, 3, figure=fig, height_ratios=[1.0, 0.90],
                  left=0.165, right=0.985, top=0.945, bottom=0.105, wspace=0.62, hspace=0.34)

    for j, spec in enumerate(TOP):
        ax = fig.add_subplot(gs[0, j])
        draw_bars(ax, shap[spec["outcome"]], spec, top_xlims[spec["outcome"]])

    for j, letter in enumerate(["d", "e", "f"]):
        ax = fig.add_subplot(gs[1, j])
        draw_forest(ax, rat[letter], letter, BOT[letter])

    # two row-legends
    dir_handles = [Line2D([0], [0], marker="s", color=DIR_COLORS[k], lw=0, markersize=4.6,
                          markeredgecolor=TEXT, markeredgewidth=0.3,
                          label=f"{k.capitalize()} local direction") for k in ("positive", "negative", "mixed")]
    leg1 = fig.legend(handles=dir_handles, loc="upper center", bbox_to_anchor=(0.55, 0.515),
                      ncol=3, frameon=False, fontsize=5.7, handletextpad=0.4, columnspacing=1.1)
    for t in leg1.get_texts():
        t.set_color(TEXT)

    order = ["Country context", "Task-specific", "Country/task interaction", "Mixed/unclear"]
    cls_handles = [Line2D([0], [0], marker=CLASS_MARKERS[k], color=CLASS_COLORS[k], lw=0, markersize=4.9,
                          markeredgecolor=TEXT, markeredgewidth=0.38, label=CLASS_DISPLAY[k]) for k in order]
    leg2 = fig.legend(handles=cls_handles, loc="lower center", bbox_to_anchor=(0.55, 0.012),
                      ncol=4, frameon=False, fontsize=5.7, handletextpad=0.45, columnspacing=1.05)
    for t in leg2.get_texts():
        t.set_color(TEXT)

    stem = OUTDIR / "fig_country_context_rf_rationale_combined"
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".png"), dpi=450)
    plt.close(fig)
    print("WROTE", stem.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
