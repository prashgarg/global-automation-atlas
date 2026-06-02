# Rationale-concept source data

This folder contains the compact source-data bundle for the same-task rationale-concept analysis reported in the manuscript.

The analysis uses retained short rationales generated during the original task-country labelling step. The public package does not include the full rationale corpus, raw API request logs, batch outputs, embeddings, or exploratory rationale analyses. Instead, it includes the fixed concept list, fidelity summaries, evaluation-sample paired tests, mask terms, and figure/table source data needed to inspect the reported results.

## Files

- `target_spec.json`: target definition for the same-task exposed versus non-exposed country comparison.
- `place_mask_terms_used.csv`: country, demonym, regional, and bloc terms masked before text analysis.
- `selected_hypotheses.csv`: the 20 fixed concepts retained before evaluation-sample testing.
- `concept_fidelity_ranked.csv`: fidelity audit for candidate interpretations, including the high-minus-low activation gap used before retention.
- `evaluation_sample_overview.csv`: evaluation-sample counts.
- `paired_concept_tests.csv`: paired exposed-minus-non-exposed tests for the 20 retained concepts.
- `paired_family_tests.csv`: family-level paired tests used for the main rationale-concept figure panel.
- `paired_summary.csv`: compact summary of the paired evaluation.
- `fig_country_context_explanations_panel_a_source.csv`: source data for the random-forest panel of the combined country-context figure.
- `fig_country_context_explanations_panel_b_source.csv`: source data for the family-level rationale-concept panel of the combined country-context figure.
- `fig_country_context_rf_rationale_children_panel_a_source.csv`: source data for the random-forest panel of the fuller supplementary country-context figure.
- `fig_country_context_rf_rationale_children_panel_b_source.csv`: source data for the child-concept panel of the fuller supplementary country-context figure.
- `fig_country_context_panel_b_rationale_children_exact_source.csv`: child-concept source data for the standalone rationale-concept panel.
- `fig_country_context_explanations_rf_source.csv`: random-forest source data used in the combined figure preparation.
- `rationale_examples_table_source.csv`: source data behind the illustrative same-task rationale-pair table.

## Interpretation

Positive paired differences indicate concepts that appear more often in rationales from the exposed-country side of the same-task pair. Negative paired differences indicate concepts that appear more often in rationales from the non-exposed-country side. Standard errors are paired within task pair; adjusted p-values are Bonferroni-adjusted across retained child concepts.
