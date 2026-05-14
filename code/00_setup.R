suppressPackageStartupMessages({
  library(arrow)
  library(dplyr)
  library(readr)
  library(tidyr)
  library(ggplot2)
  library(scales)
})

pkg_root <- normalizePath(getwd(), mustWork = TRUE)
dir.create(file.path(pkg_root, "reproduced/figures"), recursive = TRUE, showWarnings = FALSE)
dir.create(file.path(pkg_root, "reproduced/tables"), recursive = TRUE, showWarnings = FALSE)
dir.create(file.path(pkg_root, "reproduced/checks"), recursive = TRUE, showWarnings = FALSE)

income_order <- c("Low income", "Lower middle income", "Upper middle income", "High income")
income_cols <- c(
  "Low income" = "#C95F5A",
  "Lower middle income" = "#7EA56B",
  "Upper middle income" = "#D1A552",
  "High income" = "#5F82A3"
)
domain_cols <- c("ISCO-2 occupations" = "#548C90", "ISIC-2 industries" = "#343B54")

theme_paper <- function(base_size = 10) {
  theme_minimal(base_size = base_size) +
    theme(
      panel.grid.minor = element_blank(),
      plot.title = element_blank(),
      axis.title = element_text(color = "#243447"),
      axis.text = element_text(color = "#546676"),
      legend.title = element_blank(),
      legend.position = "bottom"
    )
}

save_pdf <- function(plot, filename, width = 7.2, height = 4.8) {
  ggsave(
    filename = file.path(pkg_root, "reproduced/figures", filename),
    plot = plot,
    width = width,
    height = height,
    device = cairo_pdf
  )
}

read_csv_here <- function(path) read_csv(file.path(pkg_root, path), show_col_types = FALSE)
read_parquet_here <- function(path) read_parquet(file.path(pkg_root, path), as_data_frame = TRUE)
