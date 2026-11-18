# Shared OpenCode V2 configuration

- `models.json`: **generated** by `model-curator/curate.py`; do not edit manually.
  Disables every catalog model and enables only `go-small`, `go-medium`,
  `go-strong` and `paid-small`, `paid-medium`, `paid-strong`, `paid-flagship`
  where available. Picker labels are Go Small, Paid Strong, etc.; the underlying
  model and effort remain documented in `../model-curator/MODELS.md`. Alias
  defaults use the selected effort; manually selecting a variant can override it.
  No main-session default model is chosen automatically.
- `settings.json`: hand-maintained settings (Ponytail and subagent depth).
- `agents/*.json`: native V2 agent fragments, merged in filename order. Duplicate
  agent IDs across fragments or settings fail the build.
- `prompts/*.md`: shared role prompts, referenced with an entire
  `"system": "{file:prompts/reviewer.md}"` value. The builder inlines these before
  publishing; machines need no extra files. Missing, empty, escaping or unresolved
  prompt references fail the build. Third-party prompt sources and notices are
  recorded in `prompts/THIRD_PARTY.md` and carried in the published reviewer prompt.
- `opencode.json`: **generated merge**; do not edit manually. Published on `main`
  after either fragment changes. Models owns `providers`/`model`; settings owns
  everything else. Conflicting top-level fields fail, even if values match.

The nightly/manual curator commits the report, plots, `models.json` and merged
`opencode.json` directly to `main` after its data checks, both test suites and config
validation pass (see [publication gates](../model-curator/README.md#run-the-workflow)).
Validation checks JSON, OpenCode's published schema, every alias target and every
configured agent model reference. Required tiers missing from the curated inventory
block publication rather than silently substituting another provider.
Failed runs publish nothing; date-only report updates create no commit, while other
report, frontier or inventory changes do. The separate config publisher remains for
hand-maintained source changes. Source-path filters prevent loops.
All `providers` configuration currently belongs to the models fragment; MCP,
permissions and other settings belong to settings. No keys belong in either file.
Use `{env:...}` for secrets; each machine supplies its own credentials.

Pushes using `GITHUB_TOKEN` cannot trigger other workflows, so the curator builds
and validates the merged config itself rather than relying on the config publisher.

Enablement combines authenticated/public inference catalogs and the published
models.dev client inventory. It is a snapshot, not a server-side access restriction.
New catalog IDs require a subsequent refresh to gain explicit disable entries.
V2.2.7 treats model-map keys literally: `"*": {"disabled": true}` does not disable
other models. Wildcard provider policies do not provide per-model filtering.
Other providers are untouched. Aliases inherit catalog metadata in V2;
effort mapping is reviewed against V2.2.7 `core/src/variant.ts` and fails for
unreviewed families rather than guessing.

## Agents and routing

| Default (Go) | Explicit Paid alternative | Tier | Role |
|---|---|---|---|
| `explore` | `explore-paid` | Small | Read-only code/doc discovery (15 steps) |
| `general` | `general-paid` | Medium | Bounded implementation/research (25 steps) |
| `reviewer` | `reviewer-paid` | Strong | Independent evidence-based review (25 steps) |

`title` and `summary` use Go Small; compaction and the main session model are unchanged.
Go is the default for delegation, not a new primary model or agent. Paid agents have
explicit metered-cost warnings; Strong review is for meaningful changes, not routine
lookups or automatic repeated reviews. Descriptions guide model routing but are not
hard spending limits. Step limits reset on new input and are not monetary budgets.

The caller's normal subagent task supplies change/base references, requirements,
extra focus and constraints. No special prompt API is needed. Example:

> Use reviewer to review the staged changes. Focus on config ownership and data-loss
> paths. Requirements: preserve the last successful config on any validation error.

`experimental.subagent_depth: 2` permits reviewer → explorer. Only reviewers may
launch exploration children; explorers and general workers cannot launch children.
Both reviewers prefer Go exploration, even for Paid reviews. Explorers/reviewers
use explicit read-only permission allowlists, retain sensitive `.env` read prompts,
and ask before crossing the project boundary. They cannot use MCP/plugin tools
that fall outside the allowlist. General workers retain broad implementation access.

Reviewers allow only three exact shell commands: unstaged diff, cached diff, and
last-commit diff, all with external diff/textconv disabled (see `prompts/reviewer.md`).
For another comparison supply the diff in the task. Reviewers do not execute tests
or builds; they distinguish caller-supplied results from their own inspection.
Read-only tool permissions are not an operating-system sandbox.

GitHub writes ask first. `settings.json` asks before any `gh` command and before `git push`,
except the read-only `gh` views it allowlists; unlisted `gh` subcommands ask too. Agent rules
are appended after these, so explorers and reviewers keep their stricter limits. Rules match each
command's raw text, so wrapped or quoted forms such as `GH_TOKEN=x gh ...`, `env gh`, `/usr/bin/gh`,
`"gh"`, or `bash -c "git push"` are not caught. Direct REST calls (for example `curl`) are not covered.

### Regeneration and rollout

After changing alias IDs, regenerate **both outputs together** before publishing:

```sh
AA_API_KEY=... OPENCODE_API_KEY=... python model-curator/curate.py
python opencode-config/config.py
```

Keys come from the environment; do not put them in files. Without keys, source
changes and fixture tests can be checked, but the old generated inventory will not
resolve the new agent references. The normal build intentionally fails until a
curator refresh supplies the new IDs. The nightly/manual curator has the secrets
and generates models before assembling config. Do not hand-edit generated output.

Changing only agent JSON or prompt Markdown triggers the config publisher. Machines
still fetch only `opencode.json`; no installer or sync-protocol change is required.
Existing enrolled validators continue to accept the generated config but do not gain
new validation code until an explicitly requested installer rerun. The publisher
always runs the current validator. No installer rerun is performed by this change.

## Enroll a macOS or Linux machine

Requires Python 3.10+ with `venv`, and systemd on Linux. From a trusted checkout:

```sh
sudo sh opencode-config/install.sh
```

This installs a root-owned hourly systemd timer (Linux) or LaunchDaemon (macOS).
It downloads **only the merged config**, not scripts, validates before installing,
and atomically replaces the system `opencode.json`. Existing system config is
backed up on first enrollment; an existing system `opencode.jsonc` blocks enrollment
because it would override the synced file. Failures are silent and preserve the
last good config. A successful hourly fetch updates `last-success.json`:

| | Managed config | Sync state (timestamp, hash, previous config) |
|---|---|---|
| Linux | `/etc/opencode/opencode.json` | `/var/lib/opencode-config-sync/` |
| macOS | `/Library/Application Support/opencode/opencode.json` | `/Library/Application Support/opencode-config-sync/` |

System settings outrank user/project values; macOS MDM can still override them.
OpenCode normally reloads config automatically; `/reload` forces a reload without
restarting. Existing session model selections persist. Local additions to fields
not controlled here can still apply: this is configuration management, not a sandbox.

To stop syncing: Linux `sudo systemctl disable --now opencode-config-sync.timer`;
macOS `sudo launchctl bootout system/ai.opencode.config-sync`. Restore the saved
`before-enrollment.json` manually if rolling back. Script updates require rerunning
the installer from a reviewed checkout; the hourly job never downloads executable code.

## Validate locally

```sh
python3 -m venv /tmp/opencode-config-venv
/tmp/opencode-config-venv/bin/pip install -r opencode-config/requirements.txt
/tmp/opencode-config-venv/bin/python opencode-config/config.py
```

Validation fetches `https://opencode.ai/config.json`; unavailable schema means no
publication or installation of changed config. The published schema supports legacy
fields too, so schema validation is not a full runtime/inference test. No paid
inference requests are used for validation.
