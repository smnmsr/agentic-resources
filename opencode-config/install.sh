#!/bin/sh
# One-time, privileged installation. No machine is enrolled by CI.
set -eu
umask 022
if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo sh opencode-config/install.sh" >&2
  exit 1
fi
SOURCE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BASE=/usr/local/lib/opencode-config-sync
command -v python3 >/dev/null || { echo "Python 3 is required" >&2; exit 1; }
case $(uname -s) in
  Linux) DEST=/etc/opencode; STATE=/var/lib/opencode-config-sync ;;
  Darwin) DEST='/Library/Application Support/opencode'; STATE='/Library/Application Support/opencode-config-sync' ;;
  *) echo "Only macOS and Linux are supported" >&2; exit 1 ;;
esac
mkdir -p "$BASE" "$DEST" "$STATE"
chmod 755 "$BASE" "$DEST"
chmod 700 "$STATE"
# opencode.jsonc loads after opencode.json and would override managed values.
if [ -e "$DEST/opencode.jsonc" ]; then
  echo "Existing $DEST/opencode.jsonc must be reviewed before enrollment" >&2
  exit 1
fi
if [ -e "$DEST/opencode.json" ] && [ ! -e "$STATE/before-enrollment.json" ]; then
  cp -p "$DEST/opencode.json" "$STATE/before-enrollment.json"
fi
cp "$SOURCE/config.py" "$SOURCE/sync.py" "$BASE/"
chmod 644 "$BASE/config.py" "$BASE/sync.py"
python3 -m venv "$BASE/venv"
"$BASE/venv/bin/python" -m pip install --disable-pip-version-check -r "$SOURCE/requirements.txt"
cat > "$BASE/run" <<EOF
#!/bin/sh
exec "$BASE/venv/bin/python" "$BASE/sync.py" --destination "$DEST/opencode.json" --state "$STATE" >/dev/null 2>&1
EOF
chmod 755 "$BASE/run"
if [ "$(uname -s)" = Linux ]; then
  command -v systemctl >/dev/null || { echo "systemd is required on Linux" >&2; exit 1; }
  cat > /etc/systemd/system/opencode-config-sync.service <<EOF
[Unit]
Description=Sync managed OpenCode configuration
[Service]
Type=oneshot
ExecStart=$BASE/run
StandardOutput=null
StandardError=null
UMask=0022
EOF
  cat > /etc/systemd/system/opencode-config-sync.timer <<'EOF'
[Unit]
Description=Hourly OpenCode configuration sync
[Timer]
OnCalendar=hourly
Persistent=true
RandomizedDelaySec=120
[Install]
WantedBy=timers.target
EOF
  systemctl daemon-reload
  systemctl enable --now opencode-config-sync.timer
else
  cat > /Library/LaunchDaemons/ai.opencode.config-sync.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>ai.opencode.config-sync</string>
<key>ProgramArguments</key><array><string>$BASE/run</string></array>
<key>RunAtLoad</key><true/>
<key>StartInterval</key><integer>3600</integer>
<key>StandardOutPath</key><string>/dev/null</string>
<key>StandardErrorPath</key><string>/dev/null</string>
</dict></plist>
EOF
  chmod 644 /Library/LaunchDaemons/ai.opencode.config-sync.plist
  launchctl bootout system/ai.opencode.config-sync 2>/dev/null || true
  launchctl bootstrap system /Library/LaunchDaemons/ai.opencode.config-sync.plist
fi
"$BASE/run" || true
echo "Enrolled. Successful syncs are recorded in $STATE/last-success.json"
