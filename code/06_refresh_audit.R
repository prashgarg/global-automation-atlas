if (!exists("pkg_root", inherits = FALSE)) {
  suppressPackageStartupMessages({library(dplyr); library(readr)})
  pkg_root <- normalizePath(getwd(), mustWork = TRUE)
}

message("Building active-manuscript replication manifest...")

hash_file <- function(path) unname(tools::md5sum(path))
snapshot <- file.path(pkg_root, "docs/main_manuscript_snapshot.tex")
tex <- readLines(snapshot, warn = FALSE)

graphic_lines <- tex[grepl("\\\\includegraphics", tex) & !grepl("^%", trimws(tex))]
graphic_paths <- sub(".*\\\\includegraphics(\\[[^]]*\\])?\\{([^}]*)\\}.*", "\\2", graphic_lines)
graphic_paths <- graphic_paths[nzchar(graphic_paths)]
figure_names <- unique(basename(graphic_paths))

input_lines <- tex[grepl("\\\\input\\{02_Tables", tex) & !grepl("^%", trimws(tex))]
table_paths <- sub(".*\\\\input\\{([^}]*)\\}.*", "\\1", input_lines)
table_names <- unique(basename(paste0(table_paths, ifelse(grepl("\\.tex$", table_paths), "", ".tex"))))

figure_registry <- read_csv(file.path(pkg_root, "docs/figure_asset_registry.csv"), show_col_types = FALSE)
missing_registry <- setdiff(figure_names, figure_registry$manuscript_figure)
inactive_registry <- setdiff(figure_registry$manuscript_figure, figure_names)
if (length(missing_registry) || length(inactive_registry)) {
  stop(
    "Figure registry does not equal active manuscript figures. Missing: ",
    paste(missing_registry, collapse = ", "), "; inactive: ",
    paste(inactive_registry, collapse = ", "), call. = FALSE
  )
}

figure_rows <- tibble(manuscript_figure = figure_names) %>%
  left_join(figure_registry, by = "manuscript_figure") %>%
  transmute(
    asset_type = "figure",
    manuscript_asset = file.path("01_Figures/refresh_country124_20260406", manuscript_figure),
    package_asset = file.path("outputs/figures", manuscript_figure),
    replication_command,
    reproduction_class,
    expected_hash = vapply(file.path(pkg_root, "outputs/figures", manuscript_figure), function(path) {
      if (file.exists(path)) hash_file(path) else NA_character_
    }, character(1)),
    expected_statistics,
    source_data = included_public_source_files,
    rebuilt_file,
    original_production_script,
    blocker_or_rendering_note
  )

table_rows <- tibble(
  asset_type = "input_table",
  manuscript_asset = table_paths,
  package_asset = file.path("outputs/tables", table_names),
  replication_command = "Rscript code/make_all.R",
  reproduction_class = "exact_reference_snapshot_or_rebuilt_check",
  expected_hash = vapply(file.path(pkg_root, "outputs/tables", table_names), function(path) {
    if (file.exists(path)) hash_file(path) else NA_character_
  }, character(1)),
  expected_statistics = NA_character_,
  source_data = "See docs/provenance/REFRESH_PROVENANCE.md"
)

inline_rows <- tibble(
  asset_type = "inline_table",
  manuscript_asset = "main.tex (seven active inline tables, including corrected Table B.8)",
  package_asset = "docs/main_manuscript_snapshot.tex; outputs/tables/tabS_ilostat_gender_fe_baseline.tex",
  replication_command = "Rscript code/01_rebuild_tables.R",
  reproduction_class = "snapshot_plus_rebuilt_gender_FE_check",
  expected_hash = hash_file(snapshot),
  expected_statistics = "Corrected B.8 coefficients: -0.338, 0.140, -0.227, 0.015",
  source_data = "outputs/source_data/ilostat_gender/gender_fe_table_current.csv"
)

numeric_path <- file.path(pkg_root, "reproduced/checks/numeric_claim_audit.csv")
numeric_rows <- if (file.exists(numeric_path)) {
  read_csv(numeric_path, show_col_types = FALSE) %>%
    transmute(
      asset_type = "reported_statistic",
      manuscript_asset = paste(section, claim, sep = ": "),
      package_asset = "reproduced/checks/numeric_claim_audit.csv",
      replication_command = "Rscript code/04_numeric_audit.R",
      reproduction_class = "numeric_rebuild",
      expected_hash = NA_character_,
      expected_statistics = as.character(expected_paper_value),
      source_data = "See numeric_claim_audit.csv source columns"
    )
} else tibble()

rationale_path <- file.path(pkg_root, "reproduced/checks/rationale_hypothesaes_audit.csv")
rationale_rows <- if (file.exists(rationale_path)) {
  read_csv(rationale_path, show_col_types = FALSE) %>%
    transmute(
      asset_type = "rationale_hypothesaes_contrast",
      manuscript_asset = target_name,
      package_asset = "reproduced/checks/rationale_hypothesaes_audit.csv",
      replication_command = "Rscript code/05_rationale_concept_audit.R",
      reproduction_class = "heldout_paired_estimator_audit",
      expected_hash = NA_character_,
      expected_statistics = paste0("20 concepts; 2,000 pairs; source significant=", source_bonferroni_significant,
                                   "; manuscript significant=", manuscript_significant),
      source_data = "outputs/source_data/rationale_concepts/current_paper/full_fixed_concept_appendix_figure_source.csv"
    )
} else tibble()

manifest <- bind_rows(figure_rows, table_rows, inline_rows, numeric_rows, rationale_rows)
write_csv(manifest, file.path(pkg_root, "manifest.csv"))
write_csv(manifest, file.path(pkg_root, "reproduced/checks/active_manuscript_asset_manifest.csv"))

missing <- manifest %>%
  filter(asset_type %in% c("figure", "input_table"), !file.exists(file.path(pkg_root, package_asset)))
if (nrow(missing)) {
  print(missing, n = Inf)
  stop("Manifest points to missing package artifacts.", call. = FALSE)
}

active_root <- Sys.getenv("ACTIVE_MANUSCRIPT_ROOT", unset = "")
if (nzchar(active_root)) {
  active_root <- normalizePath(active_root, mustWork = TRUE)

  compare_snapshots <- function(rows, output_file) {
    check <- rows %>%
      mutate(
        paper_rel = if_else(
          grepl("\\.[A-Za-z0-9]+$", manuscript_asset),
          manuscript_asset,
          paste0(manuscript_asset, ".tex")
        )
      ) %>%
      transmute(
        file = basename(manuscript_asset),
        paper_path = file.path(active_root, paper_rel),
        package_path = file.path(pkg_root, package_asset),
        paper_exists = file.exists(paper_path),
        package_exists = file.exists(package_path),
        paper_md5 = if_else(paper_exists, vapply(paper_path, hash_file, character(1)), NA_character_),
        package_md5 = if_else(package_exists, vapply(package_path, hash_file, character(1)), NA_character_),
        exact_match = paper_exists & package_exists & paper_md5 == package_md5
      ) %>%
      select(file, paper_exists, package_exists, paper_md5, package_md5, exact_match)

    write_csv(check, file.path(pkg_root, "reproduced/checks", output_file))
    if (!all(check$exact_match)) {
      print(filter(check, !exact_match), n = Inf)
      stop("Active manuscript artifacts differ from package snapshots.", call. = FALSE)
    }
    check
  }

  figure_check <- compare_snapshots(
    figure_rows,
    "manuscript_figure_artifact_exact_match.csv"
  )
  table_check <- compare_snapshots(
    table_rows,
    "manuscript_table_artifact_exact_match.csv"
  )
  message(
    "Exact snapshot checks passed for ", nrow(figure_check), " figures and ",
    nrow(table_check), " file-backed tables."
  )
}

message("Manifest written with ", nrow(manifest), " rows and ", nrow(figure_rows), " active figures.")
