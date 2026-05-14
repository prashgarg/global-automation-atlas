message("Rebuilding selected figures from source data...")

country <- read_csv_here("outputs/source_data/country_map/scatter_exposed_share_vs_log_gdp_pc.csv") %>%
  mutate(income_level = factor(income_level, levels = income_order))

p_country_scatter <- ggplot(country, aes(log_gdp_per_capita, 100 * share_exposed, color = income_level, size = share_high_exposure)) +
  geom_point(alpha = 0.82) +
  geom_smooth(
    data = country,
    aes(log_gdp_per_capita, 100 * share_exposed),
    inherit.aes = FALSE,
    method = "loess",
    se = TRUE,
    color = "#222222",
    linewidth = 0.6,
    fill = "grey70"
  ) +
  scale_color_manual(values = income_cols, drop = FALSE) +
  scale_size_continuous(range = c(1.5, 5), labels = percent_format(accuracy = 1)) +
  labs(x = "Log GDP per capita", y = "Economically exposed task share (%)") +
  theme_paper()
save_pdf(p_country_scatter, "fig_country_opening_scatter_log_nopanel_rebuilt.pdf", 6.8, 4.6)

p_margin_all <- ggplot(country, aes(100 * sub_only_share, 100 * aug_only_share, color = income_level, size = share_exposed)) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "grey55") +
  geom_point(alpha = 0.78) +
  scale_color_manual(values = income_cols, drop = FALSE) +
  scale_size_continuous(range = c(1.5, 5), labels = percent_format(accuracy = 1)) +
  coord_equal() +
  labs(x = "Substitution-only share of all tasks (%)", y = "Augmentation-only share of all tasks (%)") +
  theme_paper()
save_pdf(p_margin_all, "fig_tasks_country_pathways_joint_review_all_tasks_rebuilt.pdf", 6.4, 5.2)

country_within <- country %>%
  mutate(
    sub_within_exposed = sub_only_share / share_exposed,
    aug_within_exposed = aug_only_share / share_exposed
  )
p_margin_within <- ggplot(country_within, aes(100 * sub_within_exposed, 100 * aug_within_exposed, color = income_level, size = share_exposed)) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "grey55") +
  geom_point(alpha = 0.78) +
  scale_color_manual(values = income_cols, drop = FALSE) +
  scale_size_continuous(range = c(1.5, 5), labels = percent_format(accuracy = 1)) +
  coord_equal() +
  labs(x = "Substitution-only share within exposed tasks (%)", y = "Augmentation-only share within exposed tasks (%)") +
  theme_paper()
save_pdf(p_margin_within, "fig_tasks_country_pathways_joint_review_rebuilt.pdf", 6.4, 5.2)

pathway_states <- read_csv_here("outputs/source_data/income_group_pathways/balanced_income_group_state_shares.csv") %>%
  mutate(
    context_label = factor(context_label, levels = income_order),
    state = recode(
      state,
      non_exposed = "Non-exposed",
      sub_only = "Substitution-only",
      both = "Balanced-both",
      aug_only = "Augmentation-only"
    ),
    state = factor(state, levels = c("Non-exposed", "Substitution-only", "Balanced-both", "Augmentation-only"))
  )
p_pathway_flow <- ggplot(pathway_states, aes(context_label, 100 * share, fill = state)) +
  geom_col(width = 0.72, color = "white", linewidth = 0.15) +
  scale_fill_manual(values = c(
    "Non-exposed" = "grey82",
    "Substitution-only" = "#C95F5A",
    "Balanced-both" = "#D1A552",
    "Augmentation-only" = "#548C90"
  )) +
  labs(x = NULL, y = "Share of common task universe (%)") +
  theme_paper(9) +
  theme(axis.text.x = element_text(angle = 20, hjust = 1))
save_pdf(p_pathway_flow, "fig_income_group_pathway_modal_alluvial_main_rebuilt.pdf", 6.4, 4.2)

channel <- read_csv_here("outputs/source_data/channel_ai/country_channel_ai_panel.csv") %>%
  mutate(income_level = factor(income_level, levels = income_order))

p_ai <- ggplot(channel, aes(log_gdp_per_capita, 100 * ai_material_share_exposed, color = income_level)) +
  geom_point(alpha = 0.75, size = 2) +
  geom_smooth(
    data = channel,
    aes(log_gdp_per_capita, 100 * ai_material_share_exposed),
    inherit.aes = FALSE,
    method = "loess",
    se = TRUE,
    color = "#222222",
    linewidth = 0.6,
    fill = "grey70"
  ) +
  scale_color_manual(values = income_cols, drop = FALSE) +
  labs(x = "Log GDP per capita", y = "AI-material share among exposed tasks (%)") +
  theme_paper()
save_pdf(p_ai, "fig_ai_materiality_income_rebuilt.pdf", 6.8, 4.6)

channel_long <- channel %>%
  select(
    iso3, income_level, log_gdp_per_capita,
    physical_execution_share_exposed,
    rule_based_workflow_share_exposed,
    planning_control_share_exposed,
    informational_transformation_share_exposed,
    inference_scoring_share_exposed
  ) %>%
  pivot_longer(
    ends_with("_share_exposed"),
    names_to = "channel",
    values_to = "share"
  ) %>%
  mutate(
    channel = recode(
      channel,
      physical_execution_share_exposed = "Physical execution",
      rule_based_workflow_share_exposed = "Rule-based workflow",
      planning_control_share_exposed = "Planning/control",
      informational_transformation_share_exposed = "Information transformation",
      inference_scoring_share_exposed = "Inference/scoring"
    )
  )
p_channel <- ggplot(channel_long, aes(log_gdp_per_capita, 100 * share, color = channel)) +
  geom_smooth(se = FALSE, method = "loess", linewidth = 0.8) +
  labs(x = "Log GDP per capita", y = "Share of exposed tasks (%)") +
  theme_paper(9)
save_pdf(p_channel, "fig_channel_shares_income_rebuilt.pdf", 7.2, 4.8)

channel_mat <- channel %>%
  summarise(
    `Physical execution` = weighted.mean(physical_execution_share_exposed, exposed_count, na.rm = TRUE),
    `Rule-based workflow` = weighted.mean(rule_based_workflow_share_exposed, exposed_count, na.rm = TRUE),
    `Planning/control` = weighted.mean(planning_control_share_exposed, exposed_count, na.rm = TRUE),
    `Information transformation` = weighted.mean(informational_transformation_share_exposed, exposed_count, na.rm = TRUE),
    `Inference/scoring` = weighted.mean(inference_scoring_share_exposed, exposed_count, na.rm = TRUE)
  ) %>%
  pivot_longer(everything(), names_to = "channel", values_to = "share_exposed")
channel_ai_by_channel <- channel_long %>%
  group_by(channel) %>%
  summarise(mean_share = mean(share, na.rm = TRUE), .groups = "drop") %>%
  left_join(channel_mat, by = "channel")
p_channel_ai_bar <- ggplot(channel_ai_by_channel, aes(100 * share_exposed, reorder(channel, share_exposed))) +
  geom_col(fill = "#548C90", width = 0.68) +
  labs(x = "Average share of exposed tasks (%)", y = NULL) +
  theme_paper(9)

pdf(file.path(pkg_root, "reproduced/figures/fig_channel_ai_mechanism_rebuilt.pdf"), width = 7.2, height = 4.8)
print(p_channel)
print(p_channel_ai_bar)
dev.off()

ai_function <- read_csv_here("outputs/source_data/channel_ai/region_ai_function_summary.csv") %>%
  rename(weight_countries = countries) %>%
  group_by(income_level) %>%
  summarise(
    countries = sum(weight_countries, na.rm = TRUE),
    `Content transformation` = weighted.mean(learned_content_transformation, weight_countries, na.rm = TRUE),
    `State inference` = weighted.mean(learned_state_inference, weight_countries, na.rm = TRUE),
    `Recommendation/decision` = weighted.mean(learned_recommendation_decision, weight_countries, na.rm = TRUE),
    `Adaptive control` = weighted.mean(learned_adaptive_control, weight_countries, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(income_level = factor(income_level, levels = income_order)) %>%
  pivot_longer(-c(income_level, countries), names_to = "ai_function", values_to = "share")
p_ai_function <- ggplot(ai_function, aes(income_level, 100 * share, fill = ai_function)) +
  geom_col(width = 0.72, color = "white", linewidth = 0.15) +
  labs(x = NULL, y = "Share of AI-material exposed tasks (%)") +
  theme_paper(9) +
  theme(axis.text.x = element_text(angle = 20, hjust = 1))

p_ai_sub <- ggplot(channel, aes(100 * ai_material_share_exposed, 100 * non_substitution_share_exposed, color = income_level)) +
  geom_point(alpha = 0.78, size = 2) +
  geom_smooth(data = channel, aes(100 * ai_material_share_exposed, 100 * non_substitution_share_exposed), inherit.aes = FALSE, method = "loess", se = TRUE, color = "#222222", linewidth = 0.6, fill = "grey75") +
  scale_color_manual(values = income_cols, drop = FALSE) +
  labs(x = "AI-material share among exposed tasks (%)", y = "Non-substitution share among exposed tasks (%)") +
  theme_paper()

country_within_ai <- country_within %>%
  left_join(channel %>% select(iso3, ai_material_share_exposed), by = "iso3")
p_ai_aug <- ggplot(country_within_ai, aes(100 * ai_material_share_exposed, 100 * aug_within_exposed, color = income_level)) +
  geom_point(alpha = 0.78, size = 2) +
  geom_smooth(aes(group = 1), method = "loess", se = TRUE, color = "#222222", linewidth = 0.6, fill = "grey75") +
  scale_color_manual(values = income_cols, drop = FALSE) +
  labs(x = "AI-material share among exposed tasks (%)", y = "Augmentation-only share within exposed tasks (%)") +
  theme_paper()

pdf(file.path(pkg_root, "reproduced/figures/fig_ai_materiality_margins_2x2_rebuilt.pdf"), width = 7.2, height = 4.8)
print(p_ai)
print(p_ai_function)
print(p_ai_sub)
print(p_ai_aug)
dev.off()

shap <- read_csv_here("outputs/source_data/country_predictors/country_covariate_rf_mean_abs_shap.csv") %>%
  filter(spec == "main68", outcome %in% c("share_exposed", "sub_only_within_exposed", "aug_only_within_exposed")) %>%
  group_by(outcome) %>%
  slice_max(mean_abs_shap, n = 8, with_ties = FALSE) %>%
  ungroup() %>%
  mutate(variable = gsub("_", " ", variable), outcome = recode(outcome,
    share_exposed = "Exposed share",
    sub_only_within_exposed = "Substitution within exposed",
    aug_only_within_exposed = "Augmentation within exposed"
  ))
p_shap <- ggplot(shap, aes(100 * mean_abs_shap, reorder(variable, mean_abs_shap), fill = direction_flag)) +
  geom_col(width = 0.72) +
  facet_wrap(~outcome, scales = "free_y") +
  scale_fill_manual(values = c(negative = "#C95F5A", positive = "#548C90", mixed = "grey60"), na.value = "grey70") +
  labs(x = "Mean absolute TreeSHAP value (percentage points)", y = NULL) +
  theme_paper(8)
save_pdf(p_shap, "fig_country_covariate_mean_abs_shap_main68_bc_common_axis_rebuilt.pdf", 8.8, 5.2)

perm <- read_csv_here("outputs/source_data/country_predictors/country_covariate_rf_permutation_importance.csv") %>%
  filter(spec == "main68", outcome %in% c("share_exposed", "sub_only_within_exposed", "aug_only_within_exposed")) %>%
  group_by(outcome) %>%
  slice_max(permutation_importance_mean, n = 8, with_ties = FALSE) %>%
  ungroup() %>%
  mutate(variable = gsub("_", " ", variable), outcome = recode(outcome,
    share_exposed = "Exposed share",
    sub_only_within_exposed = "Substitution within exposed",
    aug_only_within_exposed = "Augmentation within exposed"
  ))
p_perm <- ggplot(perm, aes(permutation_importance_mean, reorder(variable, permutation_importance_mean), fill = outcome)) +
  geom_col(width = 0.72, show.legend = FALSE) +
  facet_wrap(~outcome, scales = "free_y") +
  labs(x = "Permutation importance", y = NULL) +
  theme_paper(8)
save_pdf(p_perm, "fig_country_covariate_feature_importance_main68_rebuilt.pdf", 8.8, 5.2)

valid <- read_csv_here("outputs/source_data/construct_validity/channel_aligned_correlations.csv") %>%
  mutate(alignment = if_else(is_aligned, "Matched construct", "Other construct"))
p_valid <- ggplot(valid, aes(pearson, reorder(paste(external, atlas_feature, sep = " - "), pearson), color = alignment)) +
  geom_vline(xintercept = 0, color = "grey70") +
  geom_point(size = 2) +
  scale_color_manual(values = c("Matched construct" = "#548C90", "Other construct" = "grey65")) +
  labs(x = "Pearson correlation", y = NULL) +
  theme_paper(7)
save_pdf(p_valid, "fig_validation_channel_alignment_rebuilt.pdf", 7.0, 6.0)

aipi <- read_csv_here("outputs/source_data/firm_ai_adoption/imf_aipi_atlas_merged.csv") %>%
  filter(!is.na(AI_PI), !is.na(ai_material_share)) %>%
  mutate(income_level = factor(income_level, levels = income_order))
p_aipi <- ggplot(aipi, aes(AI_PI, 100 * ai_material_share, color = income_level)) +
  geom_point(alpha = 0.8, size = 2) +
  geom_smooth(aes(group = 1), method = "lm", se = TRUE, color = "#222222", linewidth = 0.6) +
  scale_color_manual(values = income_cols, drop = FALSE) +
  labs(x = "IMF AI Preparedness Index", y = "AI-material share among exposed tasks (%)") +
  theme_paper()
save_pdf(p_aipi, "fig_validation_imf_aipi_rebuilt.pdf", 6.2, 4.6)

euro <- read_csv_here("outputs/source_data/firm_ai_adoption/eurostat_x_atlas_industry_merged.csv") %>%
  filter(!is.na(ai_any_pct), !is.na(atlas_ai_material_share))
p_euro <- ggplot(euro, aes(100 * atlas_ai_material_share, ai_any_pct)) +
  geom_point(color = "#548C90", alpha = 0.75, size = 1.8) +
  geom_smooth(method = "lm", se = TRUE, color = "#222222", fill = "grey75", linewidth = 0.6) +
  labs(x = "Atlas AI-material industry share (%)", y = "Eurostat firm AI adoption (%)") +
  theme_paper()
save_pdf(p_euro, "fig_validation_eurostat_adoption_rebuilt.pdf", 6.2, 4.6)

cross <- read_csv_here("outputs/source_data/cross_model_validity/agreement_summary.csv")
p_cross <- ggplot(cross, aes(reorder(metric, value), 100 * value)) +
  geom_col(fill = "#548C90", width = 0.65) +
  coord_flip() +
  labs(x = NULL, y = "Agreement (%)") +
  theme_paper()
save_pdf(p_cross, "fig_validation_cross_model_validity_rebuilt.pdf", 5.8, 3.6)

para <- read_csv_here("outputs/source_data/paraphrase_stability/agreement_by_paraphrase.csv") %>%
  pivot_longer(c(binary_exposed, level_exact, level_adjacent, channel_exact, margin_exact), names_to = "metric", values_to = "agreement")
p_para <- ggplot(para, aes(metric, 100 * agreement, group = paraphrase, color = paraphrase)) +
  geom_point(size = 2) +
  geom_line(alpha = 0.75) +
  coord_flip() +
  labs(x = NULL, y = "Agreement (%)") +
  theme_paper(8)
save_pdf(p_para, "fig_validation_paraphrase_stability_rebuilt.pdf", 6.8, 4.2)

rat <- read_csv_here("outputs/source_data/rationale_label_predictability/agreement_summary.csv")
p_rat <- ggplot(rat, aes(reorder(field, value), 100 * value)) +
  geom_col(fill = "#343B54", width = 0.65) +
  coord_flip() +
  labs(x = NULL, y = "Recovered label agreement (%)") +
  theme_paper()
save_pdf(p_rat, "fig_validation_rationale_predictability_rebuilt.pdf", 5.8, 3.4)

occ <- read_csv_here("data_analysis/occupation_isco2_gender_gap_country_panel.csv") %>%
  mutate(domain = "ISCO-2 occupations")
ind <- read_csv_here("data_analysis/industry_isic2_gender_gap_country_panel.csv") %>%
  mutate(domain = "ISIC-2 industries")
gender <- bind_rows(occ, ind) %>%
  mutate(
    income_level = factor(income_level, levels = income_order),
    income_label = as.character(income_level)
  ) %>%
  pivot_longer(c(sub_gap_pp, aug_gap_pp), names_to = "margin", values_to = "gap_pp") %>%
  mutate(margin = recode(margin, sub_gap_pp = "Substitution-only", aug_gap_pp = "Augmentation-only"))
gender_all <- gender %>% mutate(income_label = "All countries")
gender_plot <- bind_rows(gender_all, gender) %>%
  mutate(income_label = factor(income_label, levels = c("All countries", rev(income_order))))
gender_iqr <- gender_plot %>%
  group_by(domain, margin, income_label) %>%
  summarise(median_gap = median(gap_pp, na.rm = TRUE), q25 = quantile(gap_pp, .25, na.rm = TRUE), q75 = quantile(gap_pp, .75, na.rm = TRUE), .groups = "drop")
p_gender <- ggplot(gender_iqr, aes(median_gap, income_label, color = domain)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey55") +
  geom_errorbarh(aes(xmin = q25, xmax = q75), height = 0.15, linewidth = 0.8, position = position_dodge(width = 0.45)) +
  geom_point(size = 2.3, position = position_dodge(width = 0.45)) +
  facet_wrap(~margin, scales = "free_x") +
  scale_color_manual(values = domain_cols) +
  labs(x = "Median female minus male contribution (percentage points)", y = NULL) +
  theme_paper()
save_pdf(p_gender, "fig_gender_gap_2digit_objects_median_iqr_rebuilt.pdf", 8.8, 4.6)
