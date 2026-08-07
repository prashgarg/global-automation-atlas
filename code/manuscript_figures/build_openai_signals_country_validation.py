#!/usr/bin/env python3
"""Rebuild the OpenAI Signals v2.0 country-level Atlas comparisons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats


PKG_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = PKG_ROOT / "outputs/source_data/openai_observed_use"
DEFAULT_COUNTRY = PKG_ROOT / "outputs/source_data/country_map/scatter_exposed_share_vs_log_gdp_pc.csv"
DEFAULT_AI = PKG_ROOT / "outputs/source_data/channel_ai/country_channel_ai_panel.csv"
DEFAULT_METADATA = PKG_ROOT / "data_intermediate/country_metadata.csv"
DEFAULT_OUT = PKG_ROOT / "reproduced/data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--country-panel", type=Path, default=DEFAULT_COUNTRY)
    parser.add_argument("--ai-panel", type=Path, default=DEFAULT_AI)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def atlas_panel(country_path: Path, ai_path: Path, metadata_path: Path) -> pd.DataFrame:
    country = pd.read_csv(country_path)[
        ["iso3", "country_name", "region", "share_exposed", "log_gdp_per_capita", "internet_users_pct"]
    ]
    ai = pd.read_csv(ai_path)[["iso3", "ai_material_share_exposed"]].rename(
        columns={"ai_material_share_exposed": "ai_material_share"}
    )
    codes = pd.read_csv(metadata_path)[["iso2", "iso3"]].drop_duplicates()
    return codes.merge(country, on="iso3", validate="one_to_one").merge(
        ai, on="iso3", validate="one_to_one"
    )


def rank_percentile(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    highest_rank = out.groupby("quarter")["rank"].transform("max")
    out["openai_rank_percentile"] = 1 - (out["rank"] - 1) / (highest_rank - 1)
    return out


def correlation_rows(frame: pd.DataFrame, outcome: str, sample: str) -> list[dict[str, float | str]]:
    rows = []
    for variable in ["share_exposed", "ai_material_share"]:
        use = frame[[outcome, variable]].dropna()
        spearman = stats.spearmanr(use[outcome], use[variable])
        pearson = stats.pearsonr(use[outcome], use[variable])
        rows.append(
            {
                "sample": sample,
                "outcome": outcome,
                "atlas_measure": variable,
                "countries": len(use),
                "spearman_rho": spearman.statistic,
                "spearman_p": spearman.pvalue,
                "pearson_r": pearson.statistic,
                "pearson_p": pearson.pvalue,
            }
        )
    return rows


def zscore(series: pd.Series) -> pd.Series:
    return (series - series.mean()) / series.std(ddof=0)


def adjusted_models(frame: pd.DataFrame, outcome: str, sample: str) -> list[dict[str, float | str]]:
    rows = []
    for variable in ["share_exposed", "ai_material_share"]:
        use = frame[
            [outcome, variable, "log_gdp_per_capita", "internet_users_pct", "region"]
        ].dropna().copy()
        for name in [outcome, variable, "log_gdp_per_capita", "internet_users_pct"]:
            use[f"z_{name}"] = zscore(use[name])
        fit = smf.ols(
            f"z_{outcome} ~ z_{variable} + z_log_gdp_per_capita + "
            "z_internet_users_pct + C(region)",
            data=use,
        ).fit(cov_type="HC1")
        rows.append(
            {
                "sample": sample,
                "outcome": outcome,
                "atlas_measure": variable,
                "countries": len(use),
                "standardized_beta": fit.params[f"z_{variable}"],
                "robust_se": fit.bse[f"z_{variable}"],
                "p_value": fit.pvalues[f"z_{variable}"],
                "r_squared": fit.rsquared,
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    atlas = atlas_panel(args.country_panel, args.ai_panel, args.metadata)

    ranks = rank_percentile(
        pd.read_csv(args.source_dir / "share_of_messages_by_country_quarter_rank.csv")
    ).merge(atlas, left_on="country", right_on="iso2", how="inner", validate="many_to_one")
    quarter_count = ranks["quarter"].nunique()
    average_rank = (
        ranks.groupby("iso3", as_index=False)
        .agg(
            openai_rank_percentile=("openai_rank_percentile", "mean"),
            quarters=("quarter", "nunique"),
            country_name=("country_name", "first"),
            region=("region", "first"),
            share_exposed=("share_exposed", "first"),
            ai_material_share=("ai_material_share", "first"),
            log_gdp_per_capita=("log_gdp_per_capita", "first"),
            internet_users_pct=("internet_users_pct", "first"),
        )
    )
    complete_rank = average_rank[average_rank["quarters"].eq(quarter_count)].copy()

    work = pd.read_csv(args.source_dir / "share_of_messages_by_work_related_country_month.csv")
    work = (
        work[work["work_related"].eq(1)]
        .groupby("country", as_index=False)["share_of_messages"]
        .mean()
        .rename(columns={"share_of_messages": "work_related_share"})
        .merge(atlas, left_on="country", right_on="iso2", how="inner", validate="one_to_one")
    )

    correlations = correlation_rows(
        complete_rank, "openai_rank_percentile", "six_quarter_average"
    ) + correlation_rows(work, "work_related_share", "twenty_four_month_average")
    models = adjusted_models(
        complete_rank, "openai_rank_percentile", "six_quarter_average"
    ) + adjusted_models(work, "work_related_share", "twenty_four_month_average")

    complete_rank.to_csv(args.out_dir / "openai_signals_v2_country_rank_atlas.csv", index=False)
    work.to_csv(args.out_dir / "openai_signals_v2_work_share_atlas.csv", index=False)
    pd.DataFrame(correlations).to_csv(
        args.out_dir / "openai_signals_v2_country_correlations.csv", index=False
    )
    pd.DataFrame(models).to_csv(
        args.out_dir / "openai_signals_v2_country_adjusted_models.csv", index=False
    )
    coverage = {
        "release": "OpenAI Signals v2.0",
        "quarters": int(quarter_count),
        "complete_rank_countries": int(len(complete_rank)),
        "work_share_countries": int(len(work)),
        "rank_period": "2025 Q1--2026 Q2",
        "work_share_period": "2024-07--2026-06",
    }
    (args.out_dir / "openai_signals_v2_country_coverage.json").write_text(
        json.dumps(coverage, indent=2) + "\n", encoding="utf-8"
    )
    print(pd.DataFrame(correlations).to_string(index=False))


if __name__ == "__main__":
    main()
