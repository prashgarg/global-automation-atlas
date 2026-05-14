message("Writing reproduction status table...")

final_figures <- list.files(file.path(pkg_root, "outputs/figures"), pattern = "\\.(pdf|png)$", full.names = FALSE)
rebuilt_figures <- list.files(file.path(pkg_root, "reproduced/figures"), pattern = "\\.pdf$", full.names = FALSE)

rebuilt_base <- gsub("_rebuilt\\.pdf$", "", rebuilt_figures)
final_base <- tools::file_path_sans_ext(final_figures)

status <- tibble(
  manuscript_figure = final_figures,
  reproduction_status = if_else(final_base %in% rebuilt_base, "rebuilt_from_source_data", "preserved_final_artifact"),
  rebuilt_file = if_else(
    final_base %in% rebuilt_base,
    paste0(final_base, "_rebuilt.pdf"),
    NA_character_
  )
)

write_csv(status, file.path(pkg_root, "reproduced/checks/figure_reproduction_status.csv"))

table_status <- tibble(
  manuscript_tables = list.files(file.path(pkg_root, "outputs/tables"), pattern = "\\.tex$", full.names = FALSE),
  reproduction_status = "preserved_latex_artifact"
)
write_csv(table_status, file.path(pkg_root, "reproduced/checks/table_reproduction_status.csv"))

cat("Rebuilt figures:", sum(status$reproduction_status == "rebuilt_from_source_data"), "\n")
cat("Preserved final figure artifacts:", sum(status$reproduction_status == "preserved_final_artifact"), "\n")
