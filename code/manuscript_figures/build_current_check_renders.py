#!/usr/bin/env python3
"""Build current source-data check renders from released package inputs.

These plots verify the numerical content and direction rules of current paper
figures. They are not asserted to be pixel-identical to manuscript artwork.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-atlas-replication")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PKG_ROOT = Path(__file__).resolve().parents[2]
OUT = PKG_ROOT / "reproduced/figures"
CHECKS = PKG_ROOT / "reproduced/checks"

TEXT = "#172232"
GRID = "#E5EBF1"
BLUE = "#4F7EA8"
ORANGE = "#C8753D"
TEAL = "#31867A"
GREY = "#7C8793"

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

OUTCOME_LABELS = {
    "share_exposed": "Exposed share",
    "substitution_within_exposed": "Substitution-only within exposed",
    "augmentation_within_exposed": "Augmentation-only within exposed",
}


def setup() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CHECKS.mkdir(parents=True, exist_ok=True)
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def build_shap_ale() -> None:
    path = PKG_ROOT / "outputs/source_data/country_predictors/country_covariate_rf_mean_abs_shap.csv"
    data = pd.read_csv(path)
    outcomes = list(OUTCOME_LABELS)
    data = data[(data["spec"] == "main68") & data["outcome"].isin(outcomes)].copy()
    if len(data) != 27:
        raise RuntimeError(f"Expected 27 main68 SHAP rows, found {len(data)}")

    data["direction_from_five_seed_rule"] = np.where(
        data["positive_ale_share"] >= 0.8,
        "positive",
        np.where(data["negative_ale_share"] >= 0.8, "negative", "mixed"),
    )
    data["direction_rule_match"] = (
        data["direction_from_five_seed_rule"] == data["direction_flag"]
    )
    data.to_csv(CHECKS / "shap_ale_five_seed_direction_check.csv", index=False)
    if not data["direction_rule_match"].all():
        bad = data.loc[~data["direction_rule_match"], ["outcome", "variable"]]
        raise RuntimeError(f"Five-seed ALE direction mismatch:\n{bad.to_string(index=False)}")

    colors = {"positive": BLUE, "negative": ORANGE, "mixed": GREY}
    fig, axes = plt.subplots(1, 3, figsize=(8.8, 4.7))
    for ax, outcome in zip(axes, outcomes):
        sub = data[data["outcome"] == outcome].sort_values("mean_abs_shap")
        y = np.arange(len(sub))
        ax.barh(
            y,
            100 * sub["mean_abs_shap"],
            xerr=100 * sub["mean_abs_shap_ci"],
            color=[colors[x] for x in sub["direction_flag"]],
            edgecolor="none",
            error_kw={"ecolor": TEXT, "elinewidth": 0.7, "capsize": 1.5},
        )
        ax.set_yticks(y, [FEATURE_LABELS.get(x, x) for x in sub["variable"]], fontsize=6)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)
        ax.set_title(OUTCOME_LABELS[outcome], loc="left", weight="bold", fontsize=8)
        ax.set_xlabel("Mean absolute TreeSHAP (pp)", fontsize=7)
    fig.tight_layout(w_pad=1.4)
    fig.savefig(OUT / "fig_country_context_rf_shap_check.pdf")
    plt.close(fig)


def gender_summary(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    fields = {
        "Overall exposure": "exposed_gap_pp",
        "Substitution-only": "sub_gap_pp",
        "Both margins": "both_gap_pp",
        "Augmentation-only": "aug_gap_pp",
    }
    rows = []
    for label, field in fields.items():
        values = data[field].dropna()
        rows.append(
            {
                "margin": label,
                "median": values.median(),
                "q25": values.quantile(0.25),
                "q75": values.quantile(0.75),
                "n": len(values),
            }
        )
    return pd.DataFrame(rows)


def build_gender_informality() -> None:
    occ = gender_summary(PKG_ROOT / "data_analysis/occupation_isco2_gender_gap_country_panel.csv")
    ind = gender_summary(PKG_ROOT / "data_analysis/industry_isic2_gender_gap_country_panel.csv")
    inf = pd.read_csv(
        PKG_ROOT / "outputs/source_data/informality/informality_country_regressions.csv"
    ).copy()
    inf["estimate"] = 10 * inf["coefficient"]
    inf["lo"] = 10 * (inf["coefficient"] - 1.96 * inf["se"])
    inf["hi"] = 10 * (inf["coefficient"] + 1.96 * inf["se"])

    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.9))
    for ax, data, title in zip(axes[:2], [occ, ind], ["Occupation weights", "Industry weights"]):
        y = np.arange(len(data))[::-1]
        ax.hlines(y, data["q25"], data["q75"], color=GREY, linewidth=2)
        ax.scatter(data["median"], y, color=TEAL, s=22, zorder=3)
        ax.set_yticks(y, data["margin"], fontsize=7)
        ax.axvline(0, color=TEXT, linewidth=0.7)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.set_title(title, loc="left", weight="bold")
        ax.set_xlabel("Female minus male gap (pp); median and IQR")

    ax = axes[2]
    y = np.arange(len(inf))[::-1]
    ax.hlines(y, inf["lo"], inf["hi"], color=BLUE, linewidth=2)
    ax.scatter(inf["estimate"], y, color=TEAL, s=22, zorder=3)
    ax.set_yticks(y, inf["model"], fontsize=7)
    ax.axvline(0, color=TEXT, linewidth=0.7)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.set_title("Informality", loc="left", weight="bold")
    ax.set_xlabel("Coefficient per 10 pp higher informality; 95% CI")
    fig.tight_layout(w_pad=1.2)
    fig.savefig(OUT / "fig_gender_informality_margin_applications_rebuilt.pdf")
    plt.close(fig)


def build_gender_gap_decomposition() -> None:
    path = (
        PKG_ROOT
        / "outputs/source_data/ilostat_gender/gender_gap_decomposition_by_income.csv"
    )
    data = pd.read_csv(path)
    data = data[
        (data["support"] == "Figure 5 sex-specific support")
        & data["margin"].isin(["Substitution-only", "Augmentation-only"])
    ].copy()
    if len(data) != 16:
        raise RuntimeError(f"Expected 16 decomposition rows, found {len(data)}")
    additive_error = (
        data["mean_reference_profile_pp"]
        + data["mean_country_specific_pp"]
        - data["mean_total_gap_pp"]
    ).abs()
    if additive_error.max() > 1e-9:
        raise RuntimeError("Gender-gap decomposition does not add to the total gap")

    data.to_csv(CHECKS / "gender_gap_decomposition_source_check.csv", index=False)
    income_order = [
        "Low income",
        "Lower middle income",
        "Upper middle income",
        "High income",
    ]
    domains = ["Occupation (ISCO-2)", "Industry (ISIC-2)"]
    margins = ["Substitution-only", "Augmentation-only"]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.9), sharex=True)
    for i, domain in enumerate(domains):
        for j, margin in enumerate(margins):
            ax = axes[i, j]
            sub = (
                data[(data["domain"] == domain) & (data["margin"] == margin)]
                .set_index("income_level")
                .loc[income_order]
            )
            y = np.arange(len(income_order))
            ref = sub["mean_reference_profile_pp"].to_numpy()
            total = sub["mean_total_gap_pp"].to_numpy()
            lo = sub["total_ci_low"].to_numpy()
            hi = sub["total_ci_high"].to_numpy()
            ax.hlines(y, 0, ref, color=BLUE, linewidth=5)
            ax.hlines(y, ref, total, color=ORANGE, linewidth=5)
            ax.errorbar(
                total,
                y,
                xerr=np.vstack([total - lo, hi - total]),
                fmt="D",
                color=TEXT,
                ecolor=TEXT,
                markersize=3.2,
                linewidth=0.7,
                capsize=1.5,
                zorder=3,
            )
            ax.axvline(0, color=TEXT, linewidth=0.6)
            ax.grid(axis="x", color=GRID, linewidth=0.5)
            ax.set_axisbelow(True)
            ax.set_yticks(y, income_order if j == 0 else [], fontsize=6.5)
            ax.invert_yaxis()
            ax.set_title(
                f"{domain.replace(' (ISCO-2)', '').replace(' (ISIC-2)', '')}: {margin}",
                loc="left",
                weight="bold",
                fontsize=7.5,
            )
    fig.supxlabel("Mean female-minus-male exposure gap (percentage points)", fontsize=7)
    fig.tight_layout(w_pad=1.0, h_pad=1.1)
    fig.savefig(OUT / "fig_gender_gap_decomposition_rebuilt.pdf")
    plt.close(fig)


def save_check(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / f"{name}_rebuilt.pdf")
    plt.close(fig)


def build_extended_source_checks() -> None:
    country = pd.read_csv(
        PKG_ROOT / "outputs/source_data/country_map/country_map_figure_panel.csv"
    )

    # Country map numerical content, shown without the omitted cartographic geometry.
    top = country.nlargest(30, "share_exposed").sort_values("share_exposed")
    fig, ax = plt.subplots(figsize=(6.8, 5.4))
    ax.barh(top["iso3"], 100 * top["share_exposed"], color=BLUE)
    ax.set(xlabel="Economically exposed task share (%)", title="Country-map source-data check: top 30")
    save_check(fig, "fig3_map_share_exposed")

    labels = pd.read_parquet(
        PKG_ROOT / "data_intermediate/task_country_labels_analysis.parquet",
        columns=["exposure_level", "economic_exposed", "income_level"],
    )
    counts = labels["exposure_level"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.bar(counts.index.astype(str), counts.values, color=TEAL)
    ax.set(xlabel="Exposure level", ylabel="Task-country observations", title="Task-country exposure measures")
    save_check(fig, "fig_task_country_exposure_measures")

    bench = pd.read_csv(
        PKG_ROOT / "outputs/source_data/benchmark_ladder/country_benchmark_residual_summary.csv"
    )
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.scatter(bench["mean_resid_vs_income_group"], bench["mean_resid_vs_contextfree"], s=14, color=BLUE, alpha=0.75)
    ax.axhline(0, color=GREY, linewidth=0.6); ax.axvline(0, color=GREY, linewidth=0.6)
    ax.set(xlabel="Residual vs income-group benchmark", ylabel="Residual vs context-free benchmark", title="Benchmark ladder country deviations")
    save_check(fig, "fig_benchmark_ladder_country_deviation")

    divergence = pd.read_csv(
        PKG_ROOT / "outputs/source_data/country_conditioning_divergence/task_pair_results.csv"
    )
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.hist(divergence["cosine"].dropna(), bins=35, color=BLUE, alpha=0.8, label="Cosine")
    ax.hist(divergence["jaccard"].dropna(), bins=35, color=ORANGE, alpha=0.65, label="Jaccard")
    ax.set(xlabel="Same-task high/low-country rationale similarity", ylabel="Tasks", title="Country-conditioning divergence")
    ax.legend(frameon=False)
    save_check(fig, "fig_validation_country_conditioning_divergence")

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.9))
    axes[0].hist(labels["exposure_level"], bins=np.arange(-0.5, 4.6, 1), color=BLUE)
    axes[0].set(xlabel="Exposure level", ylabel="Observations", title="Exposure distribution")
    axes[1].bar(["Not exposed", "Exposed"], labels["economic_exposed"].value_counts().reindex([False, True]).values, color=[GREY, TEAL])
    axes[1].set(title="Economic exposure")
    save_check(fig, "fig_validation_distribution_overview")

    order = ["Low income", "Lower middle income", "Upper middle income", "High income"]
    arrays = [labels.loc[labels["income_level"] == x, "exposure_level"].to_numpy() for x in order]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.boxplot(arrays, tick_labels=["Low", "Lower middle", "Upper middle", "High"], showfliers=False)
    ax.set(ylabel="Exposure level", title="Exposure distribution by income group")
    save_check(fig, "fig_validation_distribution_by_income")
    del labels

    us = pd.read_csv(PKG_ROOT / "outputs/source_data/construct_validity/country_vs_us_movement.csv")
    fig, ax = plt.subplots(figsize=(5.6, 4.5))
    ax.scatter(us["pearson"], us["spearman"], s=15, color=BLUE, alpha=0.75)
    ax.plot([0, 1], [0, 1], color=GREY, linestyle="--", linewidth=0.7)
    ax.set(xlabel="Pearson correlation", ylabel="Spearman correlation", title="US versus external-country alignment")
    save_check(fig, "fig_validation_us_vs_external")

    contrib = pd.read_csv(PKG_ROOT / "outputs/source_data/construct_validity/aligned_by_scope.csv").set_index("scope")
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    im = ax.imshow(contrib.to_numpy(), aspect="auto", cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(np.arange(len(contrib.columns)), contrib.columns, rotation=35, ha="right", fontsize=6)
    ax.set_yticks(np.arange(len(contrib.index)), contrib.index, fontsize=7)
    ax.set_title("Country contribution / construct-alignment check")
    fig.colorbar(im, ax=ax, label="Correlation")
    save_check(fig, "fig_validation_country_contribution")

    arrays = [100 * country.loc[country["income_level"] == x, "share_exposed"].dropna().to_numpy() for x in order]
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.boxplot(arrays, tick_labels=["Low", "Lower middle", "Upper middle", "High"], showfliers=False)
    ax.set(ylabel="Exposed task share (%)", title="Within-income variability")
    save_check(fig, "fig_within_income_variability")

    transitions = pd.read_csv(
        PKG_ROOT / "outputs/source_data/income_group_pathways/income_group_pathway_transition_row_shares.csv"
    )
    matrix = transitions.set_index(["pair", "state"])[["non_exposed", "sub_only", "both", "aug_only"]]
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    im = ax.imshow(matrix.to_numpy(), aspect="auto", cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(np.arange(4), ["Non-exposed", "Sub-only", "Both", "Aug-only"], rotation=25, ha="right")
    ax.set_yticks(np.arange(len(matrix)), [f"{a}: {b}" for a, b in matrix.index], fontsize=5.5)
    fig.colorbar(im, ax=ax, label="Row share")
    ax.set_title("Income-group pathway transitions")
    save_check(fig, "fig_income_group_pathway_transition_heatmaps_triptych_appendix")

    states = pd.read_csv(
        PKG_ROOT / "outputs/source_data/income_group_pathways/balanced_income_group_state_shares.csv"
    )
    pivot = states.pivot(index="context_label", columns="state", values="share").reindex(order)
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    bottom = np.zeros(len(pivot))
    for col, color in zip(pivot.columns, [GREY, ORANGE, "#D0A645", TEAL]):
        ax.bar(pivot.index, 100 * pivot[col], bottom=bottom, label=col, color=color)
        bottom += 100 * pivot[col].to_numpy()
    ax.set(ylabel="Share of common task universe (%)", title="Joint pathway decomposition")
    ax.tick_params(axis="x", rotation=20); ax.legend(frameon=False, fontsize=6)
    save_check(fig, "fig_appendix_joint_pathway_decomposition")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.scatter(country["log_gdp_per_capita"], 100 * country["substitution_minus_augmentation"], color=BLUE, s=15, alpha=0.7)
    ax.axhline(0, color=GREY, linewidth=0.7)
    ax.set(xlabel="Log GDP per capita", ylabel="Substitution minus augmentation (pp)", title="Polarisation by income")
    save_check(fig, "fig_polarisation_p_loess")
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    arrays = [100 * country.loc[country["income_level"] == x, "substitution_minus_augmentation"].dropna().to_numpy() for x in order]
    ax.boxplot(arrays, tick_labels=["Low", "Lower middle", "Upper middle", "High"], showfliers=False)
    ax.axhline(0, color=GREY, linewidth=0.7)
    ax.set(ylabel="Substitution minus augmentation (pp)", title="Polarisation distribution")
    save_check(fig, "fig_polarisation_p_boxplot")

    channel = pd.read_csv(PKG_ROOT / "outputs/source_data/channel_ai/region_channel_ai_summary.csv")
    channel_cols = ["physical_execution", "rule_based_workflow", "planning_control", "informational_transformation", "inference_scoring"]
    means = channel.groupby("income_level")[channel_cols].mean().reindex(order)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for col in channel_cols:
        ax.plot(means.index, 100 * means[col], marker="o", label=col.replace("_", " "))
    ax.set(ylabel="Share of exposed tasks (%)", title="Channel rotation by income")
    ax.tick_params(axis="x", rotation=20); ax.legend(frameon=False, fontsize=5.5, ncol=2)
    save_check(fig, "fig_channel_rotation_loess_all_tasks")

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    bottom = np.zeros(len(means))
    for col, color in zip(channel_cols, [ORANGE, "#D0A645", GREY, BLUE, TEAL]):
        ax.bar(means.index, 100 * means[col], bottom=bottom, label=col.replace("_", " "), color=color)
        bottom += 100 * means[col].to_numpy()
    ax.set(ylabel="Channel composition (%)", title="Channel composition and income")
    ax.tick_params(axis="x", rotation=20); ax.legend(frameon=False, fontsize=5.5, ncol=2)
    save_check(fig, "fig_channel_composition_income_function")

    functions = pd.read_csv(PKG_ROOT / "outputs/source_data/channel_ai/ai_function_income_summary_taskid.csv").set_index("income_level").reindex(order)
    function_cols = ["learned_content_transformation", "learned_state_inference", "learned_recommendation_decision", "learned_adaptive_control"]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    bottom = np.zeros(len(functions))
    for col, color in zip(function_cols, [BLUE, TEAL, "#D0A645", ORANGE]):
        ax.bar(functions.index, 100 * functions[col], bottom=bottom, label=col.replace("learned_", "").replace("_", " "), color=color)
        bottom += 100 * functions[col].to_numpy()
    ax.set(ylabel="AI-material function mix (%)", title="AI function mix by income")
    ax.tick_params(axis="x", rotation=20); ax.legend(frameon=False, fontsize=5.5)
    save_check(fig, "fig_ai_function_mix_income_taskid")

    occ = pd.read_parquet(PKG_ROOT / "data_intermediate/country_occupation_panel.parquet", columns=["occupation_title", "mean_exposure"])
    occ_top = occ.groupby("occupation_title")["mean_exposure"].mean().nlargest(15).sort_values()
    fig, ax = plt.subplots(figsize=(7.2, 5.0)); ax.barh(occ_top.index, occ_top.values, color=TEAL)
    ax.set(xlabel="Mean exposure", title="Top occupation exposure rotation check")
    save_check(fig, "fig_isco_income_rotation_top_tier")

    ind = pd.read_parquet(PKG_ROOT / "data_intermediate/country_industry_panel.parquet", columns=["activity_description", "weighted_exposure"])
    ind_top = ind.groupby("activity_description")["weighted_exposure"].mean().nlargest(15).sort_values()
    fig, ax = plt.subplots(figsize=(7.2, 5.0)); ax.barh(ind_top.index, ind_top.values, color=BLUE)
    ax.set(xlabel="Mean weighted exposure", title="Top industry exposure rotation check")
    save_check(fig, "fig11_isic_income_rotation_main")

    shapley = pd.read_csv(PKG_ROOT / "outputs/source_data/country_predictors/country_covariate_shapley_importance.csv")
    shapley = shapley.nlargest(15, "shapley_r2").sort_values("shapley_r2")
    fig, ax = plt.subplots(figsize=(7.2, 5.0)); ax.barh(shapley["variable"], shapley["shapley_r2"], color=BLUE)
    ax.set(xlabel="Linear Shapley R-squared contribution", title="Country predictor linear decomposition")
    save_check(fig, "fig_country_predictor_linear_shapley_r2")

    weight = pd.read_csv(PKG_ROOT / "data_intermediate/country_employment_weighting_comparison.csv")
    fig, ax = plt.subplots(figsize=(5.8, 4.8))
    ax.scatter(100 * weight["transport_weighted_occ_exposed_share"], 100 * weight["employment_weighted_occ_exposed_share"], color=BLUE, s=15, alpha=0.75)
    lim = [0, 100 * max(weight["transport_weighted_occ_exposed_share"].max(), weight["employment_weighted_occ_exposed_share"].max())]
    ax.plot(lim, lim, color=GREY, linestyle="--", linewidth=0.7)
    ax.set(xlabel="Transport-weighted exposed share (%)", ylabel="Employment-weighted exposed share (%)", title="ILOSTAT weighting comparison")
    save_check(fig, "figS28_ilostat_country_weighting_scatter")


def main() -> None:
    setup()
    build_shap_ale()
    build_gender_informality()
    build_gender_gap_decomposition()
    build_extended_source_checks()
    print("Wrote current and extended manuscript source-data check renders")


if __name__ == "__main__":
    main()
