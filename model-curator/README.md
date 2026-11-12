# Model Pareto report

Compares OpenCode Go and paid models using the latest [Artificial Analysis](https://artificialanalysis.ai/)
Intelligence Index and cost per benchmark task. Generates Pareto plots and tables
in [MODELS.md](MODELS.md), excluding endpoints that train on request data or lack
verified US/EU hosting. AA task costs are a comparison proxy, not actual Go usage.

## Run the workflow

In GitHub, open **Actions → Model Pareto report → Run workflow**.
It also runs every night at 00:42 UTC.

Requires the repository secrets `AA_API_KEY` and `OPENCODE_API_KEY` (a read-only
OpenCode key; only models its workspace can call are compared). Changed reports
open a PR; unchanged reports create none. Results are also shown in the run summary.

The same PR updates the [model config fragment](../opencode-config/README.md).
After merge, a separate workflow publishes the merged config for enrolled machines.

## Selection

The shortlist uses fixed score bands: Go <25 / 25–40 / ≥40; Paid adds a
55-point flagship boundary. Within each band, it keeps the upper hull of
score versus log₂(cost), then chooses the largest drop in score gain per price
doubling (or the highest-scoring endpoint if no corner remains). Hull candidates
less than 3 score points apart retain the cheaper option, including across bands.
Empty bands stay empty. In `models.json` only the `curated-*` aliases are enabled;
every catalog model, including the picked ones, is disabled. These editorial defaults
are `SELECTION` and `MIN_SCORE_GAP` in `curate.py`, not benchmark confidence intervals.
