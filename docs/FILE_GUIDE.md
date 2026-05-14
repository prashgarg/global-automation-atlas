# File guide

This note explains the main files in the replication package.

## Main measurement files

- `data_intermediate/task_country_labels_analysis.parquet`: retained task-country labels. This is the main measurement file. It has one row per task-country observation and excludes language-model rationales.
- `data_intermediate/task_metadata.csv`: task statements and task identifiers.
- `data_intermediate/country_metadata.csv`: country identifiers, regions, income groups, and weighting metadata.
- `data_intermediate/benchmark_task_labels.parquet`: task labels under benchmark contexts used for context-free and income-group comparisons.
- `data_intermediate/country_occupation_panel.parquet`: country-occupation exposure summaries.
- `data_intermediate/country_industry_panel.parquet`: country-industry exposure summaries.

## Analysis panels

- `data_analysis/country_map_panel.csv`: country-level exposure, margin, GDP, population, and covariate fields used in the opening country figures.
- `data_analysis/country_channel_ai_panel.csv`: country-level channel and AI-materiality summaries.
- `data_analysis/country_covariate_rf_mean_abs_shap.csv`: random-forest TreeSHAP predictor summaries.
- `data_analysis/gender_gap_isco_isic_summary.csv`: gender-gap summary statistics for occupation and industry weighting.
- `data_analysis/gender_fe_regression_table.csv`: fixed-effect regression results for the gender sorting check.

## Output folders

- `outputs/figures/`: exact figure files used in the manuscript.
- `outputs/tables/`: exact LaTeX table files used in the manuscript.
- `outputs/source_data/`: compact source data behind validation checks, country figures, predictors, benchmarks, and ILOSTAT analyses.
- `reproduced/`: files created by `Rscript code/make_all.R`.

## Checks

- `reproduced/checks/numeric_claim_audit.csv`: paper-presented numbers checked against source data.
- `reproduced/checks/figure_reproduction_status.csv`: which figures are rebuilt from source data and which are preserved as final manuscript files.
- `reproduced/checks/manuscript_figure_artifact_exact_match.csv`: checksum comparison between manuscript figures and package copies.
- `reproduced/checks/manuscript_table_artifact_exact_match.csv`: checksum comparison between manuscript tables and package copies.

