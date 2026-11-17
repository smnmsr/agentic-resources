import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import config
import sync


def document():
    models = {"base": {"disabled": False}, "old": {"disabled": True},
              "small": {"modelID": "base", "disabled": False}}
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
        data["providers"]["opencode"]["models"]["small"] = {"modelID": "missing", "disabled": False}
        with self.assertRaises(ValueError):
            config.validate(data, {})
        with self.assertRaises(ValueError):
            config.validate({}, {})
        data = document()
        data["model"] = "opencode/missing"
        with self.assertRaises(ValueError):
            config.validate(data, {})

    def test_agent_fragments_and_prompt_inlining(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            (directory / "agents").mkdir()
            (directory / "prompts").mkdir()
            prompt = directory / "prompts/review.md"
            prompt.write_text("Review callers.\n")
            fragment = directory / "agents/reviewer.json"
            fragment.write_text(json.dumps({"agents": {"reviewer": {
                "system": "{file:prompts/review.md}", "model": "opencode/small"}}}))
            settings = {"plugins": ["example"]}
            assembled = config.agent_settings(directory, settings)
            self.assertEqual(assembled["agents"]["reviewer"]["system"], "Review callers.")
            self.assertEqual(settings, {"plugins": ["example"]})
            with self.assertRaisesRegex(ValueError, "Duplicate agents"):
                config.agent_settings(directory, {"agents": {"reviewer": {}}})
            (directory / "agents/duplicate.json").write_text(fragment.read_text())
            with self.assertRaisesRegex(ValueError, "Duplicate agents"):
                config.agent_settings(directory, {})
            (directory / "agents/duplicate.json").unlink()
            prompt.write_text("  \n")
            with self.assertRaisesRegex(ValueError, "Empty prompt"):
                config.agent_settings(directory, {})
            prompt.unlink()
            with self.assertRaises(FileNotFoundError):
                config.agent_settings(directory, {})
            fragment.write_text('{"agents":{"reviewer":{"system":"{file:../secret}"}}}')
            with self.assertRaisesRegex(ValueError, "outside prompts"):
                config.agent_settings(directory, {})
            (directory / "secret").write_text("outside prompt root")
            prompt.symlink_to(directory / "secret")
            fragment.write_text('{"agents":{"reviewer":{"system":"{file:prompts/review.md}"}}}')
            with self.assertRaisesRegex(ValueError, "outside prompts"):
                config.agent_settings(directory, {})
            fragment.write_text('{"agents":{"reviewer":{"system":"prefix {file:prompts/review.md}"}}}')
            with self.assertRaisesRegex(ValueError, "Unresolved prompt"):
                config.agent_settings(directory, {})
            fragment.write_text('{"plugins":[]}')
            with self.assertRaisesRegex(ValueError, "Expected an agents"):
                config.agent_settings(directory, {})

    def test_agent_model_validation(self):
        for reference in ("opencode/missing", "opencode/old", "broken", "opencode/small#high"):
            data = document()
            data["agents"] = {"reviewer": {"model": reference}}
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                config.validate(data, {})
        data["agents"]["reviewer"]["model"] = "opencode/small"
        config.validate(data, {})

    def test_shipped_agents_routing_and_permissions(self):
        directory = Path(__file__).resolve().parent
        settings = config.agent_settings(directory, config.decode((directory / "settings.json").read_bytes()))
        agents = settings["agents"]
        self.assertEqual(settings["experimental"]["subagent_depth"], 2)
        self.assertEqual(set(agents), {"explore", "explore-paid", "general", "general-paid",
                                       "reviewer", "reviewer-paid", "title", "summary"})
        from fnmatch import fnmatchcase

        def effect(agent, action, resource):
            return next((rule["effect"] for rule in reversed(agent["permissions"])
                         if fnmatchcase(action, rule["action"]) and fnmatchcase(resource, rule["resource"])), None)

        for role, tier in (("explore", "small"), ("general", "medium"), ("reviewer", "strong")):
            go, paid = agents[role], agents[role + "-paid"]
            self.assertEqual(go["model"], f"opencode-go/go-{tier}")
            self.assertEqual(paid["model"], f"opencode/paid-{tier}")
            self.assertEqual(go["system"], paid["system"])
            self.assertNotIn("{file:", go["system"])
            self.assertIn("METERED", paid["description"])
            for agent in (go, paid):
                self.assertEqual(effect(agent, "subagent", "reviewer"), "deny")
                if role != "general":
                    self.assertEqual(effect(agent, "edit", "file.py"), "deny")
                    self.assertEqual(effect(agent, "shell", "git diff --output=file.py"), "deny")
                    self.assertEqual(effect(agent, "read", ".env"), "ask")
                self.assertEqual(effect(agent, "subagent", "explore"),
                                 "allow" if role == "reviewer" else "deny")
        self.assertIn("MIT License", agents["reviewer"]["system"])
        self.assertEqual(agents["title"]["model"], "opencode-go/go-small")
        self.assertEqual(agents["summary"]["model"], "opencode-go/go-small")

    def test_build_inlines_prompts_and_validates_references(self):
        source = Path(__file__).resolve().parent
        settings = config.agent_settings(source, config.decode((source / "settings.json").read_bytes()))
        models = {"providers": {provider: {"models": {
            "base": {"disabled": True},
            **{f"{channel}-{tier}": {"disabled": False, "modelID": "base"}
               for tier in ("small", "medium", "strong")}}}
            for provider, channel in (("opencode-go", "go"), ("opencode", "paid"))}}
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            (directory / "models.json").write_text(json.dumps(models))
            (directory / "settings.json").write_text(json.dumps(settings))
            with patch("config.download", return_value=b'{}'):
                output = config.build(directory)
            built = config.decode(output.read_bytes())
            self.assertEqual(built["agents"], settings["agents"])
            self.assertNotIn("{file:", output.read_text())
            previous = output.read_bytes()
            del models["providers"]["opencode-go"]["models"]["go-small"]
            (directory / "models.json").write_text(json.dumps(models))
            with patch("config.download", return_value=b'{}'):
                with self.assertRaisesRegex(ValueError, "Agent model is not enabled"):
                    config.build(directory)
            self.assertEqual(output.read_bytes(), previous)

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
