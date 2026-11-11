#!/usr/bin/env python3
"""Silently fetch, validate, and atomically install a centrally managed config."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile

from config import decode, download, validate

URL = "https://raw.githubusercontent.com/smnmsr/agentic-resources/refs/heads/main/opencode-config/opencode.json"


def atomic_write(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".opencode-sync-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def sync(url, destination, state):
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / "lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        if destination.with_suffix(".jsonc").exists():
            raise ValueError("System opencode.jsonc would override synced settings")
        data = download(url)
        document = decode(data)
        previous = destination.read_bytes() if destination.exists() else None
        digest = hashlib.sha256(data).hexdigest()
        marker = state / "last-success.json"
        recorded = decode(marker.read_bytes()).get("sha256") if marker.exists() else None
        if data != previous or recorded != digest:
            validate(document)
        if data != previous:
            if previous is not None:
                atomic_write(state / "previous.json", previous)
            atomic_write(destination, data, mode=0o644)
        atomic_write(state / "last-success.json", (json.dumps({
            "synced_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "sha256": digest, "url": url,
        }, indent=2) + "\n").encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=URL)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    try:
        sync(args.url, args.destination, args.state)
    except Exception:
        # No notifications or error output; last-success only advances on success.
        raise SystemExit(1)


if __name__ == "__main__":
    main()
