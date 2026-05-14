message("Rebuilding summary tables...")

labels <- read_parquet_here("data_intermediate/task_country_labels_analysis.parquet")
country_map <- read_csv_here("data_analysis/country_map_panel.csv")

core_counts <- tibble(
  object = c("Task-country labels", "Countries", "Tasks", "Economically exposed label rows"),
  value = c(
    nrow(labels),
    n_distinct(labels$iso3),
    n_distinct(labels$task_id),
    sum(labels$economic_exposed, na.rm = TRUE)
  )
)
write_csv(core_counts, file.path(pkg_root, "reproduced/tables/core_counts.csv"))

country_opening_summary <- country_map %>%
  mutate(income_level = factor(income_level, levels = income_order)) %>%
  group_by(income_level) %>%
  summarise(
    countries = n(),
    median_exposed_share = median(share_exposed, na.rm = TRUE),
    mean_exposed_share = mean(share_exposed, na.rm = TRUE),
    median_high_exposure_share = median(share_high_exposure, na.rm = TRUE),
    .groups = "drop"
  )
write_csv(country_opening_summary, file.path(pkg_root, "reproduced/tables/country_opening_summary_rebuilt.csv"))

validation_channels <- read_csv_here("outputs/source_data/construct_validity/channel_aligned_correlations.csv") %>%
  filter(is_aligned) %>%
  arrange(desc(pearson))
write_csv(validation_channels, file.path(pkg_root, "reproduced/tables/validation_channel_aligned_correlations_rebuilt.csv"))

gender_fe <- read_csv_here("data_analysis/gender_fe_regression_table.csv") %>%
  filter(model == "Baseline", term == "x")
write_csv(gender_fe, file.path(pkg_root, "reproduced/tables/gender_fe_regression_table_rebuilt.csv"))

gender_fe_tex <- c(
  "\\begin{tabular}{lrrrr}",
  "\\toprule",
  "Domain & Margin & Coefficient & SE & p-value \\\\",
  "\\midrule",
  apply(gender_fe, 1, function(r) {
    paste0(
      r[["domain"]], " & ", r[["margin"]], " & ",
      sprintf("%.3f", as.numeric(r[["coef"]])), " & ",
      sprintf("%.3f", as.numeric(r[["se"]])), " & ",
      sprintf("%.3f", as.numeric(r[["pvalue"]])), " \\\\"
    )
  }),
  "\\bottomrule",
  "\\end{tabular}"
)
writeLines(gender_fe_tex, file.path(pkg_root, "reproduced/tables/gender_fe_regression_table_rebuilt.tex"))
