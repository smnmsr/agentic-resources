# Model Pareto report

Compares OpenCode Go and paid models using the latest [Artificial Analysis](https://artificialanalysis.ai/)
Intelligence Index and cost per benchmark task. Generates Pareto plots and tables
in [MODELS.md](MODELS.md), excluding endpoints that train on request data or lack
verified US/EU hosting. AA task costs are a comparison proxy, not actual Go usage.

## Run the workflow

In GitHub, open **Actions → Model Pareto report → Run workflow**.
It also runs every night at 00:42 UTC.

Requires the repository secrets `AA_API_KEY` and `OPENCODE_API_KEY` (a read-only
OpenCode key; only models its workspace can call are compared). The workflow commits
`MODELS.md`, plots, the [model config fragment](../opencode-config/README.md) and merged
`opencode.json` directly to `main`. Date-only report updates create no commit; other
report, frontier or inventory changes do. Results also appear in the run summary.

Publication requires at least 50 finite AA scores, unique AA IDs and valid pagination,
nonempty catalogs and frontiers, existing privacy/effort checks, both test suites and
merged-config schema validation. Failed runs publish nothing. Pushes using
`GITHUB_TOKEN` cannot trigger other workflows, so the curator builds the merged config
itself; the separate config publisher remains for hand-maintained source changes.

## Selection

The shortlist uses fixed score bands: Go <25 / 25–40 / ≥40; Paid adds a
55-point flagship boundary. Within each band, it keeps the upper hull of
score versus log₂(cost), then chooses the largest drop in score gain per price
doubling (or the highest-scoring endpoint if no corner remains). Hull candidates
less than 3 score points apart retain the cheaper option, including across bands.
Empty bands stay empty. In `models.json` only the `curated-*` aliases are enabled;
every catalog model, including the picked ones, is disabled. These editorial defaults
are `SELECTION` and `MIN_SCORE_GAP` in `curate.py`, not benchmark confidence intervals.
