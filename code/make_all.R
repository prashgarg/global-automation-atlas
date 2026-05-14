#!/usr/bin/env Rscript

message("Running public replication workflow...")

source("code/00_setup.R")
source("code/01_rebuild_tables.R")
source("code/02_rebuild_figures.R")
source("code/03_compare_outputs.R")
source("code/04_numeric_audit.R")

message("Done. Rebuilt outputs are in reproduced/.")
