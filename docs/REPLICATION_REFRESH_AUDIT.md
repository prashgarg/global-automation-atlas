# Replication package refresh audit

Date: 2026-07-18

## Coverage and classes

The explicit registry equals the 40-figure active set parsed from `docs/main_manuscript_snapshot.tex`.

- 5 `exact_reproducible_build`
- 35 `numerical_source_data_check_render`
- 14/14 file-backed active table snapshots match the manuscript assets exactly.
- 59/59 audited reported statistics match the paper values at the reported precision.
- Supplementary Table B.8 is re-estimated from the released two-digit employment weights and country-cell exposure panels, then checked against `outputs/source_data/ilostat_gender/gender_fe_table_current.csv`.

## Direct builds

The combined Figure 6, three fixed-concept HypotheSAEs appendix figures, and OpenAI observed-use alignment are produced by package-relative adaptations of their original scripts and checked against the active snapshots after 150 dpi rendering. PDF byte hashes can differ because regenerated PDFs contain different metadata or font object encoding.

The HypotheSAEs audit confirms 20 fixed concepts per target, 2,000 heldout same-task pairs per concept, and complete discovery, fidelity, and corrected paired-estimator fields.

The TreeSHAP/ALE audit recomputes the five-seed rule for all 27 `main68` feature-outcome rows: a direction is positive or negative only when at least four of five seed-specific ALE signs agree. All 27 released flags pass.

## Remaining limits

1. The 35 numerical/source-data check renders reproduce released values but do not claim pixel identity where the original composition, cartography, or typography differs.
2. The analysis-ready rationale text is released in eight Parquet partitions. Raw API batches, annotation batches, embeddings, exploratory concept sets, and restricted third-party microdata are excluded. The public workflow does not repeat the original paid API labelling or concept-discovery calls.
3. The compact gender/informality check reproduces country medians, IQRs, and country-level informality coefficients. The omitted cell-FE informality construction input prevents claiming an exact direct build of that panel.

## Verification command

```bash
ACTIVE_MANUSCRIPT_ROOT=/path/to/overleaf_nature_v8 \
Rscript code/make_all.R
```

Install Python dependencies first with `python3 -m pip install -r code/requirements.txt`. This audit used the same dependencies in an isolated temporary target directory.

The final clean-environment run used Python 3.9 with only the packages declared in `code/requirements.txt` and completed successfully. `make_all.R` accepts a `PYTHON` environment variable, allowing the workflow to use a project virtual environment. The release-time checksum audit then confirmed exact matches for all 40 active figure snapshots and all 14 file-backed table snapshots.

## Changed source and documentation files

- `README.md`
- `code/00_setup.R`
- `code/01_rebuild_tables.R`
- `code/02_rebuild_figures.R`
- `code/03_compare_outputs.R`
- `code/04_numeric_audit.R`
- `code/05_rationale_concept_audit.R`
- `code/06_refresh_audit.R`
- `code/check_replication_package.R`
- `code/make_all.R`
- `code/requirements.txt`
- `code/manuscript_figures/build_combined_rf_rationale_main_figure.py`
- `code/manuscript_figures/build_current_check_renders.py`
- `code/manuscript_figures/build_fixed_concept_appendix_figures.py`
- `code/manuscript_figures/build_openai_observed_use_iwa_validation.py`
- `code/manuscript_figures/compare_exact_build_renders.py`
- `docs/FILE_GUIDE.md`
- `docs/figure_asset_registry.csv`
- `docs/main_manuscript_snapshot.tex`
- `docs/provenance/REFRESH_PROVENANCE.md`
- `docs/references.bib`
- `outputs/source_data/benchmark_ladder/benchmark_pack_summary.json`
- `outputs/source_data/ilostat_gender/gender_fe_table_current.csv`
- `outputs/source_data/ilostat_gender/gender_gap_decomposition_by_income.csv`
- `outputs/source_data/ilostat_gender/gender_gap_decomposition_country_level.csv`
- `outputs/source_data/openai_observed_use/`
- `outputs/source_data/rationale_concepts/README.md`
- `outputs/source_data/rationale_concepts/current_paper/full_fixed_concept_appendix_figure_source.csv`
- `outputs/source_data/rationale_concepts/current_paper/full_fixed_concept_appendix_figure_summary.csv`
- `outputs/source_data/rationale_concepts/current_paper/rf_companion_rationale_panel_source.csv`
- `outputs/source_data/rationale_concepts/rationale_examples_table_source.csv`
- `outputs/tables/tab_appendix_country_context_rationale_examples.tex`
- `manifest.csv`
- `docs/REPLICATION_REFRESH_AUDIT.md`

## Regenerated files

- `reproduced/checks/active_manuscript_asset_manifest.csv`
- `reproduced/checks/exact_build_render_comparison.csv`
- `reproduced/checks/figure_reproduction_status.csv`
- `reproduced/checks/hypothesaes_figure_input_summary.csv`
- `reproduced/checks/manuscript_figure_artifact_exact_match.csv`
- `reproduced/checks/manuscript_table_artifact_exact_match.csv`
- `reproduced/checks/numeric_claim_audit.csv`
- `reproduced/checks/rationale_hypothesaes_audit.csv`
- `reproduced/checks/rationale_hypothesaes_family_audit.csv`
- `reproduced/checks/shap_ale_five_seed_direction_check.csv`
- `reproduced/checks/table_reproduction_status.csv`
- `reproduced/figures/fig11_isic_income_rotation_main_rebuilt.pdf`
- `reproduced/figures/fig3_map_share_exposed_rebuilt.pdf`
- `reproduced/figures/figS28_ilostat_country_weighting_scatter_rebuilt.pdf`
- `reproduced/figures/fig_ai_function_mix_income_taskid_rebuilt.pdf`
- `reproduced/figures/fig_ai_materiality_income_rebuilt.pdf`
- `reproduced/figures/fig_ai_materiality_margins_2x2_rebuilt.pdf`
- `reproduced/figures/fig_appendix_hypothesaes_augmentation_20_concepts.pdf`
- `reproduced/figures/fig_appendix_hypothesaes_augmentation_20_concepts.png`
- `reproduced/figures/fig_appendix_hypothesaes_exposure_20_concepts.pdf`
- `reproduced/figures/fig_appendix_hypothesaes_exposure_20_concepts.png`
- `reproduced/figures/fig_appendix_hypothesaes_substitution_20_concepts.pdf`
- `reproduced/figures/fig_appendix_hypothesaes_substitution_20_concepts.png`
- `reproduced/figures/fig_appendix_joint_pathway_decomposition_rebuilt.pdf`
- `reproduced/figures/fig_benchmark_ladder_country_deviation_rebuilt.pdf`
- `reproduced/figures/fig_channel_ai_mechanism_rebuilt.pdf`
- `reproduced/figures/fig_channel_composition_income_function_rebuilt.pdf`
- `reproduced/figures/fig_channel_rotation_loess_all_tasks_rebuilt.pdf`
- `reproduced/figures/fig_channel_shares_income_rebuilt.pdf`
- `reproduced/figures/fig_country_context_rf_rationale_combined.pdf`
- `reproduced/figures/fig_country_context_rf_rationale_combined.png`
- `reproduced/figures/fig_country_covariate_feature_importance_main68_rebuilt.pdf`
- `reproduced/figures/fig_country_context_rf_shap_check.pdf`
- `reproduced/figures/fig_country_covariate_permutation_importance_main68_rebuilt.pdf`
- `reproduced/figures/fig_country_opening_scatter_log_nopanel_rebuilt.pdf`
- `reproduced/figures/fig_country_predictor_linear_shapley_r2_rebuilt.pdf`
- `reproduced/figures/fig_gender_informality_margin_applications_rebuilt.pdf`
- `reproduced/figures/fig_income_group_pathway_modal_alluvial_main_rebuilt.pdf`
- `reproduced/figures/fig_income_group_pathway_transition_heatmaps_triptych_appendix_rebuilt.pdf`
- `reproduced/figures/fig_isco_income_rotation_top_tier_rebuilt.pdf`
- `reproduced/figures/fig_polarisation_p_boxplot_rebuilt.pdf`
- `reproduced/figures/fig_polarisation_p_loess_rebuilt.pdf`
- `reproduced/figures/fig_task_country_exposure_measures_rebuilt.pdf`
- `reproduced/figures/fig_tasks_country_pathways_joint_review_all_tasks_rebuilt.pdf`
- `reproduced/figures/fig_tasks_country_pathways_joint_review_rebuilt.pdf`
- `reproduced/figures/fig_validation_channel_alignment_rebuilt.pdf`
- `reproduced/figures/fig_validation_country_conditioning_divergence_rebuilt.pdf`
- `reproduced/figures/fig_validation_country_contribution_rebuilt.pdf`
- `reproduced/figures/fig_validation_cross_model_validity_rebuilt.pdf`
- `reproduced/figures/fig_validation_distribution_by_income_rebuilt.pdf`
- `reproduced/figures/fig_validation_distribution_overview_rebuilt.pdf`
- `reproduced/figures/fig_validation_eurostat_adoption_rebuilt.pdf`
- `reproduced/figures/fig_validation_imf_aipi_rebuilt.pdf`
- `reproduced/figures/fig_validation_paraphrase_stability_rebuilt.pdf`
- `reproduced/figures/fig_validation_rationale_predictability_rebuilt.pdf`
- `reproduced/figures/fig_validation_us_vs_external_rebuilt.pdf`
- `reproduced/figures/fig_within_income_variability_rebuilt.pdf`
- `reproduced/figures/full_fixed_concept_appendix_figures.pdf`
- `reproduced/tables/core_counts.csv`
- `reproduced/tables/country_opening_summary_rebuilt.csv`
- `reproduced/tables/gender_fe_regression_table_rebuilt.csv`
- `reproduced/tables/gender_fe_regression_table_rebuilt.tex`
- `reproduced/tables/validation_channel_aligned_correlations_rebuilt.csv`
