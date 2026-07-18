#!/usr/bin/env Rscript

message("Running public replication workflow...")

source("code/00_setup.R")
source("code/01_rebuild_tables.R")
source("code/02_rebuild_figures.R")

python_bin <- Sys.getenv("PYTHON", unset = "python3")

run_python <- function(script) {
  status <- system2(python_bin, script)
  if (!identical(status, 0L)) stop("Python reproduction step failed: ", script, call. = FALSE)
}

run_python("code/manuscript_figures/build_current_check_renders.py")
run_python("code/manuscript_figures/build_combined_rf_rationale_main_figure.py")
run_python("code/manuscript_figures/build_fixed_concept_appendix_figures.py")
run_python("code/manuscript_figures/build_openai_observed_use_iwa_validation.py")
run_python("code/manuscript_figures/compare_exact_build_renders.py")

source("code/03_compare_outputs.R")
source("code/04_numeric_audit.R")
source("code/05_rationale_concept_audit.R")
source("code/06_refresh_audit.R")

message("Done. Rebuilt outputs are in reproduced/.")
