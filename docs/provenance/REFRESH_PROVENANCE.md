# Active Manuscript Refresh Provenance

This package was refreshed against `overleaf_nature_v8/main.tex` and its active figure/table assets on 2026-07-18. `docs/main_manuscript_snapshot.tex` is an immutable documentation snapshot of that source at refresh time. The package does not modify the manuscript.

## Exact Reference Snapshots

Files in `outputs/figures/` and `outputs/tables/` are exact reference snapshots captured from the active manuscript asset folder with these explicit refresh commands:

```bash
cp overleaf_import/Automation_and_Skill_Gaps_Survey/overleaf_nature_v8/01_Figures/refresh_country124_20260406/<active-figure> replication_package/outputs/figures/
cp overleaf_import/Automation_and_Skill_Gaps_Survey/overleaf_nature_v8/02_Tables/refresh_country124_20260406/<active-table>.tex replication_package/outputs/tables/
```

These commands capture compiled manuscript artifacts; they do not claim to regenerate them. `manifest.csv` records each snapshot checksum and its public verification command.

After refreshing the snapshots, the release-time checksum audit is regenerated with:

```bash
ACTIVE_MANUSCRIPT_ROOT=/path/to/active/manuscript Rscript code/06_refresh_audit.R
```

This writes exact-match reports for every active figure and file-backed table. A public run without `ACTIVE_MANUSCRIPT_ROOT` verifies the package inventory and retained checks without requiring access to the manuscript workspace.

## Original Production And Public Boundaries

- Supplementary Table B.8 is re-estimated publicly with `Rscript code/08_rebuild_gender_table_B8.R` from the released sex-specific two-digit employment weights and country-cell exposure panels in `outputs/source_data/ilostat_gender/table_B8_inputs/`. The script checks the resulting coefficients, standard errors, and sample sizes against `gender_fe_table_current.csv`. The original ILOSTAT downloads are not redistributed; source indicators, years, and access details are retained in the released inputs and source inventory.
- The gender/informality figure was originally produced by `Rscript validation/application_portfolio/gender_informality_margin_section_20260604/build_gender_informality_section.R`. The package includes compact country-level regression inputs, but not the complete ILOSTAT/informality construction inputs needed for an exact rendering.
- The combined TreeSHAP/rationale figure was originally produced by `python validation/rationale_theme_model/heldout_hypothesis_literature_positioning_20260604/build_combined_rf_rationale_main_figure.py`. The adapted public builder reads `outputs/source_data/country_predictors/country_covariate_rf_mean_abs_shap.csv` and `outputs/source_data/rationale_concepts/current_paper/rf_companion_rationale_panel_source.csv`. The analysis-ready rationales are released in `data_intermediate/task_country_rationales/`; embeddings and raw API batches are excluded.
- The three full fixed-concept appendix figures were originally produced by `python validation/rationale_theme_model/heldout_hypothesis_literature_positioning_20260604/full_fixed_concept_appendix_figures_20260624/build_full_fixed_concept_appendix_figures.py`. The package includes the 60-row fixed-concept derived source table with discovery score, fidelity score, heldout paired estimate, standard error, and significance status. The analysis-ready rationale text is released; annotation batches and embeddings remain excluded.
- The OpenAI observed-use alignment is rebuilt from the retained U.S. task labels, O*NET task hierarchy, and public OpenAI Signals IWA series. OpenAI releases the Signals files under CC BY 4.0; the package includes the two series used by the figure with attribution.

The public commands in `code/` regenerate direct figures or numerical/source-data checks from released inputs. `docs/figure_asset_registry.csv` records the exact status for all 40 active figures. Five figures have direct package-relative builds, and thirty-five have named check renders from released inputs.

## HypotheSAEs boundary

The 60-row fixed-concept table exposes the paper-facing discovery separation, fidelity gap, and heldout paired estimate for 20 concepts in each of three targets. Each heldout estimate uses 2,000 same-task pairs. The public package also exposes the analysis-ready rationale corpus. Annotation batches, embeddings, exploratory concept sets, and typology-adjudication records are not included, so the public workflow reproduces the reported estimates and displays without repeating the original paid annotation and concept-discovery calls.

The released source and the refreshed manuscript snapshot report 20 Bonferroni-significant exposure concepts, 13 substitution concepts, and 12 augmentation concepts.
