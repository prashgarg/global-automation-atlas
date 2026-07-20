if (!exists("read_csv_here", inherits = FALSE)) {
  source("code/00_setup.R")
}

if (!requireNamespace("fixest", quietly = TRUE)) {
  stop("Package 'fixest' is required to rebuild Supplementary Table B.8.", call. = FALSE)
}

message("Re-estimating Supplementary Table B.8...")

input_dir <- "outputs/source_data/ilostat_gender/table_B8_inputs"
income_groups <- c(
  "Low income", "Lower middle income", "Upper middle income", "High income"
)

make_panel <- function(domain) {
  if (domain == "occupation") {
    weights <- read_csv_here(file.path(input_dir, "ilostat_sex_isco2_latest_weights.csv")) %>%
      mutate(code = stringr::str_pad(as.character(code), 2, side = "left", pad = "0"))
    atlas <- read_csv_here(file.path(input_dir, "atlas_country_isco2_panel.csv")) %>%
      mutate(code = stringr::str_pad(as.character(isco2), 2, side = "left", pad = "0")) %>%
      transmute(iso3, country_name, income_level, code, substitution = sub, augmentation = aug)
    domain_label <- "ISCO-2 occupations"
    expected_countries <- 88L
    expected_cells <- 42L
  } else {
    weights <- read_csv_here(file.path(input_dir, "ilostat_sex_isic2_latest_weights.csv")) %>%
      mutate(code = as.character(as.integer(code)))
    atlas <- read_csv_here(file.path(input_dir, "atlas_country_isic2_panel.csv")) %>%
      transmute(
        iso3, country_name, income_level,
        code = as.character(as.integer(isic2)),
        substitution = sub,
        augmentation = aug
      )
    domain_label <- "ISIC-2 industries"
    expected_countries <- 72L
    expected_cells <- 88L
  }

  panel <- weights %>%
    inner_join(atlas, by = c("iso3", "code")) %>%
    filter(income_level %in% income_groups) %>%
    select(
      iso3, country_name, income_level, ilostat_year,
      sex, cell = code, employment_share = share,
      substitution, augmentation
    ) %>%
    pivot_wider(
      id_cols = c(
        iso3, country_name, income_level, ilostat_year,
        cell, substitution, augmentation
      ),
      names_from = sex,
      values_from = employment_share
    ) %>%
    drop_na(SEX_F, SEX_M) %>%
    group_by(iso3) %>%
    mutate(
      female_share_common = SEX_F / sum(SEX_F),
      male_share_common = SEX_M / sum(SEX_M),
      female_minus_male_share_pp = 100 * (female_share_common - male_share_common)
    ) %>%
    ungroup() %>%
    mutate(domain = domain_label)

  stopifnot(!anyDuplicated(panel[c("iso3", "cell")]))
  stopifnot(n_distinct(panel$iso3) == expected_countries)
  stopifnot(n_distinct(panel$cell) == expected_cells)
  panel
}

estimate_margin <- function(panel, margin, variable) {
  model_data <- panel %>%
    mutate(
      outcome = female_minus_male_share_pp,
      exposure_10pp = 10 * .data[[variable]]
    )
  fit <- fixest::feols(outcome ~ exposure_10pp | iso3 + cell, data = model_data, cluster = ~iso3)
  estimate <- fixest::coeftable(fit)["exposure_10pp", ]
  tibble(
    domain = first(panel$domain),
    margin = margin,
    coefficient = unname(estimate["Estimate"]),
    standard_error = unname(estimate["Std. Error"]),
    t_statistic = unname(estimate["t value"]),
    p_value = unname(estimate["Pr(>|t|)"]),
    observations = nrow(model_data),
    countries = n_distinct(model_data$iso3),
    cells = n_distinct(model_data$cell),
    country_fixed_effects = "Yes",
    cell_fixed_effects = "Yes",
    normalization = "Common cells within country and sex",
    sample = "Countries classified in the four World Bank income groups"
  )
}

occupation_panel <- make_panel("occupation")
industry_panel <- make_panel("industry")
results <- bind_rows(
  estimate_margin(occupation_panel, "Substitution-only", "substitution"),
  estimate_margin(occupation_panel, "Augmentation-only", "augmentation"),
  estimate_margin(industry_panel, "Substitution-only", "substitution"),
  estimate_margin(industry_panel, "Augmentation-only", "augmentation")
)

released <- read_csv_here("outputs/source_data/ilostat_gender/gender_fe_table_current.csv")
comparison <- results %>%
  select(domain, margin, coefficient, standard_error, p_value, observations, countries, cells) %>%
  left_join(
    released %>% select(
      domain, margin,
      released_coefficient = coefficient,
      released_standard_error = standard_error,
      released_p_value = p_value,
      released_observations = observations,
      released_countries = countries,
      released_cells = cells
    ),
    by = c("domain", "margin")
  ) %>%
  mutate(
    coefficient_match = abs(coefficient - released_coefficient) < 1e-10,
    standard_error_match = abs(standard_error - released_standard_error) < 1e-10,
    sample_match = observations == released_observations &
      countries == released_countries & cells == released_cells
  )

write_csv(results, file.path(pkg_root, "reproduced/tables/gender_table_B8_reestimated.csv"))
write_csv(comparison, file.path(pkg_root, "reproduced/checks/gender_table_B8_reestimation_check.csv"))

if (any(!comparison$coefficient_match | !comparison$standard_error_match | !comparison$sample_match)) {
  print(comparison, n = Inf)
  stop("Supplementary Table B.8 re-estimation does not match the released table.", call. = FALSE)
}

message("Supplementary Table B.8 re-estimation matches the released coefficients and standard errors.")
