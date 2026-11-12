# AGENTS.md

Small repo of automation for OpenCode model curation. No package manager; Python 3.12 in CI. Config scripts need `jsonschema` (see `opencode-config/requirements.txt`).

## Commands

- Report tests (stdlib only): `python -m unittest discover -s model-curator -p 'test_*.py'`
- Config tests need deps: `python -m pip install -r opencode-config/requirements.txt`, then `python -m unittest discover -s opencode-config -p 'test_*.py'`
- Regenerate report + model fragment: `AA_API_KEY=... OPENCODE_API_KEY=... python model-curator/curate.py` (network; both keys required)
- Merge + validate config: `python opencode-config/config.py` (needs jsonschema; fetches `https://opencode.ai/config.json`)
- Run both test suites before committing, since CI runs both.

## Generated files: do not edit by hand

- `model-curator/MODELS.md`, `model-curator/plots/*.svg`: from `curate.py`.
- `opencode-config/models.json`: from `curate.py`.
- `opencode-config/opencode.json`: from `config.py`; published to `main` by the curator or config publish workflow.
- Changing a fragment means changing the generator or source input, then regenerating.

## Config ownership

- `models.json` owns `providers` and the default `model`; `settings.json` owns everything else. Conflicting top-level fields fail the merge.
- Model enablement is an explicit per-model `disabled` list. In V2.2.7 `"*": {"disabled": true}` does not work for models.
- Aliases (`curated-*`) have fixed effort mappings in `alias_settings()`, tied to `packages/core/src/variant.ts` at `anomalyco/opencode` commit `fedc6f2` (v2.2.7). Unknown model families fail closed; add a mapping only after checking that source.
- Only V2 config fields are valid. Don't use V1 docs or fields.

## Publishing and triggers

- Nightly/manual curator commits `MODELS.md`, plots, `models.json` and merged `opencode.json` directly to `main`. Date-only report updates create no commit; other report, frontier or inventory changes do.
- Publication requires >=50 finite AA scores, unique AA IDs and valid pagination, nonempty catalogs/frontiers, existing privacy/effort checks, both test suites and merged-config schema validation. Failed runs publish nothing.
- `GITHUB_TOKEN` pushes cannot trigger other workflows, so the curator builds and validates merged config itself.
- The config publisher remains for hand-maintained source changes; its path filters exclude generated output to prevent loops. Pull requests validate only; publishing happens on push to `main`.

## Machine sync (macOS/Linux)

- `opencode-config/install.sh` is a one-time root installer. Do not run it from CI or an agent session without an explicit user request.
- Machines fetch only the published `opencode-config/opencode.json` over HTTPS, validate it, and atomically replace `/etc/opencode/opencode.json` (Linux) or `/Library/Application Support/opencode/opencode.json` (macOS).
- A system `opencode.jsonc` blocks enrollment because it would override synced settings.
- Failures are silent. Last successful sync info lives in `/var/lib/opencode-config-sync/` or `/Library/Application Support/opencode-config-sync/`.

## Secrets

- `AA_API_KEY` and `OPENCODE_API_KEY` come only from the environment or GitHub Actions secrets. Never write keys to files or commit them.
- `OPENCODE_API_KEY` is a read-only OpenCode key; it lists workspace-visible models.

## Other

- `skills/swiss-ricardo-listings/SKILL.md` is an unrelated listing-writing skill for Ricardo.ch.
