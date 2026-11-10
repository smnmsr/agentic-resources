# Model Pareto report

Keep it simple: current Artificial Analysis Intelligence Index score versus
AA cost per benchmark task, intersected separately with OpenCode Go and paid
catalogs. Publish two Pareto frontier tables in `MODELS.md`. No score blending,
token-price ranking, model selection or config application.

## Run

Python 3.12+, standard library only:

```sh
export AA_API_KEY=... # keep the key out of source control
python model-curator/curate.py
python -m unittest discover -s model-curator -p 'test_*.py'
```

Set repository Actions secret `AA_API_KEY`. After merging the workflow into the
default branch, run **Model Pareto report** manually in Actions; it also runs
Mondays at 05:30 UTC. The workflow opens/updates one PR containing `MODELS.md`.
GitHub must allow Actions to create pull requests. Fetch failures fail the job
without replacing the report with stale or partial data.

AA's `/api/v2/language/models/free` endpoint is paginated. Null scores or missing/
nonpositive task costs are not rankable. All pages must report the same index
version. The API version is major.minor; patch changes are not represented.

Matching removes punctuation, not version/date suffixes. Model names, canonical
IDs and exact AA slugs provide identity matches. Explicit AA effort levels must
appear in the OpenCode capabilities. Unmatched endpoints are listed rather than
fuzzy-matched. The first version deliberately prioritizes precision over coverage.

Free endpoints appear separately, never as zero-cost frontier points. Nonzero
discounted endpoints still use AA reference task cost on the main frontier;
OpenCode pricing rules are shown separately. `cost.multipliers` can expose regular
post-promotion prices (e.g. a date-only rule) or peak/context pricing. The script
only infers post-promo rates from one unambiguous date-only multiplier, displaying
the original rule. It does not invent regular prices for free endpoints, reverse
engineer arbitrary conditions, or reprice AA tasks. Go allowances are not supplied
by these model catalogs and are not estimated here.

The Go frontier is a **Go-available cost/capability comparison**, not a measured
allowance frontier. AA costs use AA's pricing/cache assumptions, not necessarily
your actual bill. Privacy/region approval and task-specific suitability remain
separate decisions. Availability is not a policy endorsement.

Data attribution: [Artificial Analysis](https://artificialanalysis.ai/).
Use is subject to their API terms; this project publishes a derived comparison,
not raw API snapshots.
