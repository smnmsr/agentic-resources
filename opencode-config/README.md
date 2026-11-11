# Shared OpenCode V2 configuration

- `models.json`: **generated** by `model-curator/curate.py`; do not edit manually.
  Enables Go/Paid frontier models and adds `curated-small`, `curated-medium`,
  `curated-strong` and (Paid) `curated-flagship` aliases where available. Alias
  defaults use the selected effort; manually selecting a variant can override it.
  No default model is chosen automatically.
- `settings.json`: hand-maintained non-model settings; initially empty.
- `opencode.json`: **generated merge**; do not edit manually. Published on `main`
  after either fragment changes. Models owns `providers`/`model`; settings owns
  everything else. Conflicting top-level fields fail, even if values match.

The weekly/manual report opens a PR including `models.json`. After merge, the
publish workflow validates JSON, OpenCode's published schema, alias targets and
enablement, then commits `opencode.json`. Source-path filters prevent loops.
All `providers` configuration currently belongs to the models fragment; MCP,
permissions and other settings belong to settings. No keys belong in either file.
Use `{env:...}` for secrets; each machine supplies its own credentials.

Report PRs created with the default `GITHUB_TOKEN` do not trigger PR workflows.
Validation still runs on publication after merge; do not assume a bot-created PR
has passed pre-merge config checks.

Enablement combines authenticated/public inference catalogs and the published
models.dev client inventory. It is a snapshot, not a server-side access restriction.
New catalog IDs require a subsequent refresh to gain explicit disable entries.
V2.2.7 treats model-map keys literally: `"*": {"disabled": true}` does not disable
other models. Wildcard provider policies do not provide per-model filtering.
Other providers are untouched. Aliases inherit catalog metadata in V2;
effort mapping is reviewed against V2.2.7 `core/src/variant.ts` and fails for
unreviewed families rather than guessing.

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
