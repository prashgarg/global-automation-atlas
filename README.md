# Global Automation Atlas replication package

This repository contains the public replication package for **Global Automation Atlas** by Prashant Garg, Tommaso Crosta, and Jasmin Baier.

The accompanying online atlas is available at [automationatlas.org](https://automationatlas.org/). It provides country-, occupation-, industry-, and task-level exposure measures, with documentation and downloadable data.

This package contains the data and code needed to check the results reported in the paper. It starts from the retained task-country labels used in the analysis and rebuilds the downstream checks, tables, and selected figures from those fixed labels.

If you use this package, please cite the paper and this repository. Citation metadata are provided in `CITATION.cff`.

The package does not include exploratory drafts, old figure variants, raw API logs, or language-model rationales. Those files are not needed to reproduce the paper results and would make the release harder to use.

## Quick start

From the package root, first check that the expected files are present:

```bash
Rscript code/check_replication_package.R
```

Then run the reproduction workflow:

```bash
Rscript code/make_all.R
```

The workflow writes rebuilt files to `reproduced/`. It also runs a numeric audit of paper-presented values. If any audited number fails to match after rounding, the script stops and points to `reproduced/checks/numeric_claim_audit.csv`.

## What the scripts check

- `code/check_replication_package.R` checks the core inventory and prints row counts for the task-country label file.
- `code/make_all.R` rebuilds summary tables and selected figures from the included data.
- `code/04_numeric_audit.R` checks headline values reported in the paper, including country exposure ranges, validation correlations, gender-gap summaries, and fixed-effect coefficients.
- `reproduced/checks/figure_reproduction_status.csv` records which manuscript figures are rebuilt from source data and which are included as final manuscript figure files.

At the time of this package build, the numeric audit checks 53 rounded paper values.

## Folder guide

- `prompts/` contains the country-conditioned, income-group, and context-free prompt protocols, plus model notes.
- `data_intermediate/` contains the retained measurement outputs used downstream. The central file is `task_country_labels_analysis.parquet`, with 2,330,776 task-country observations across 124 countries and 18,797 tasks.
- `data_analysis/` contains smaller panels used directly in the country, channel, predictor, occupation, industry, and gender analyses.
- `outputs/source_data/` contains source data for paper and supplementary figures and tables where a compact source file is available.
- `outputs/figures/` and `outputs/tables/` contain the final manuscript figure and table files copied from the submitted paper folder.
- `reproduced/` is created by `code/make_all.R` and contains rebuilt checks, tables, and figures.
- `docs/data_dictionary/` gives column descriptions and types for the main public data files.
- `data_raw_public_metadata/source_inventory.csv` lists public source datasets and links.

## Language-model labelling step

The package documents the language-model labelling protocol but does not rerun it. The API stage depends on model availability, model versions, and paid external services. For reproducibility, the package supplies the retained labels used in the paper and the prompts needed to inspect the measurement protocol.

The prompt files are:

- `prompts/country_conditioned_prompt.md`
- `prompts/income_group_prompt.md`
- `prompts/context_free_prompt.md`
- `prompts/model_config.json`

The retained label file excludes rationales. It keeps only the columns needed for the paper analyses: exposure level, labour margin, channel, AI materiality, AI function, country identifiers, and task identifiers.

## Data dictionaries

The main dictionary is `docs/data_dictionary/schema_with_descriptions.csv`. It reports file names, column names, inferred column types, and descriptions for the main files in `data_intermediate/` and `data_analysis/`. A shorter hand-written dictionary is also available at `docs/data_dictionary/data_dictionary.csv`.

## Figure and table reproduction

The package contains two kinds of figure files.

First, `outputs/figures/` contains the exact figure files used by the paper. These files are included so that readers can recover the submitted visual evidence exactly.

Second, `reproduced/figures/` contains figures rebuilt from the included source data. These rebuilt figures check the underlying numbers but are not meant to be pixel-identical to the designed manuscript figures. The file `reproduced/checks/figure_reproduction_status.csv` identifies the status of each manuscript figure.

The same logic applies to tables. Final manuscript table files are in `outputs/tables/`; rebuilt check tables are in `reproduced/tables/`.

## Data sources

The analysis uses public source data from O*NET, the World Bank, Penn World Table, Barro-Lee, Worldwide Governance Indicators, CEPII BACI, ILOSTAT, the IMF AI Preparedness Index, Eurostat, and external exposure measures cited in the paper. The file `data_raw_public_metadata/source_inventory.csv` lists source links and roles in the analysis.

## Requirements

The reproduction scripts are written in R. They use `arrow`, `dplyr`, `readr`, `tidyr`, `ggplot2`, and `scales`. The package was checked with R on macOS. No API keys are needed.

## Known limits

The package is designed to reproduce the paper results from retained labels, not to repeat the original API labelling run. Some final manuscript figures are included as exact submitted files while their full plotting scripts remain outside this public package. The status file in `reproduced/checks/` makes this distinction explicit.

## Licence and third-party data terms

The code in this package is released under the MIT License; see `LICENSE`. The data files combine original constructed measures with cleaned extracts or derived variables from public third-party sources. Those source datasets remain governed by their own terms. See `docs/DATA_USE_NOTICE.md` for source-specific notes and attribution guidance.
