#!/usr/bin/env python3
"""Build the OpenAI observed-use IWA validation appendix assets.

The analysis compares public U.S. ChatGPT message shares by O*NET
intermediate work activity with U.S.-conditioned Atlas task labels
aggregated to the same IWA codes.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy.stats import spearmanr


PKG_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_LABELS = PKG_ROOT / "data_intermediate/task_country_labels_analysis.parquet"
DEFAULT_HIERARCHY = PKG_ROOT / "outputs/source_data/openai_observed_use/onet_task_hierarchy.csv"
DEFAULT_WORK_SIGNALS = (
    PKG_ROOT
    / "outputs/source_data/openai_observed_use/"
    / "usa_share_of_work_related_messages_by_onet_iwa_month.csv"
)
DEFAULT_ALL_SIGNALS = (
    PKG_ROOT
    / "outputs/source_data/openai_observed_use/"
    / "usa_share_of_messages_by_onet_iwa_month.csv"
)
DEFAULT_OUT = PKG_ROOT / "reproduced"


PALETTE = {
    "blue": "#0F4D92",
    "blue_soft": "#8FB7DE",
    "red": "#B64342",
    "red_soft": "#E9A6A1",
    "neutral_light": "#D8D8D8",
    "neutral_mid": "#8F8F8F",
    "neutral_dark": "#4D4D4D",
    "black": "#272727",
}


CHANNEL_ORDER = [
    "info_exposed",
    "workflow_exposed",
    "planning_exposed",
    "inference_exposed",
    "physical_exposed",
    "economic_exposed",
]

AI_FUNCTION_ORDER = [
    "ai_material_exposed",
    "content_transform_ai",
    "recommendation_decision_ai",
    "state_inference_ai",
    "adaptive_control_ai",
]

SUMMARY_ORDER = [
    "info_exposed",
    "content_transform_ai",
    "ai_material_exposed",
    "economic_exposed",
    "physical_exposed",
]

TABLE_METRIC_ORDER = CHANNEL_ORDER + AI_FUNCTION_ORDER

CHANNEL_PANEL_LABELS = {
    "info_exposed": "Information transformation",
    "workflow_exposed": "Rule-based workflow",
    "planning_exposed": "Planning/control",
    "inference_exposed": "Inference/scoring",
    "physical_exposed": "Physical execution",
    "economic_exposed": "Broad exposure",
}

AI_PANEL_LABELS = {
    "ai_material_exposed": "AI-material share",
    "content_transform_ai": "Content transformation",
    "recommendation_decision_ai": "Recommendation/decision",
    "state_inference_ai": "State inference",
    "adaptive_control_ai": "Adaptive control",
}

SUMMARY_PANEL_LABELS = {
    "info_exposed": "Information\ntransformation",
    "content_transform_ai": "Content\ntransformation",
    "ai_material_exposed": "AI-material\nshare",
    "economic_exposed": "Broad\nexposure",
    "physical_exposed": "Physical\nexecution",
}

TABLE_METRIC_LABELS = {
    "info_exposed": "Information transformation",
    "workflow_exposed": "Rule-based workflow",
    "planning_exposed": "Planning/control",
    "inference_exposed": "Inference/scoring",
    "physical_exposed": "Physical execution",
    "economic_exposed": "Broad economic exposure",
    "ai_material_exposed": "AI-material exposed share",
    "content_transform_ai": "Content transformation",
    "recommendation_decision_ai": "Recommendation/decision",
    "state_inference_ai": "State inference",
    "adaptive_control_ai": "Adaptive control",
}

GROUP_BY_METRIC = {
    **{metric: "channel" for metric in CHANNEL_ORDER},
    **{metric: "ai_function" for metric in AI_FUNCTION_ORDER},
    "economic_exposed": "aggregate",
    "ai_material_exposed": "ai_aggregate",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--hierarchy", type=Path, default=DEFAULT_HIERARCHY)
    parser.add_argument("--work-signals", type=Path, default=DEFAULT_WORK_SIGNALS)
    parser.add_argument("--all-signals", type=Path, default=DEFAULT_ALL_SIGNALS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def apply_publication_style() -> None:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    mpl.rcParams.update(
        {
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "legend.frameon": False,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
        }
    )


def add_panel_label(ax: plt.Axes, label: str, x: float = -0.12, y: float = 1.03) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        fontsize=8,
        fontweight="bold",
        ha="left",
        va="bottom",
        color=PALETTE["black"],
    )


def ensure_dirs(out_dir: Path) -> dict[str, Path]:
    dirs = {
        "data": out_dir / "data",
        "figures": out_dir / "figures",
        "tables": out_dir / "tables",
        "notes": out_dir / "notes",
    }
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)
    return dirs


def load_usa_labels(path: Path) -> pd.DataFrame:
    cols = [
        "task_id",
        "iso3",
        "exposure_level",
        "economic_exposed",
        "dominant_channel",
        "sub_only_share",
        "both_share",
        "aug_only_share",
        "ai_material_share",
        "dominant_ai_function",
    ]
    labels = pq.read_table(path, columns=cols).to_pandas()
    labels = labels.loc[labels["iso3"] == "USA"].copy()
    labels["task_id"] = labels["task_id"].astype(str)
    labels["economic_exposed"] = labels["economic_exposed"].astype(float)
    labels["exposure_level"] = labels["exposure_level"].astype(float)
    labels["ai_material_share"] = labels["ai_material_share"].astype(float)

    labels["ai_material_exposed"] = labels["economic_exposed"] * labels["ai_material_share"]
    labels["info_exposed"] = labels["economic_exposed"] * (
        labels["dominant_channel"] == "informational_transformation"
    ).astype(float)
    labels["workflow_exposed"] = labels["economic_exposed"] * (
        labels["dominant_channel"] == "rule_based_workflow"
    ).astype(float)
    labels["planning_exposed"] = labels["economic_exposed"] * (
        labels["dominant_channel"] == "planning_control"
    ).astype(float)
    labels["inference_exposed"] = labels["economic_exposed"] * (
        labels["dominant_channel"] == "inference_scoring"
    ).astype(float)
    labels["physical_exposed"] = labels["economic_exposed"] * (
        labels["dominant_channel"] == "physical_execution"
    ).astype(float)
    labels["content_transform_ai"] = labels["economic_exposed"] * (
        labels["dominant_ai_function"] == "learned_content_transformation"
    ).astype(float)
    labels["recommendation_decision_ai"] = labels["economic_exposed"] * (
        labels["dominant_ai_function"] == "learned_recommendation_decision"
    ).astype(float)
    labels["state_inference_ai"] = labels["economic_exposed"] * (
        labels["dominant_ai_function"] == "learned_state_inference"
    ).astype(float)
    labels["adaptive_control_ai"] = labels["economic_exposed"] * (
        labels["dominant_ai_function"] == "learned_adaptive_control"
    ).astype(float)
    return labels


def load_hierarchy(path: Path) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row["task_id"], row["iwa_id"])
            if key in seen:
                continue
            seen.add(key)
            try:
                segments = json.loads(row["path_segments"])
            except json.JSONDecodeError:
                segments = []
            rows.append(
                {
                    "task_id": row["task_id"],
                    "iwa_id": row["iwa_id"],
                    "iwa_label": segments[1] if len(segments) > 1 else row["iwa_id"],
                    "gwa_label": segments[0] if segments else "",
                }
            )
    return pd.DataFrame(rows)


def load_signals(path: Path, prefix: str) -> pd.DataFrame:
    signals = pd.read_csv(path)
    signals = signals.loc[signals["iwa_cleaned"] != "Other IWA"].copy()
    signals["month"] = pd.to_datetime(signals["month"])

    q2 = (
        signals.loc[(signals["month"] >= "2026-04-01") & (signals["month"] <= "2026-06-01")]
        .groupby("iwa_cleaned", as_index=False)["share_of_messages"]
        .mean()
        .rename(columns={"share_of_messages": f"{prefix}_q2_2026"})
    )
    latest_month = signals["month"].max()
    latest = signals.loc[signals["month"] == latest_month, ["iwa_cleaned", "share_of_messages"]].rename(
        columns={"share_of_messages": f"{prefix}_jun_2026"}
    )
    full = (
        signals.groupby("iwa_cleaned", as_index=False)["share_of_messages"]
        .mean()
        .rename(columns={"share_of_messages": f"{prefix}_mean_202407_202606"})
    )
    return q2.merge(latest, on="iwa_cleaned").merge(full, on="iwa_cleaned")


def build_iwa_panel(labels: pd.DataFrame, hierarchy: pd.DataFrame, work: pd.DataFrame, all_messages: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "economic_exposed",
        "exposure_level",
        "ai_material_exposed",
        "info_exposed",
        "workflow_exposed",
        "planning_exposed",
        "inference_exposed",
        "physical_exposed",
        "content_transform_ai",
        "recommendation_decision_ai",
        "state_inference_ai",
        "adaptive_control_ai",
        "sub_only_share",
        "both_share",
        "aug_only_share",
    ]
    merged = hierarchy.merge(labels, on="task_id", how="inner")
    iwa = (
        merged.groupby(["iwa_id", "iwa_label", "gwa_label"], as_index=False)
        .agg(n_task_edges=("task_id", "nunique"), **{metric: (metric, "mean") for metric in metrics})
        .sort_values("iwa_id")
    )
    panel = work.merge(all_messages, on="iwa_cleaned", how="inner").merge(
        iwa, left_on="iwa_cleaned", right_on="iwa_id", how="inner"
    )
    panel["work_q2_2026_per_task_edge"] = panel["work_q2_2026"] / panel["n_task_edges"]

    eps = 1e-8
    panel["log_work_q2_2026"] = np.log(panel["work_q2_2026"] + eps)
    panel["log_n_task_edges"] = np.log(panel["n_task_edges"])
    x = np.vstack([np.ones(len(panel)), panel["log_n_task_edges"].to_numpy()]).T
    beta = np.linalg.lstsq(x, panel["log_work_q2_2026"].to_numpy(), rcond=None)[0]
    panel["work_q2_2026_resid_log_task_edges"] = panel["log_work_q2_2026"] - x.dot(beta)
    return panel


def spearman_table(panel: pd.DataFrame) -> pd.DataFrame:
    outcomes = {
        "work_q2_2026": "Work Q2",
        "work_jun_2026": "Work June",
        "work_mean_202407_202606": "Work full",
        "work_q2_2026_per_task_edge": "Per edge",
        "work_q2_2026_resid_log_task_edges": "Residual",
        "all_q2_2026": "All Q2",
    }
    rows = []
    for metric in TABLE_METRIC_ORDER:
        for outcome, outcome_label in outcomes.items():
            subset = panel[[metric, outcome]].dropna()
            rho, p_value = spearmanr(subset[metric], subset[outcome])
            rows.append(
                {
                    "atlas_measure": metric,
                    "atlas_measure_label": TABLE_METRIC_LABELS[metric],
                    "outcome": outcome,
                    "outcome_label": outcome_label,
                    "spearman_rho": rho,
                    "p_value": p_value,
                    "n_iwa": len(subset),
                }
            )
    return pd.DataFrame(rows)


def write_latex_table(corr: pd.DataFrame, path: Path) -> None:
    table = corr.pivot(index=["atlas_measure", "atlas_measure_label"], columns="outcome_label", values="spearman_rho")
    table = table.reset_index().set_index("atlas_measure")
    table = table.loc[TABLE_METRIC_ORDER]
    cols = ["Work Q2", "Work June", "Work full", "Per edge", "Residual", "All Q2"]

    lines = [
        r"\begin{table}[!htbp]",
        r"\centering",
        r"\footnotesize",
        r"\caption{Robustness of observed-use correlations across U.S. work activities.}",
        r"\label{tab:appendix_openai_observed_use_iwa_robustness}",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Atlas measure & Work Q2 & Work June & Work full & Per edge & Residual & All Q2 \\",
        r"\midrule",
    ]
    for metric in TABLE_METRIC_ORDER:
        row = table.loc[metric]
        vals = " & ".join(f"{row[col]:.3f}" for col in cols)
        lines.append(f"{TABLE_METRIC_LABELS[metric]} & {vals} " + r"\\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption*{\scriptsize Notes: Entries are Spearman rank correlations across 164 named O*NET intermediate work activities. The primary outcome is the OpenAI public work-related U.S. message share averaged over April--June 2026. The June 2026 column uses the latest public month. The full-period column averages July 2024--June 2026. The per-task-edge column divides the 2026 Q2 work-related message share by the number of Atlas task edges in the IWA. The residual column uses residual log message share after projecting log work-related message share on log task-edge count. The all-message column uses the OpenAI public all-message IWA series rather than the work-related series. Atlas measures are built from U.S.-conditioned task labels. Channel rows are exposed task shares whose dominant channel is the named channel. AI-function rows are exposed task shares whose dominant AI function is the named function. Broad economic exposure and AI-material exposed share are aggregate measures rather than channels or AI functions.}",
            r"\end{table}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def wrapped_label(label: str, width: int = 18) -> str:
    return "\n".join(textwrap.wrap(label.rstrip("."), width=width))


def plot_figure(panel: pd.DataFrame, corr: pd.DataFrame, out_base: Path) -> None:
    apply_publication_style()
    fig = plt.figure(figsize=(8.25, 5.15))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.04, 1.0], width_ratios=[1.0, 1.14], hspace=0.42, wspace=0.55)

    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    work_corr = corr.loc[corr["outcome"] == "work_q2_2026"].set_index("atlas_measure")

    def label_offset(value: float) -> tuple[float, str]:
        if value < 0:
            return 0.016, "left"
        return 0.016, "left"

    def metric_color(metric: str, value: float) -> str:
        if value < 0:
            return PALETTE["red"]
        if metric == "economic_exposed":
            return PALETTE["neutral_mid"]
        if metric == "ai_material_exposed":
            return "#3D7DBB"
        return PALETTE["blue"]

    def draw_lollipop(
        ax: plt.Axes,
        metrics: list[str],
        labels: dict[str, str],
        panel_letter: str,
        title: str,
        separator_after,
    ) -> None:
        values = work_corr.loc[metrics, "spearman_rho"]
        y = np.arange(len(metrics))
        ax.axvline(0, color=PALETTE["neutral_mid"], lw=0.8, zorder=1)
        if separator_after is not None:
            ax.axhline(separator_after, color=PALETTE["neutral_light"], lw=0.8, ls=(0, (2, 2)), zorder=0)
        for yi, metric, value in zip(y, metrics, values):
            color = metric_color(metric, float(value))
            ax.plot([0, value], [yi, yi], color=color, lw=1.85, solid_capstyle="round", zorder=2)
            ax.scatter(value, yi, s=34, color=color, edgecolor="white", linewidth=0.7, zorder=3)
            offset, ha = label_offset(float(value))
            ax.text(
                value + offset,
                yi,
                f"{value:.3f}",
                ha=ha,
                va="center",
                fontsize=6.2,
                color=PALETTE["black"],
                bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.15},
            )
        ax.set_yticks(y)
        ax.set_yticklabels([labels[metric] for metric in metrics], fontsize=6.5)
        ax.invert_yaxis()
        ax.set_xlim(-0.37, 0.52)
        ax.set_xlabel("Spearman correlation")
        ax.grid(axis="x", color=PALETTE["neutral_light"], lw=0.5, alpha=0.75)
        ax.set_title(f"{panel_letter}. {title}", loc="left", fontsize=7.6, pad=5)
        ax.tick_params(axis="y", pad=3)

    draw_lollipop(ax_a, CHANNEL_ORDER, CHANNEL_PANEL_LABELS, "a", "Channel measures", separator_after=4.5)

    draw_lollipop(ax_b, AI_FUNCTION_ORDER, AI_PANEL_LABELS, "b", "AI-material and AI-function measures", separator_after=0.5)

    scatter = panel.copy()
    ax_c.scatter(
        scatter["info_exposed"],
        100 * scatter["work_q2_2026"],
        s=np.clip(scatter["n_task_edges"], 10, 180) * 0.20,
        color=PALETTE["blue_soft"],
        edgecolor="white",
        linewidth=0.45,
        alpha=0.78,
    )
    ax_c.set_xlabel("Information-transformation exposure")
    ax_c.set_ylabel("Work-related message share (%)")
    ax_c.set_xlim(-0.03, 1.05)
    ax_c.set_ylim(-0.3, 13.8)
    ax_c.grid(color=PALETTE["neutral_light"], lw=0.5, alpha=0.65)
    anchor_labels = {
        "4.A.2.b.1.I07": ("Edit written\nmaterials", (0.62, 13.0), "left"),
        "4.A.3.b.6.I12": ("Prepare informational\nor instructional\nmaterials", (0.47, 9.6), "left"),
        "4.A.2.b.2.I12": ("Develop marketing\nmaterials", (0.62, 5.7), "left"),
        "4.A.2.b.2.I18": ("Create visual\ndesigns", (0.70, 3.0), "left"),
        "4.A.1.a.1.I04": ("Gather information", (0.44, 4.5), "left"),
    }
    anchors = scatter.loc[scatter["iwa_id"].isin(anchor_labels)].copy()
    for _, row in anchors.iterrows():
        label, (text_x, text_y), ha = anchor_labels[row["iwa_id"]]
        ax_c.annotate(
            label,
            xy=(row["info_exposed"], 100 * row["work_q2_2026"]),
            xytext=(text_x, text_y),
            textcoords="data",
            fontsize=5.6,
            ha=ha,
            va="center",
            color=PALETTE["neutral_dark"],
            arrowprops={"arrowstyle": "-", "lw": 0.35, "color": PALETTE["neutral_mid"], "shrinkA": 0, "shrinkB": 2},
        )
    ax_c.set_title("c. High-use activities concentrate in information work", loc="left", fontsize=7.6, pad=5)

    comp = (
        corr.loc[corr["outcome"].isin(["work_q2_2026", "all_q2_2026"])]
        .pivot(index="atlas_measure", columns="outcome", values="spearman_rho")
        .loc[SUMMARY_ORDER]
    )
    y2 = np.arange(len(comp))
    ax_d.axvline(0, color=PALETTE["neutral_mid"], lw=0.8, zorder=1)
    for yi, metric in zip(y2, SUMMARY_ORDER):
        ax_d.plot(
            [comp.loc[metric, "all_q2_2026"], comp.loc[metric, "work_q2_2026"]],
            [yi, yi],
            color=PALETTE["neutral_light"],
            lw=1.0,
            zorder=2,
        )
    ax_d.scatter(comp["all_q2_2026"], y2, s=28, color=PALETTE["neutral_mid"], label="All messages", zorder=3)
    ax_d.scatter(comp["work_q2_2026"], y2, s=32, color=PALETTE["blue"], label="Work-related messages", zorder=3)
    ax_d.set_yticks(y2)
    ax_d.set_yticklabels([SUMMARY_PANEL_LABELS[metric] for metric in SUMMARY_ORDER], fontsize=6.5)
    ax_d.invert_yaxis()
    ax_d.set_xlim(-0.36, 0.50)
    ax_d.set_xlabel("Spearman correlation")
    ax_d.grid(axis="x", color=PALETTE["neutral_light"], lw=0.5, alpha=0.7)
    ax_d.tick_params(axis="y", pad=3)
    ax_d.legend(loc="lower right", fontsize=5.8)
    ax_d.set_title("d. Alignment is weaker for all messages", loc="left", fontsize=7.6, pad=5)

    fig.savefig(f"{out_base}.svg", bbox_inches="tight")
    fig.savefig(f"{out_base}.pdf", bbox_inches="tight")
    fig.savefig(f"{out_base}.tiff", dpi=600, bbox_inches="tight")
    fig.savefig(f"{out_base}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_contract(path: Path) -> None:
    text = """Core conclusion:
Observed U.S. work-related ChatGPT use is most closely associated with Atlas information-transformation and AI content-transformation measures, while other channels and AI functions reveal where public ChatGPT message shares are not a general adoption proxy.

Figure archetype:
Quantitative grid.

Target journal/output:
Nature-style supplementary figure; Python backend; SVG, PDF, TIFF, and PNG exports.

Final size:
Double-column supplementary layout, 8.25 x 5.15 inches.

Panel map:
  a: Spearman correlations between work-related message share and Atlas channel measures, with broad exposure separated as an aggregate.
  b: Spearman correlations between work-related message share and AI-material / AI-function measures.
  c: Scatter of information-transformation exposure against work-related message share.
  d: Selected correlations for work-related versus all messages.

Evidence hierarchy:
  hero evidence: Panels a and b.
  validation evidence: Panel c.
  controls/robustness: Panel d and the companion robustness table.

Statistics needed:
Spearman rank correlations across 164 named O*NET IWA categories using OpenAI Signals v2.0 through June 2026.

Source data needed:
OpenAI public U.S. IWA message-share files, Atlas U.S.-conditioned task labels, and O*NET task-to-IWA hierarchy.

Image-integrity notes:
All panels are vector plots derived from tabular source data. No raster image manipulation.

Reviewer risk:
The OpenAI outcome is a message share, not an adoption rate, task frequency, employment exposure measure, or global work-activity measure.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    dirs = ensure_dirs(args.out_dir)

    labels = load_usa_labels(args.labels)
    hierarchy = load_hierarchy(args.hierarchy)
    work = load_signals(args.work_signals, "work")
    all_messages = load_signals(args.all_signals, "all")
    panel = build_iwa_panel(labels, hierarchy, work, all_messages)
    corr = spearman_table(panel)

    panel.to_csv(dirs["data"] / "openai_observed_use_iwa_atlas_panel.csv", index=False)
    corr.to_csv(dirs["data"] / "openai_observed_use_iwa_correlations.csv", index=False)
    write_latex_table(corr, dirs["tables"] / "tab_appendix_openai_observed_use_iwa_robustness.tex")
    plot_figure(panel, corr, dirs["figures"] / "fig_openai_observed_use_iwa_alignment")
    write_contract(dirs["notes"] / "fig_openai_observed_use_iwa_contract.md")

    matched_share = panel["work_q2_2026"].sum()
    print(f"Matched named IWAs: {len(panel)}")
    print(f"Matched Q2 2026 work-related message share: {matched_share:.4f}")
    print(f"Wrote outputs under: {args.out_dir}")


if __name__ == "__main__":
    main()
