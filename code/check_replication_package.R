suppressPackageStartupMessages({library(arrow); library(readr)})
root <- normalizePath(file.path(getwd()), mustWork = TRUE)
required <- c(
  'data_intermediate/task_country_labels_analysis.parquet',
  'data_intermediate/task_country_rationales/rationale_corpus_summary.csv',
  'data_intermediate/task_metadata.csv',
  'data_intermediate/country_metadata.csv',
  'prompts/country_conditioned_prompt.md',
  'outputs/figures/fig3_map_share_exposed.png',
  'outputs/tables/tab1_data_inventory.tex',
  'outputs/source_data/rationale_concepts/current_paper/full_fixed_concept_appendix_figure_source.csv',
  'outputs/source_data/rationale_concepts/current_paper/rf_companion_rationale_panel_source.csv',
  'outputs/source_data/rationale_concepts/rationale_examples_table_source.csv',
  'outputs/source_data/ilostat_gender/gender_fe_table_current.csv',
  'outputs/source_data/ilostat_gender/table_B8_inputs/ilostat_sex_isco2_latest_weights.csv',
  'outputs/source_data/ilostat_gender/table_B8_inputs/atlas_country_isco2_panel.csv',
  'outputs/source_data/ilostat_gender/table_B8_inputs/ilostat_sex_isic2_latest_weights.csv',
  'outputs/source_data/ilostat_gender/table_B8_inputs/atlas_country_isic2_panel.csv',
  'outputs/source_data/ilostat_gender/gender_gap_decomposition_by_income.csv',
  'outputs/source_data/ilostat_gender/gender_gap_decomposition_country_level.csv',
  'outputs/source_data/informality/informality_country_regressions.csv',
  'outputs/source_data/openai_observed_use/onet_task_hierarchy.csv',
  'outputs/source_data/openai_observed_use/usa_share_of_messages_by_onet_iwa_month.csv',
  'outputs/source_data/openai_observed_use/usa_share_of_work_related_messages_by_onet_iwa_month.csv',
  'docs/main_manuscript_snapshot.tex',
  'docs/figure_asset_registry.csv'
)
required <- c(
  required,
  file.path(
    'data_intermediate/task_country_rationales',
    sprintf('task_country_rationales_%02d.parquet', 1:8)
  )
)
missing <- required[!file.exists(file.path(root, required))]
if (length(missing)) stop('Missing required files: ', paste(missing, collapse=', '))
labels <- read_parquet(file.path(root, 'data_intermediate/task_country_labels_analysis.parquet'), as_data_frame = TRUE)
cat('Task-country labels:', nrow(labels), 'rows; ', length(unique(labels$iso3)), 'countries; ', length(unique(labels$task_id)), 'tasks\n', sep='')
rationale_summary <- read_csv(
  file.path(root, 'data_intermediate/task_country_rationales/rationale_corpus_summary.csv'),
  show_col_types = FALSE
)
cat(
  'Non-empty rationales:', rationale_summary$value[rationale_summary$metric == 'nonempty_rationales'],
  'rows in ', rationale_summary$value[rationale_summary$metric == 'partition_files'],
  'partitions\n'
)
cat('Figures:', length(list.files(file.path(root, 'outputs/figures'), recursive=TRUE)), '\n')
cat('Tables:', length(list.files(file.path(root, 'outputs/tables'), recursive=TRUE)), '\n')
paper_concepts <- read_csv(file.path(root, 'outputs/source_data/rationale_concepts/current_paper/full_fixed_concept_appendix_figure_source.csv'), show_col_types = FALSE)
cat('Current-paper rationale concepts:', nrow(paper_concepts), 'across ', length(unique(paper_concepts$target_name)), ' heldout contrasts\n', sep='')
