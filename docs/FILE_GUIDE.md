# File guide

This note explains the main files in the replication package.

## Main measurement files

- `data_intermediate/task_country_labels_analysis.parquet`: retained task-country labels. This is the main measurement file, with one row per task-country observation.
- `data_intermediate/task_country_rationales/`: eight Parquet partitions containing the exact non-empty short rationales accompanying the retained labels. The files join to the label file by `item_id`, or by `task_id` and `iso3`.
- `data_intermediate/task_metadata.csv`: task statements and task identifiers.
- `data_intermediate/country_metadata.csv`: country identifiers, regions, income groups, and weighting metadata.
- `data_intermediate/benchmark_task_labels.parquet`: task labels under benchmark contexts used for context-free and income-group comparisons.
- `data_intermediate/country_occupation_panel.parquet`: country-occupation exposure summaries.
- `data_intermediate/country_industry_panel.parquet`: country-industry exposure summaries.

## Analysis panels

- `data_analysis/country_map_panel.csv`: country-level exposure, margin, GDP, population, and covariate fields used in the opening country figures.
- `data_analysis/country_channel_ai_panel.csv`: country-level channel and AI-materiality summaries.
- `data_analysis/country_covariate_rf_mean_abs_shap.csv`: current random-forest TreeSHAP predictor summaries. Direction flags use the five-seed ALE ensemble rule: median ALE difference and a four-of-five sign threshold, otherwise `mixed`.
- `data_analysis/gender_gap_isco_isic_summary.csv`: gender-gap summary statistics for occupation and industry weighting.

## Output folders

- `outputs/figures/`: exact figure files used in the manuscript.
- `outputs/tables/`: exact LaTeX table files used in the manuscript.
- `outputs/source_data/`: compact source data behind validation checks, country figures, predictors, benchmarks, and ILOSTAT analyses.
- `outputs/source_data/rationale_concepts/`: the current 60 fixed concepts, pooled Figure 6 families, place-mask terms, and source rows for the illustrative heldout rationale pairs.
- `outputs/source_data/openai_observed_use/`: public OpenAI Signals IWA series and the O*NET task hierarchy used to rebuild the observed-use validation.
- `outputs/source_data/ilostat_gender/gender_gap_decomposition_*.csv`: country-level and income-group source data for the gender-gap decomposition and its reported component means.
- `outputs/source_data/ilostat_gender/table_B8_inputs/`: sex-specific two-digit employment weights and country-cell exposure panels used to re-estimate Supplementary Table B.8.
- `reproduced/`: files created by `Rscript code/make_all.R`.

## Figure registry and builders

- `docs/figure_asset_registry.csv`: one row for each of the 40 active figures, with class, public command, rebuilt file, original producer, released sources, and a precise limit.
- `code/manuscript_figures/build_fixed_concept_appendix_figures.py`: package-relative adaptation of the original three-target fixed-concept builder.
- `code/manuscript_figures/build_combined_rf_rationale_main_figure.py`: package-relative adaptation of the original six-panel Figure 6 builder.
- `code/manuscript_figures/build_current_check_renders.py`: numerical/source-data checks for all other publicly checkable active figures.
- `code/manuscript_figures/compare_exact_build_renders.py`: 150-dpi rendered-pixel comparison for the five direct builds.

## Checks

- `reproduced/checks/numeric_claim_audit.csv`: paper-presented numbers checked against source data.
- `reproduced/checks/figure_reproduction_status.csv`: active-only validation of the explicit per-figure class, command, sources, rebuilt file, and snapshot/rebuilt hashes.
- `reproduced/checks/exact_build_render_comparison.csv`: byte-hash and rendered-pixel comparison for the five direct builds.
- `reproduced/checks/shap_ale_five_seed_direction_check.csv`: row-level recomputation of the four-of-five ALE sign rule.
- `reproduced/checks/manuscript_figure_artifact_exact_match.csv`: checksum comparison between manuscript figures and package copies.
- `reproduced/checks/manuscript_table_artifact_exact_match.csv`: checksum comparison between manuscript tables and package copies.
- `reproduced/checks/rationale_hypothesaes_audit.csv`: discovery, fidelity, and heldout paired-estimator checks for all three fixed-concept targets, including the final 20/13/12 Bonferroni-significant counts.
- `reproduced/checks/rationale_corpus_audit.csv`: coverage, uniqueness, and label-key checks for the released rationale corpus.
- `reproduced/checks/gender_table_B8_reestimation_check.csv`: comparison of the re-estimated fixed-effect results with the released Supplementary Table B.8 values.
