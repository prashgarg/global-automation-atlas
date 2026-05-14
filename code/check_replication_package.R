suppressPackageStartupMessages({library(arrow); library(readr)})
root <- normalizePath(file.path(getwd()), mustWork = TRUE)
required <- c(
  'data_intermediate/task_country_labels_analysis.parquet',
  'data_intermediate/task_metadata.csv',
  'data_intermediate/country_metadata.csv',
  'prompts/country_conditioned_prompt.md',
  'outputs/figures/fig3_map_share_exposed.png',
  'outputs/tables/tab1_data_inventory.tex'
)
missing <- required[!file.exists(file.path(root, required))]
if (length(missing)) stop('Missing required files: ', paste(missing, collapse=', '))
labels <- read_parquet(file.path(root, 'data_intermediate/task_country_labels_analysis.parquet'), as_data_frame = TRUE)
cat('Task-country labels:', nrow(labels), 'rows; ', length(unique(labels$iso3)), 'countries; ', length(unique(labels$task_id)), 'tasks\n', sep='')
cat('Figures:', length(list.files(file.path(root, 'outputs/figures'), recursive=TRUE)), '\n')
cat('Tables:', length(list.files(file.path(root, 'outputs/tables'), recursive=TRUE)), '\n')

