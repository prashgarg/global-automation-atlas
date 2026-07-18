# Rationale-concept source data

This folder contains the compact source-data bundle for the three rationale-concept contrasts reported in the manuscript.

The analysis uses retained short rationales generated during the original task-country labelling step. The public package excludes the full rationale corpus, raw API request logs, batch outputs, embeddings, exploratory contrasts, and superseded concept sets. It includes the fixed paper-facing concepts, their discovery and fidelity scores, heldout estimates, mask terms, pooled Figure 6 families, and source rows for the illustrative examples.

## Files

- `place_mask_terms_used.csv`: country, demonym, regional, and bloc terms masked before text analysis.
- `current_paper/full_fixed_concept_appendix_figure_source.csv`: 60-row fixed-concept display source with discovery separation, fidelity gap, and corrected heldout paired estimates for all three targets.
- `current_paper/full_fixed_concept_appendix_figure_summary.csv`: target-level concept and significance counts.
- `current_paper/rf_companion_rationale_panel_source.csv`: compact pooled-family display labels and heldout estimates used by the public combined Figure 6 builder.
- `rationale_examples_table_source.csv`: current heldout same-task pairs used in the illustrative examples table, including row identifiers, family scores, verbatim rationales, and shortened table text.

## Interpretation

For the exposure contrast, positive paired differences indicate concepts that appear more often on the exposed-country side of the same-task pair. The two labour-margin contrasts use the first-minus-second ordering stated in the source file. Standard errors are paired within task pair, and adjusted p-values are Bonferroni-adjusted across retained child concepts within each contrast.
