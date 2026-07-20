if (!exists("read_parquet_here", inherits = FALSE)) {
  source("code/00_setup.R")
}

message("Auditing the released rationale corpus...")

rationale_dir <- file.path(pkg_root, "data_intermediate/task_country_rationales")
rationale_files <- list.files(
  rationale_dir,
  pattern = "^task_country_rationales_[0-9]{2}\\.parquet$",
  full.names = TRUE
)

if (!length(rationale_files)) {
  stop("No partitioned rationale files found in ", rationale_dir, call. = FALSE)
}

rationales <- open_dataset(rationale_files, format = "parquet") %>%
  select(rationale_row_id, item_id, task_id, iso3, short_rationale) %>%
  collect()

labels <- read_parquet_here("data_intermediate/task_country_labels_analysis.parquet") %>%
  select(item_id, task_id, iso3)

duplicate_keys <- rationales %>%
  count(item_id, name = "n") %>%
  filter(n > 1) %>%
  nrow()

orphan_rows <- anti_join(rationales, labels, by = c("item_id", "task_id", "iso3")) %>%
  nrow()

missing_rows <- anti_join(labels, rationales, by = c("item_id", "task_id", "iso3")) %>%
  nrow()

audit <- tibble(
  metric = c(
    "retained_task_country_labels",
    "nonempty_rationales",
    "labels_without_nonempty_rationale",
    "rationale_coverage_percent",
    "duplicate_rationale_keys",
    "orphan_rationale_rows",
    "partition_files"
  ),
  value = c(
    nrow(labels),
    nrow(rationales),
    missing_rows,
    100 * nrow(rationales) / nrow(labels),
    duplicate_keys,
    orphan_rows,
    length(rationale_files)
  )
)

write_csv(audit, file.path(pkg_root, "reproduced/checks/rationale_corpus_audit.csv"))

if (duplicate_keys != 0L || orphan_rows != 0L || nrow(rationales) != 2320863L ||
    nrow(labels) != 2330776L || missing_rows != 9913L) {
  print(audit, n = Inf)
  stop("Rationale corpus audit failed. See reproduced/checks/rationale_corpus_audit.csv", call. = FALSE)
}

message(
  "Rationale corpus audit passed: ", format(nrow(rationales), big.mark = ","),
  " non-empty rationales covering ", sprintf("%.3f", 100 * nrow(rationales) / nrow(labels)),
  "% of retained labels."
)
