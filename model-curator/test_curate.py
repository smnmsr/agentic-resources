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

    def test_report(self):
        report = curate.render(5, [aa()], {"Go": [model()], "Paid": [model()]}, "2026-11-10")
        self.assertIn("## Go frontier", report)
        self.assertIn("## Paid frontier", report)
        self.assertIn("Artificial Analysis", report)
        self.assertIn("Index v5.0", report)
        self.assertIn("Index v5.1", curate.render(5.1, [aa()], {"Go": [model()]}, "2026-11-10"))
        self.assertNotIn("All comparable configurations", report)
        self.assertEqual(report, curate.render(5, [aa()], {"Go": [model()], "Paid": [model()]}, "2026-11-10"))


if __name__ == "__main__":
    unittest.main()
