message("Auditing rationale-concept source bundle...")

rationale_dir <- file.path(pkg_root, "outputs/source_data/rationale_concepts")

selected <- read_csv(file.path(rationale_dir, "selected_hypotheses.csv"), show_col_types = FALSE)
concept <- read_csv(file.path(rationale_dir, "paired_concept_tests.csv"), show_col_types = FALSE)
family <- read_csv(file.path(rationale_dir, "paired_family_tests.csv"), show_col_types = FALSE)
overview <- read_csv(file.path(rationale_dir, "evaluation_sample_overview.csv"), show_col_types = FALSE)
examples <- read_csv(file.path(rationale_dir, "rationale_examples_table_source.csv"), show_col_types = FALSE)

selected_ids <- unique(selected$hypothesis_id)
concept_ids <- unique(concept$hypothesis_id)

checks <- tibble(
  check = c(
    "Selected child concepts",
    "Paired child-concept tests",
    "Concept families",
    "Family child-concept total",
    "Evaluation rows",
    "Evaluation same-task pairs",
    "Minimum concept-test pairs",
    "Maximum concept-test pairs",
    "Illustrative example rows",
    "Example adjusted p-values",
    "Selected concepts appear in paired tests"
  ),
  value = c(
    nrow(selected),
    nrow(concept),
    nrow(family),
    sum(family$n_hypotheses),
    overview$sample_n[[1]],
    overview$per_class_actual[[1]],
    min(concept$n_pairs),
    max(concept$n_pairs),
    nrow(examples),
    paste(sort(unique(examples$adjusted_p)), collapse = "; "),
    length(setdiff(selected_ids, concept_ids))
  ),
  expected = c(
    20,
    20,
    7,
    20,
    4000,
    2000,
    2000,
    2000,
    7,
    "<0.001",
    0
  ),
  pass = c(
    nrow(selected) == 20,
    nrow(concept) == 20,
    nrow(family) == 7,
    sum(family$n_hypotheses) == 20,
    overview$sample_n[[1]] == 4000,
    overview$per_class_actual[[1]] == 2000,
    min(concept$n_pairs) == 2000,
    max(concept$n_pairs) == 2000,
    nrow(examples) == 7,
    all(examples$adjusted_p == "<0.001"),
    length(setdiff(selected_ids, concept_ids)) == 0
  )
)

write_csv(checks, file.path(pkg_root, "reproduced/checks/rationale_concept_audit.csv"))

family_values <- family %>%
  select(
    concept_family,
    side,
    n_hypotheses,
    score_exposed_mean,
    score_non_exposed_mean,
    score_paired_difference,
    score_paired_se,
    score_paired_p_text
  )
write_csv(family_values, file.path(pkg_root, "reproduced/checks/rationale_concept_family_values.csv"))

concept_values <- concept %>%
  select(
    hypothesis_rank,
    side,
    concept_family,
    interpretation,
    n_pairs,
    exposed_yes_rate,
    non_exposed_yes_rate,
    paired_difference,
    paired_se,
    paired_p_text,
    paired_bonferroni_p_text
  )
write_csv(concept_values, file.path(pkg_root, "reproduced/checks/rationale_concept_child_values.csv"))

if (any(!checks$pass)) {
  print(checks %>% filter(!pass), n = Inf)
  stop("Rationale-concept audit found mismatches. See reproduced/checks/rationale_concept_audit.csv", call. = FALSE)
}

message("Rationale-concept audit passed: 20 concepts, 7 families, 2,000 same-task pairs.")
