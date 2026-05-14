message("Auditing paper-presented numeric claims against package source data...")

claim_rows <- list()

add_claim <- function(section, claim, source_value, expected_value, digits = NULL, scale = 1) {
  value <- as.numeric(source_value) * scale
  expected <- as.numeric(expected_value)
  rounded <- if (is.null(digits)) value else round(value, digits)
  expected_rounded <- if (is.null(digits)) expected else round(expected, digits)
  claim_rows[[length(claim_rows) + 1]] <<- tibble(
    section = section,
    claim = claim,
    source_value = value,
    source_value_rounded = rounded,
    expected_paper_value = expected,
    expected_rounded = expected_rounded,
    digits_checked = ifelse(is.null(digits), NA_integer_, digits),
    match = isTRUE(all.equal(rounded, expected_rounded, tolerance = 1e-12))
  )
}

labels <- read_parquet_here("data_intermediate/task_country_labels_analysis.parquet")
country <- read_csv_here("data_analysis/country_map_panel.csv")
gender_summary <- read_csv_here("data_analysis/gender_gap_isco_isic_summary.csv")
gender_fe <- read_csv_here("data_analysis/gender_fe_regression_table.csv")
valid <- read_csv_here("outputs/source_data/construct_validity/channel_aligned_correlations.csv")
cross <- read_csv_here("outputs/source_data/cross_model_validity/agreement_summary.csv")
rationale <- read_csv_here("outputs/source_data/rationale_label_predictability/agreement_summary.csv")
para <- read_csv_here("outputs/source_data/paraphrase_stability/agreement_by_paraphrase.csv")
para_pair <- read_csv_here("outputs/source_data/paraphrase_stability/agreement_pairwise.csv")
aipi_raw <- read_csv_here("outputs/source_data/firm_ai_adoption/imf_aipi_correlations.csv")
aipi_partial <- read_csv_here("outputs/source_data/firm_ai_adoption/aipi_partial_correlations.csv")
aipi_within <- read_csv_here("outputs/source_data/firm_ai_adoption/aipi_within_income_group.csv")
euro <- read_csv_here("outputs/source_data/firm_ai_adoption/eurostat_validation_robustness.csv")

add_claim("Core data", "Task-country observations", nrow(labels), 2330776)
add_claim("Core data", "Countries", n_distinct(labels$iso3), 124)
add_claim("Core data", "Tasks", n_distinct(labels$task_id), 18797)

add_claim("Global exposure", "Minimum exposed-task share, percent", 100 * min(country$share_exposed, na.rm = TRUE), 3.3, digits = 1)
add_claim("Global exposure", "Maximum exposed-task share, percent", 100 * max(country$share_exposed, na.rm = TRUE), 61.6, digits = 1)

get_valid <- function(external, feature) {
  valid %>% filter(.data$external == .env$external, .data$atlas_feature == .env$feature) %>% pull(pearson) %>% .[[1]]
}
add_claim("Construct validity", "Eloundou GPT-4 gamma vs foundation-model-like share", get_valid("Eloundou GPT-4 gamma", "Paper foundation-model-like share"), 0.78, digits = 2)
add_claim("Construct validity", "Eloundou GPT-4 gamma vs overall exposure", get_valid("Eloundou GPT-4 gamma", "Paper overall exposure"), 0.22, digits = 2)
add_claim("Construct validity", "Felten AIOE vs AI-material share", get_valid("Felten AIOE", "Paper AI-material share"), 0.61, digits = 2)
add_claim("Construct validity", "Felten AIOE vs overall exposure", get_valid("Felten AIOE", "Paper overall exposure"), 0.10, digits = 2)
add_claim("Construct validity", "Webb robotics vs physical-execution share", get_valid("Webb Robot", "Paper physical-execution share"), 0.72, digits = 2)
add_claim("Construct validity", "Webb robotics vs overall exposure", get_valid("Webb Robot", "Paper overall exposure"), 0.05, digits = 2)

get_metric <- function(df, key_col, key, value_col = "value") {
  df %>% filter(.data[[key_col]] == key) %>% pull(.data[[value_col]]) %>% .[[1]]
}
add_claim("Cross-model validity", "Binary exposed agreement, percent", get_metric(cross, "metric", "binary_exposed"), 75.1, digits = 1, scale = 100)
add_claim("Cross-model validity", "Exact four-level agreement, percent", get_metric(cross, "metric", "level_exact"), 48.1, digits = 1, scale = 100)
add_claim("Cross-model validity", "Adjacent-level agreement, percent", get_metric(cross, "metric", "level_adjacent"), 95.0, digits = 1, scale = 100)
add_claim("Cross-model validity", "Dominant-channel exact agreement, percent", get_metric(cross, "metric", "channel_exact"), 61.8, digits = 1, scale = 100)
add_claim("Cross-model validity", "AI-material exact agreement, percent", get_metric(cross, "metric", "ai_material_exact"), 72.3, digits = 1, scale = 100)
add_claim("Cross-model validity", "Exposed-margin exact agreement, percent", get_metric(cross, "metric", "margin_exact_exposed"), 48.5, digits = 1, scale = 100)

add_claim("Reasoning consistency", "Rationale binary-exposed recovery, percent", get_metric(rationale, "field", "binary_exposed"), 99.0, digits = 1, scale = 100)
add_claim("Reasoning consistency", "Rationale exposure exact recovery, percent", get_metric(rationale, "field", "exposure_exact"), 71.5, digits = 1, scale = 100)
add_claim("Reasoning consistency", "Rationale adjacent exposure recovery, percent", get_metric(rationale, "field", "exposure_adjacent_pm1"), 100.0, digits = 1, scale = 100)
add_claim("Reasoning consistency", "Rationale channel exact recovery, percent", get_metric(rationale, "field", "channel_exact"), 67.7, digits = 1, scale = 100)
add_claim("Reasoning consistency", "Rationale exposed-margin exact recovery, percent", get_metric(rationale, "field", "margin_exact_exposed"), 74.8, digits = 1, scale = 100)

for (i in seq_len(nrow(para))) {
  add_claim(
    "Prompt paraphrase stability",
    paste0("Binary exposed agreement for ", para$paraphrase[[i]], ", percent"),
    para$binary_exposed[[i]],
    c(88.7, 87.0, 84.3)[[i]],
    digits = 1,
    scale = 100
  )
}
add_claim("Prompt paraphrase stability", "Minimum pairwise adjacent agreement across paraphrases, percent", min(para_pair$level_adj), 99.8, digits = 1, scale = 100)

get_gender <- function(domain, margin, col) {
  gender_summary %>%
    filter(figure == "Two-digit paper-candidate figure", .data$domain == .env$domain, .data$margin == .env$margin) %>%
    pull(.data[[col]]) %>%
    .[[1]]
}
add_claim("Gender gaps", "ISCO-2 substitution median female-minus-male gap, pp", get_gender("ISCO-2 occupations", "Substitution-only", "median_gap_pp"), 2.11, digits = 2)
add_claim("Gender gaps", "ISCO-2 substitution female-higher share, percent", get_gender("ISCO-2 occupations", "Substitution-only", "female_higher_share"), 78.5, digits = 1, scale = 100)
add_claim("Gender gaps", "ISCO-2 augmentation median female-minus-male gap, pp", get_gender("ISCO-2 occupations", "Augmentation-only", "median_gap_pp"), -0.063, digits = 3)
add_claim("Gender gaps", "ISIC-2 substitution median female-minus-male gap, pp", get_gender("ISIC-2 industries", "Substitution-only", "median_gap_pp"), -0.102, digits = 3)
add_claim("Gender gaps", "ISIC-2 augmentation median female-minus-male gap, pp", get_gender("ISIC-2 industries", "Augmentation-only", "median_gap_pp"), -0.832, digits = 3)
add_claim("Gender gaps", "ISIC-2 augmentation female-higher share, percent", get_gender("ISIC-2 industries", "Augmentation-only", "female_higher_share"), 9.7, digits = 1, scale = 100)

fe_base <- gender_fe %>% filter(model == "Baseline", term == "x")
for (i in seq_len(nrow(fe_base))) {
  add_claim(
    "Gender fixed effects",
    paste(fe_base$domain[[i]], fe_base$margin[[i]], "coefficient"),
    fe_base$coef[[i]],
    c(-0.351, 0.273, -0.219, 0.008)[[i]],
    digits = 3
  )
  add_claim(
    "Gender fixed effects",
    paste(fe_base$domain[[i]], fe_base$margin[[i]], "standard error"),
    fe_base$se[[i]],
    c(0.119, 0.393, 0.041, 0.074)[[i]],
    digits = 3
  )
}

add_claim("AIPI validation", "AI-material share vs AIPI raw Pearson", aipi_raw %>% filter(atlas == "ai_material_share", imf == "AI_PI") %>% pull(pearson), 0.90, digits = 2)
add_claim("AIPI validation", "AI-material share vs AIPI raw Spearman", aipi_raw %>% filter(atlas == "ai_material_share", imf == "AI_PI") %>% pull(spearman), 0.93, digits = 2)
add_claim("AIPI validation", "AI-material share vs AIPI partial Pearson after log GDP", aipi_partial %>% filter(atlas == "ai_material_share", imf == "AI_PI") %>% pull(partial_r), 0.42, digits = 2)
for (inc in c("Low income", "Lower middle income", "Upper middle income", "High income")) {
  expected <- c("Low income" = 0.72, "Lower middle income" = 0.84, "Upper middle income" = 0.90, "High income" = 0.50)[[inc]]
  add_claim("AIPI validation", paste("Within-income AIPI Pearson:", inc), aipi_within %>% filter(income_level == inc) %>% pull(r_ai_material_vs_AIPI), expected, digits = 2)
}

add_claim("Eurostat validation", "Pooled country-NACE Pearson", euro %>% filter(drop_type == "none_pooled") %>% pull(pearson), 0.41, digits = 2)
add_claim("Eurostat validation", "NACE-cell mean Pearson", euro %>% filter(drop_type == "none_industry_mean") %>% pull(pearson), 0.52, digits = 2)
add_claim("Eurostat validation", "Pooled country-NACE Spearman", euro %>% filter(drop_type == "none_pooled") %>% pull(spearman), 0.41, digits = 2)
add_claim("Eurostat validation", "NACE-cell mean Spearman", euro %>% filter(drop_type == "none_industry_mean") %>% pull(spearman), 0.49, digits = 2)
add_claim("Eurostat validation", "Within-country mean Pearson", euro %>% filter(drop_type == "within_country", dropped == "mean") %>% pull(pearson), 0.42, digits = 2)
add_claim("Eurostat validation", "Within-country median Pearson", euro %>% filter(drop_type == "within_country", dropped == "median") %>% pull(pearson), 0.43, digits = 2)

audit <- bind_rows(claim_rows)
write_csv(audit, file.path(pkg_root, "reproduced/checks/numeric_claim_audit.csv"))

if (any(!audit$match)) {
  bad <- audit %>% filter(!match)
  print(bad, n = Inf)
  stop("Numeric audit found mismatches. See reproduced/checks/numeric_claim_audit.csv", call. = FALSE)
} else {
  message("Numeric audit passed: ", nrow(audit), " rounded claims match expected paper values.")
}
