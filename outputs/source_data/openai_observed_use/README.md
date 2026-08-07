# OpenAI observed-use validation inputs

This folder contains the OpenAI Signals v2.0 inputs used for the paper's U.S. work-activity and global country comparisons.

- `usa_share_of_messages_by_onet_iwa_month.csv`: monthly shares of all U.S. consumer ChatGPT messages by O*NET intermediate work activity.
- `usa_share_of_work_related_messages_by_onet_iwa_month.csv`: monthly shares of U.S. work-related consumer ChatGPT messages by O*NET intermediate work activity.
- `share_of_messages_by_country_quarter_rank.csv`: population-normalised country ranks of consumer ChatGPT use by quarter.
- `share_of_messages_by_work_related_country_month.csv`: monthly work-related and non-work-related message shares by country.
- `onet_task_hierarchy.csv`: the O*NET task-to-DWA-to-IWA hierarchy used to aggregate retained U.S. Atlas task labels.
- `openai_signals_v2_data_dictionary.pdf`: the official release documentation, including sampling, privacy protections, file definitions and classifier prompts.

The release covers July 2024 through June 2026. OpenAI Signals data are available from https://openai.com/signals/data-download/ under the Creative Commons Attribution 4.0 International licence. Users should cite Aaron Chatterji, Thomas Cunningham, David J. Deming, Zoe Hitzig, Drew Johnston, Alex Martin Richmond, Christopher Ong, Carl Yan Shan and Kevin Wadman, "OpenAI Signals v2.0," 2026, https://cdn.openai.com/signals/data-dictionary.pdf. The U.S. work-activity interpretation also follows Chatterji et al., "How People Use ChatGPT," NBER Working Paper 34255 (2025), https://doi.org/10.3386/w34255.

The country files describe aggregate consumer ChatGPT use. OpenAI does not release country-by-O*NET work-activity cells, so the global country exercise and the U.S. work-activity exercise remain separate.

O*NET content is available from https://www.onetcenter.org/database.html under Creative Commons Attribution 4.0 International, except where otherwise noted by O*NET.
