if (!exists("pkg_root", inherits = FALSE)) {
  source("code/00_setup.R")
}

message("Writing active-figure reproduction status from the explicit registry...")

hash_file <- function(path) unname(tools::md5sum(path))
registry <- read_csv_here("docs/figure_asset_registry.csv")
snapshot <- readLines(file.path(pkg_root, "docs/main_manuscript_snapshot.tex"), warn = FALSE)
graphic_lines <- snapshot[grepl("\\\\includegraphics", snapshot) & !grepl("^%", trimws(snapshot))]
graphic_paths <- sub(".*\\\\includegraphics(\\[[^]]*\\])?\\{([^}]*)\\}.*", "\\2", graphic_lines)
active_figures <- unique(basename(graphic_paths[nzchar(graphic_paths)]))

missing_registry <- setdiff(active_figures, registry$manuscript_figure)
inactive_registry <- setdiff(registry$manuscript_figure, active_figures)
if (length(missing_registry) || length(inactive_registry)) {
  stop(
    "Figure registry does not equal the active manuscript set. Missing: ",
    paste(missing_registry, collapse = ", "), "; inactive: ",
    paste(inactive_registry, collapse = ", "), call. = FALSE
  )
}

valid_classes <- c(
  "exact_reproducible_build",
  "numerical_source_data_check_render",
  "snapshot_only_due_to_missing_source_inputs"
)
if (any(!registry$reproduction_class %in% valid_classes)) {
  stop("Registry contains an unsupported reproduction class.", call. = FALSE)
}

source_exists <- function(value) {
  if (is.na(value) || !nzchar(value)) return(TRUE)
  paths <- trimws(strsplit(value, ";", fixed = TRUE)[[1]])
  all(file.exists(file.path(pkg_root, paths)))
}

status <- tibble(manuscript_figure = active_figures) %>%
  left_join(registry, by = "manuscript_figure") %>%
  mutate(
    snapshot_file = file.path("outputs/figures", manuscript_figure),
    snapshot_exists = file.exists(file.path(pkg_root, snapshot_file)),
    snapshot_md5 = vapply(file.path(pkg_root, snapshot_file), hash_file, character(1)),
    rebuilt_exists = if_else(
      is.na(rebuilt_file),
      NA,
      file.exists(file.path(pkg_root, "reproduced/figures", rebuilt_file))
    ),
    rebuilt_md5 = vapply(rebuilt_file, function(filename) {
      if (is.na(filename) || !nzchar(filename)) return(NA_character_)
      path <- file.path(pkg_root, "reproduced/figures", filename)
      if (file.exists(path)) hash_file(path) else NA_character_
    }, character(1)),
    included_sources_exist = vapply(included_public_source_files, source_exists, logical(1))
  )

if (!all(status$snapshot_exists)) stop("An active reference snapshot is missing.", call. = FALSE)
if (any(status$reproduction_class != valid_classes[3] & !status$rebuilt_exists)) {
  print(filter(status, reproduction_class != valid_classes[3], !rebuilt_exists), n = Inf)
  stop("A declared rebuilt/check-render figure is missing.", call. = FALSE)
}
if (!all(status$included_sources_exist)) {
  print(filter(status, !included_sources_exist), n = Inf)
  stop("A declared public source file is missing.", call. = FALSE)
}

write_csv(status, file.path(pkg_root, "reproduced/checks/figure_reproduction_status.csv"))

table_status <- tibble(
  manuscript_tables = list.files(file.path(pkg_root, "outputs/tables"), pattern = "\\.tex$", full.names = FALSE),
  reproduction_status = "exact_reference_snapshot_or_declared_numeric_check"
)
write_csv(table_status, file.path(pkg_root, "reproduced/checks/table_reproduction_status.csv"))

print(count(status, reproduction_class, name = "active_figures"), n = Inf)
