import unittest
from unittest.mock import patch

import curate


def aa(name="Example 2 (High)", slug="example-2-high", score=50, cost=1):
    return {"name": name, "slug": slug,
            "evaluations": {"artificial_analysis_intelligence_index": score},
            "artificial_analysis_intelligence_index_cost": {"cost_per_task": {"total_cost": cost}}}


def model(mid="example-2", **kwargs):
    return {"id": mid, "name": mid, "type": "chat",
            "cost": {"text": {"input": {"price": 1}, "output": {"price": 2}}},
            "capabilities": {"reasoning": {"supported": True, "effort": ["high", "low"]}}, **kwargs}


class CurateTests(unittest.TestCase):
    def test_model_config_enables_only_curated_aliases(self):
        catalog = [model("gpt-example"), model("cheap-example"), model("unmatched")]
        catalogs = {"Go": catalog, "Paid": catalog}
        public = {"Go": catalog + [model("public-only")], "Paid": catalog}
        policy = {"allowed": {channel: ["gpt-example", "cheap-example", "unmatched"] for channel in catalogs}}
        client = {p: {"models": {"client-only": {}}} for p in ("opencode", "opencode-go")}
        # Both on the frontier and in the same band; only the stronger one is picked.
        aa_models = [aa("GPT Example (High)", "gpt-example-high", score=50, cost=1),
                     aa("Cheap Example (Low)", "cheap-example-low", score=42, cost=0.5)]
        config = curate.model_config(aa_models, catalogs, public, policy, client)
        models = config["providers"]["opencode-go"]["models"]
        self.assertEqual([mid for mid, entry in models.items() if not entry["disabled"]], ["curated-strong"])
        self.assertTrue(models["gpt-example"]["disabled"])
        self.assertTrue(models["cheap-example"]["disabled"])
        self.assertTrue(models["public-only"]["disabled"])
        self.assertTrue(models["unmatched"]["disabled"])
        self.assertTrue(models["client-only"]["disabled"])
        self.assertEqual(models["curated-strong"]["modelID"], "gpt-example")
        self.assertEqual(models["curated-strong"]["settings"], {"reasoningEffort": "high"})
        self.assertNotIn("model", config)

    def test_pr_body_describes_actual_changes(self):
        previous = {"providers": {"opencode-go": {"models": {
            "claude-haiku-5-5": {"disabled": True}, "gpt-old": {"disabled": True},
            "curated-small": {"modelID": "gpt-old", "name": "Small — GPT Old", "disabled": False, "settings": {}},
            "curated-flagship": {"modelID": "gpt-old", "name": "Flagship — GPT Old", "disabled": False, "settings": {}}}}}}
        config = {"providers": {"opencode-go": {"models": {
            "claude-haiku-5-5": {"disabled": True}, "gpt-old": {"disabled": True},
            "curated-small": {"modelID": "claude-haiku-5-5", "name": "Small — Claude Haiku 5.5",
                              "disabled": False, "settings": {}},
            "curated-medium": {"modelID": "claude-haiku-5-5", "name": "Medium — Claude Haiku 5.5",
                               "disabled": False, "settings": {}}}}}}
        body = curate.pr_body(previous, config)
        self.assertIn("- `curated-small` → `claude-haiku-5-5` (Small — Claude Haiku 5.5): was `gpt-old` (Small — GPT Old)", body)
        self.assertIn("- `curated-medium` → `claude-haiku-5-5` (Medium — Claude Haiku 5.5): new", body)
        self.assertIn("- Newly enabled: `curated-medium`", body)
        self.assertIn("- Newly disabled: `curated-flagship`", body)
        first_run = curate.pr_body({}, config)
        self.assertIn("- `curated-small` → `claude-haiku-5-5` (Small — Claude Haiku 5.5): new", first_run)
        self.assertIn("- Newly disabled: none", first_run)

    def test_alias_settings_and_empty_frontier_fail_closed(self):
        for mid, key in (("claude-haiku-5-5", "effort"), ("gemini-4-argon", "thinkingConfig")):
            self.assertIn(key, curate.alias_settings({"id": mid, "effort": "high"}))
        with self.assertRaises(ValueError):
            curate.alias_settings({"id": "unknown", "effort": "high"})
        with self.assertRaises(ValueError):
            curate.model_config([], {"Go": []}, {"Go": []}, {"allowed": {"Go": []}})

    def points(self, values):
        return [{"id": str(i), "slug": str(i), "aa_name": f"Model {i}", "cost": cost, "score": score}
                for i, (cost, score) in enumerate(values)]

    def test_hull_removes_unsupported_and_collinear_points(self):
        points = self.points([(1, 10), (2, 11), (4, 20), (8, 25), (16, 30)])
        self.assertEqual([p["score"] for p in curate.upper_hull(points)], [10, 30])
        self.assertEqual(curate.upper_hull(points[::-1]), curate.upper_hull(points))

    def test_hull_ties_and_empty(self):
        self.assertEqual(curate.upper_hull([]), [])
        points = self.points([(1, 10), (1, 10), (2, 20)])
        self.assertEqual(len(curate.upper_hull(points)), 2)

    def test_knee_per_band_and_endpoint_fallback(self):
        points = self.points([(1, 10), (2, 24), (4, 35), (8, 43), (16, 48), (32, 51)])
        picks = curate.shortlist(points, "Go")
        self.assertEqual([(tier, p["score"]) for tier, p in picks],
                         [("Small", 24), ("Medium", 35), ("Strong", 48)])
        self.assertEqual(curate.shortlist(points[:1], "Paid"), [("Small", points[0])])
        self.assertEqual(curate.shortlist([], "Go"), [])

    def test_near_equivalent_candidates_across_band_boundary(self):
        points = self.points([(1, 24), (2, 26), (8, 31), (32, 35)])
        picks = curate.shortlist(points, "Go")
        self.assertEqual([p["score"] for _, p in picks], [24, 31])
        self.assertLessEqual(len(picks), 3)

    def test_current_paid_examples(self):
        points = self.points([(0.0051, 9.7), (0.0422, 18.5), (0.0438, 18.6),
                              (0.0729, 21.4), (0.0918, 24.6), (0.152, 27.9),
                              (0.1586, 29.9), (0.1615, 34.8), (0.3594, 46.3),
                              (0.591, 50.3), (0.764, 52.5), (1.2721, 54.6),
                              (3.2386, 54.8), (3.6589, 55.3), (3.8026, 56.4),
                              (6.0472, 57.4), (9.0784, 61.8), (14.8286, 62.2), (26.5386, 64.6)])
        picks = curate.shortlist(points, "Paid")
        self.assertIn(points[7], [p for _, p in picks])
        self.assertNotIn(points[12], [p for _, p in picks])
        self.assertEqual(len(picks), 4)
        self.assertIn("| Medium | 8 |", "\n".join(curate.selection_table(points, "Paid")))

    def test_privacy_unknown_and_contributor_excluded(self):
        policy = {"allowed": {"Go": ["example-2"]}}
        allowed, excluded = curate.filter_privacy(
            [model(), model("example-2-contributor"), model("new-model")], "Go", policy)
        self.assertEqual([m["id"] for m in allowed], ["example-2"])
        self.assertEqual(excluded, ["example-2-contributor", "new-model"])

    def test_actual_policy_channel_specific(self):
        import json
        policy = json.loads((curate.HERE / "privacy.json").read_text())
        self.assertFalse(curate.filter_privacy([model("deepseek-v4-pro")], "Go", policy)[0])
        self.assertTrue(curate.filter_privacy([model("deepseek-v4-pro")], "Paid", policy)[0])
        for channel in ("Go", "Paid"):
            self.assertFalse(curate.filter_privacy([model("longcat-2.5-free")], channel, policy)[0])
            self.assertFalse(curate.filter_privacy([model("iceman-contributor-free")], channel, policy)[0])

    def test_privacy_before_frontier_and_offers(self):
        policy = {"allowed": {"Go": []}, "verified_on": "2026-11-10", "sources": {}}
        report = curate.render(5, [aa()], {"Go": [model()]}, "2026-11-10", policy)
        self.assertIn("0 frontier points", report)
        self.assertNotIn("https://artificialanalysis.ai/models/example-2-high", report)
        self.assertIn("## Privacy filter", report)

    def test_frontier_and_ties(self):
        points = [{"id": str(i), "slug": str(i), "cost": cost, "score": score}
                  for i, (cost, score) in enumerate([(1, 10), (2, 9), (2, 20), (1, 10), (3, 20)])]
        self.assertEqual([p["id"] for p in curate.frontier(points)], ["0", "3", "2"])

    def test_versions_not_erased(self):
        entries, missing, _ = curate.intersect([model()], [aa("Example 2.1 (High)")])
        self.assertFalse(entries)
        self.assertEqual(len(missing), 1)

    def test_efforts_kept_and_supported(self):
        entries, missing, _ = curate.intersect([model()], [aa(), aa("Example 2 (Low)", "example-2-low"),
                                                        aa("Example 2 (Max)", "example-2")])
        self.assertEqual([e["effort"] for e in entries], ["high", "low"])
        self.assertFalse(missing)

    def test_missing_invalid_and_zero_cost(self):
        for value in [None, 0, -1, float("nan"), float("inf"), True]:
            self.assertFalse(curate.intersect([model()], [aa(cost=value)])[0])

    def test_free_is_separate(self):
        m = model()
        m["cost"]["text"] = {"input": {"price": 0}, "output": {"price": 0}}
        entries, _, offers = curate.intersect([m], [aa()])
        self.assertFalse(entries)
        self.assertTrue(offers[0]["free"])

    def test_nested_pricing_rules(self):
        m = model()
        m["cost"]["multipliers"] = [{"when": {"date": {"gte": "2026-12-01"}}, "factor": 2}]
        entries, _, offers = curate.intersect([m], [aa()])
        self.assertEqual(entries[0]["cost"], 1)
        self.assertEqual(offers[0]["factor"], 2)
        m["cost"]["multipliers"][0]["when"] = {"utc_hours": {"gte": "01:00"}}
        self.assertEqual(curate.price_rules(m)[1], 1)

    def test_free_counterpart(self):
        paid = model()
        free = model("example-2-free")
        free["cost"]["text"] = {"input": {"price": 0}, "output": {"price": 0}}
        _, _, offers = curate.intersect([free, paid], [aa()])
        self.assertIn("`example-2`", offers[0]["counterpart"])

    @patch("curate.fetch")
    def test_pagination(self, fetch):
        fetch.side_effect = [
            {"intelligence_index_version": 5, "data": [aa()], "pagination": {"page": 1, "has_more": True}},
            {"intelligence_index_version": 5, "data": [aa()], "pagination": {"page": 2, "has_more": False}},
        ]
        self.assertEqual(len(curate.fetch_aa("unused")[1]), 2)
        self.assertIn("page=2", fetch.call_args.args[0])

    @patch("curate.fetch")
    def test_version_changes_fail(self, fetch):
        fetch.side_effect = [
            {"intelligence_index_version": 5, "data": [aa()], "pagination": {"page": 1, "has_more": True}},
            {"intelligence_index_version": 6, "data": [aa()], "pagination": {"page": 2, "has_more": False}},
        ]
        with self.assertRaises(ValueError):
            curate.fetch_aa("unused")

    @patch("curate.fetch")
    def test_catalogs_use_workspace_key(self, fetch):
        fetch.side_effect = [{"data": [model()]}, {"data": [model("example-3")]}]
        self.assertEqual(set(curate.fetch_catalogs("oc_test")), {"Go", "Paid"})
        for call in fetch.call_args_list:
            self.assertEqual(call.args[1], {"Authorization": "Bearer oc_test"})

    @patch("curate.fetch")
    def test_empty_catalog_fails(self, fetch):
        fetch.return_value = {"data": []}
        with self.assertRaises(ValueError):
            curate.fetch_catalogs("oc_test")

    def test_report(self):
        report = curate.render(5, [aa()], {"Go": [model()], "Paid": [model()]}, "2026-11-10")
        self.assertIn("## Go frontier", report)
        self.assertIn("## Paid frontier", report)
        self.assertIn("### Curated picks", report)
        self.assertIn("| Strong | 1 | Example 2 (High) |", report)
        self.assertIn("Artificial Analysis", report)
        self.assertIn("Index v5.0", report)
        self.assertIn("Index v5.1", curate.render(5.1, [aa()], {"Go": [model()]}, "2026-11-10"))
        self.assertNotIn("All comparable configurations", report)
        self.assertEqual(report, curate.render(5, [aa()], {"Go": [model()], "Paid": [model()]}, "2026-11-10"))


if __name__ == "__main__":
    unittest.main()
