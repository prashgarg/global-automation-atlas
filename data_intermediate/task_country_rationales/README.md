# Task-country rationales

The eight Parquet files in this folder contain the non-empty short rationales accompanying the retained task-country labels. Read the files together as one dataset and join them to `../task_country_labels_analysis.parquet` using `item_id`, or equivalently `task_id` and `iso3`.

The files contain 2,320,863 rationales, covering 99.575% of the 2,330,776 retained task-country labels. The remaining 9,913 retained labels have no non-empty rationale. `rationale_corpus_summary.csv` records the corresponding coverage and key-integrity checks.

## Columns

- `rationale_row_id`: stable row identifier used in the rationale-analysis workflow.
- `item_id`: task-country identifier matching the retained label file.
- `task_id`: stable O*NET task identifier.
- `iso3`: ISO 3166-1 alpha-3 country code.
- `short_rationale`: exact non-empty rationale retained from the language-model output.

These rationales are model-generated explanations for classification decisions. They should not be treated as independently verified factual descriptions of countries.
