if (!exists("read_csv_here", inherits = FALSE)) {
  suppressPackageStartupMessages({library(dplyr); library(readr)})
  pkg_root <- normalizePath(getwd(), mustWork = TRUE)
  read_csv_here <- function(path) read_csv(file.path(pkg_root, path), show_col_types = FALSE)
}

message("Auditing the fixed-concept HypotheSAEs bundle...")

concepts <- read_csv_here(
  "outputs/source_data/rationale_concepts/current_paper/full_fixed_concept_appendix_figure_source.csv"
)
families <- read_csv_here(
  "outputs/source_data/rationale_concepts/current_paper/rf_companion_rationale_panel_source.csv"
)

expected <- tibble(
  target_name = c(
    "same_task_exposed_vs_non_exposed",
    "same_task_substitution_vs_other_exposed",
    "same_task_augmentation_vs_other_exposed"
  ),
  manuscript_significant = c(20L, 13L, 12L)
)

audit <- concepts %>%
  group_by(target_name) %>%
  summarise(
    fixed_child_concepts = n(),
    heldout_pairs = first(n_pairs),
    discovery_scores_present = sum(!is.na(discovery_target_separation)),
    fidelity_scores_present = sum(!is.na(fidelity_gap)),
    paired_effects_present = sum(!is.na(effect) & !is.na(se)),
    source_bonferroni_significant = sum(is_significant),
    .groups = "drop"
  ) %>%
  left_join(expected, by = "target_name") %>%
  mutate(
    fixed_count_pass = fixed_child_concepts == 20L,
    heldout_pairs_pass = heldout_pairs == 2000L,
    discovery_pass = discovery_scores_present == 20L,
    fidelity_pass = fidelity_scores_present == 20L,
    paired_estimator_pass = paired_effects_present == 20L,
    manuscript_count_match = source_bonferroni_significant == manuscript_significant
  )

family_audit <- families %>%
  group_by(panel, target_name) %>%
  summarise(
    pooled_families = n(),
    paired_effects_present = sum(!is.na(family_effect_pp) & !is.na(family_se_pp)),
    .groups = "drop"
  )

write_csv(audit, file.path(pkg_root, "reproduced/checks/rationale_hypothesaes_audit.csv"))
write_csv(family_audit, file.path(pkg_root, "reproduced/checks/rationale_hypothesaes_family_audit.csv"))

if (any(!audit$fixed_count_pass | !audit$heldout_pairs_pass | !audit$discovery_pass |
        !audit$fidelity_pass | !audit$paired_estimator_pass)) {
  print(audit, n = Inf)
  stop("HypotheSAEs audit failed structural checks. See reproduced/checks/rationale_hypothesaes_audit.csv", call. = FALSE)
}

if (any(!audit$manuscript_count_match)) {
  message(
    "HypotheSAEs structural audit passed, but the manuscript significance count differs from the " ,
    "released figure-source data for: ",
    paste(audit$target_name[!audit$manuscript_count_match], collapse = ", "),
    ". This is recorded as a blocker rather than silently reconciled."
  )
} else {
  message("HypotheSAEs audit passed for all three heldout contrasts.")
}
