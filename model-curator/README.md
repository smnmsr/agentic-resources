# Model Pareto report

Compares OpenCode Go and paid models using the latest [Artificial Analysis](https://artificialanalysis.ai/)
Intelligence Index and cost per benchmark task. Generates Pareto plots and tables
in [MODELS.md](MODELS.md), excluding endpoints that train on request data or lack
verified US/EU hosting. AA task costs are a comparison proxy, not actual Go usage.

## Run the workflow

In GitHub, open **Actions → Model Pareto report → Run workflow**.
It also runs every Monday at 05:30 UTC.

Requires the repository secret `AA_API_KEY`. Changed reports open a PR;
unchanged reports create none. Results are also shown in the run summary.
