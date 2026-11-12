import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import config
import sync


def document():
    models = {"base": {"disabled": False}, "old": {"disabled": True},
              "curated-small": {"modelID": "base", "disabled": False}}
    return {"providers": {provider: {"models": models.copy()}
                          for provider in ("opencode", "opencode-go")}}


class ConfigTests(unittest.TestCase):
    def test_merge_and_ownership(self):
        self.assertEqual(config.merge(document(), {"mcp": {}})["mcp"], {})
        with self.assertRaises(ValueError):
            config.merge(document(), document())
        with self.assertRaises(ValueError):
            config.merge({"mcp": {}}, {})
        with self.assertRaises(ValueError):
            config.merge({}, {"providers": {}})

    def test_strict_json(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '[]', 'null'):
            with self.assertRaises(ValueError):
                config.decode(text)

    def test_curation_validation(self):
        config.validate(document(), {})
        data = document()
        data["providers"]["opencode"]["models"]["base"] = {"disabled": True}
        config.validate(data, {})  # Aliases resolve from the catalog, so a disabled target is valid.
        data["providers"]["opencode"]["models"]["curated-small"] = {"modelID": "missing", "disabled": False}
        with self.assertRaises(ValueError):
            config.validate(data, {})
        with self.assertRaises(ValueError):
            config.validate({}, {})
        data = document()
        data["model"] = "opencode/missing"
        with self.assertRaises(ValueError):
            config.validate(data, {})

    def test_schema_validation(self):
        import jsonschema
        with self.assertRaises(jsonschema.ValidationError):
            config.validate(document(), {"type": "object", "additionalProperties": False})

    def test_https_required(self):
        with self.assertRaises(ValueError):
            config.download("http://example.com/config.json")

    @patch("sync.validate")
    @patch("sync.download")
    def test_sync_installs_and_records_timestamp(self, download, validate):
        data = json.dumps(document()).encode()
        download.return_value = data
        with tempfile.TemporaryDirectory() as root:
            dest, state = Path(root) / "config/opencode.json", Path(root) / "state"
            sync.sync("https://example.com/config", dest, state)
            self.assertEqual(dest.read_bytes(), data)
            self.assertEqual(dest.stat().st_mode & 0o777, 0o644)
            timestamp = config.decode((state / "last-success.json").read_bytes())
            self.assertIn("synced_at", timestamp)
            self.assertEqual(timestamp["sha256"], sync.hashlib.sha256(data).hexdigest())
            sync.sync("https://example.com/config", dest, state)
            self.assertEqual(validate.call_count, 1)  # Unchanged file needs no schema fetch.

    @patch("sync.validate")
    @patch("sync.download")
    def test_sync_preserves_last_good_on_failure(self, download, validate):
        with tempfile.TemporaryDirectory() as root:
            dest, state = Path(root) / "opencode.json", Path(root) / "state"
            download.return_value = b'{"old":true}'
            sync.sync("https://example.com/config", dest, state)
            timestamp = (state / "last-success.json").read_bytes()
            download.return_value = b'{"new":true}'
            validate.side_effect = ValueError("bad config")
            with self.assertRaises(ValueError):
                sync.sync("https://example.com/config", dest, state)
            self.assertEqual(dest.read_bytes(), b'{"old":true}')
            self.assertEqual((state / "last-success.json").read_bytes(), timestamp)
            validate.side_effect = None
            sync.sync("https://example.com/config", dest, state)
            self.assertEqual((state / "previous.json").read_bytes(), b'{"old":true}')
            self.assertEqual((state / "previous.json").stat().st_mode & 0o777, 0o600)

    @patch("sync.download")
    def test_system_jsonc_blocks_sync(self, download):
        with tempfile.TemporaryDirectory() as root:
            dest, state = Path(root) / "opencode.json", Path(root) / "state"
            dest.with_suffix(".jsonc").write_text("{}")
            with self.assertRaises(ValueError):
                sync.sync("https://example.com/config", dest, state)
            download.assert_not_called()

    @patch("sync.download", side_effect=OSError("offline"))
    def test_offline_does_not_create_config_or_success(self, download):
        with tempfile.TemporaryDirectory() as root:
            dest, state = Path(root) / "opencode.json", Path(root) / "state"
            with self.assertRaises(OSError):
                sync.sync("https://example.com/config", dest, state)
            self.assertFalse(dest.exists())
            self.assertFalse((state / "last-success.json").exists())


if __name__ == "__main__":
    unittest.main()
