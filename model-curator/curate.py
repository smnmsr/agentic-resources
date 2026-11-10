#!/usr/bin/env python3
"""Publish AA score/cost Pareto frontiers for OpenCode. Standard library only."""
import argparse
import datetime
import json
import math
import os
from pathlib import Path
import re
import urllib.request

AA_URL = "https://artificialanalysis.ai/api/v2/language/models/free"
CATALOG_URLS = {
    "Go": "https://opencode.ai/inference/go/v1/models",
    "Paid": "https://opencode.ai/inference/v1/models",
}
HERE = Path(__file__).resolve().parent


def fetch(url, key=None):
    headers = {"User-Agent": "agentic-resources-model-curator/1.0"}
    if key:
        headers["x-api-key"] = key
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return json.load(response)


def fetch_aa(key):
    models, version, page = [], None, 1
    while True:
        data = fetch(f"{AA_URL}?page={page}", key)
        current = data["intelligence_index_version"]
        if version is not None and current != version:
            raise ValueError("AA index version changed during pagination; retry the run")
        version = current
        models.extend(data["data"])
        pagination = data["pagination"]
        if pagination["page"] != page:
            raise ValueError("Unexpected AA pagination")
        if not pagination["has_more"]:
            break
        page += 1
        if page > 100:
            raise ValueError("Unexpected number of AA pages")
    if not models:
        raise ValueError("AA returned no models")
    return version, models


def normalized(value):
    # Punctuation only: do NOT erase dates, versions, or preview suffixes.
    return re.sub(r"[^a-z0-9]", "", value.lower())


def aa_identity(model):
    name = model["name"]
    base = name.split("(", 1)[0].strip()
    qualifiers = name[len(base):].lower()
    effort = re.search(r"\b(non-reasoning|reasoning|xhigh|max|high|medium|low|minimal|none)\b", qualifiers)
    return normalized(base), effort.group(1) if effort else None


def usable_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def measures(model):
    score = (model.get("evaluations") or {}).get("artificial_analysis_intelligence_index")
    cost = ((model.get("artificial_analysis_intelligence_index_cost") or {})
            .get("cost_per_task") or {}).get("total_cost")
    return score, cost


def effort_supported(model, effort):
    reasoning = model.get("capabilities", {}).get("reasoning", {})
    if not effort:
        return True  # AA's named/default configuration; not an inferred effort.
    if effort == "non-reasoning":
        return reasoning.get("toggle") is True or reasoning.get("supported") is False
    if effort == "reasoning":
        return reasoning.get("supported") is True
    return effort in reasoning.get("effort", [])


def pricing(model):
    text = model.get("cost", {}).get("text", {})
    input_price = text.get("input", {}).get("price")
    output_price = text.get("output", {}).get("price")
    return input_price, output_price


def price_rules(model):
    """Expose upstream rules; never silently apply them to AA task costs."""
    cost = model.get("cost", {})
    rules = cost.get("multipliers") or []
    regular_factor = 1
    # Only infer a post-promo price from an unambiguous, date-only rule.
    if len(rules) == 1:
        rule = rules[0]
        when = rule.get("when", {})
        date = when.get("date", {})
        if (set(when) == {"date"} and set(date) == {"gte"}
                and usable_number(rule.get("factor")) and rule["factor"] > 1):
            regular_factor = rule["factor"]
    return rules, regular_factor


def regular_counterpart(model, catalog):
    canonical = model.get("canonical_id")
    for candidate in catalog:
        same_model = (canonical and candidate.get("canonical_id") == canonical
                      or candidate["id"] == model["id"].removesuffix("-free"))
        inp, out = pricing(candidate)
        if (same_model and candidate["id"] != model["id"]
                and all(usable_number(v) and v >= 0 for v in (inp, out)) and inp + out > 0):
            _, factor = price_rules(candidate)
            return f"`{candidate['id']}`: ${inp * factor:g}/${out * factor:g} (base/post-promo rates)"
    return None


def intersect(catalog, aa_models):
    entries, missing, offers = [], [], []
    for model in sorted(catalog, key=lambda m: m["id"]):
        if model.get("type", "chat") != "chat":
            continue
        inp, out = pricing(model)
        if not all(usable_number(v) and v >= 0 for v in (inp, out)):
            missing.append((model["id"], "no usable text pricing"))
            continue
        free = inp == out == 0
        rules, factor = price_rules(model)
        if free or rules:
            offers.append({"id": model["id"], "input": inp, "output": out,
                           "rules": rules, "free": free, "factor": factor,
                           "counterpart": regular_counterpart(model, catalog) if free else None})
        if free:
            # Free/promo endpoints are separate, not zero-cost frontier points.
            continue
        identities = {normalized(model["id"]), normalized(model.get("name", ""))}
        canonical = model.get("canonical_id", "").split("/")[-1]
        if canonical:
            identities.add(normalized(canonical))
        matches = [a for a in aa_models if aa_identity(a)[0] in identities]
        # AA slugs cover punctuation aliases, but never use an effort slug as a base alias.
        matches += [a for a in aa_models if a not in matches and normalized(a["slug"]) in identities]
        matched = False
        reasons = set()
        for aa in matches:
            score, task_cost = measures(aa)
            if not (usable_number(score) and usable_number(task_cost) and task_cost > 0):
                reasons.add("AA score or positive task cost missing")
                continue
            effort = aa_identity(aa)[1]
            if not effort_supported(model, effort):
                reasons.add("AA effort not explicitly supported by catalog")
                continue
            entries.append({"id": model["id"], "aa_name": aa["name"], "slug": aa["slug"],
                            "effort": effort, "score": score, "cost": task_cost})
            matched = True
        if not matched:
            missing.append((model["id"], "; ".join(sorted(reasons)) or "no exact AA identity match"))
    return entries, missing, offers


def frontier(entries):
    return sorted((point for point in entries if not any(
        other["cost"] <= point["cost"] and other["score"] >= point["score"]
        and (other["cost"] < point["cost"] or other["score"] > point["score"])
        for other in entries)), key=lambda p: (p["cost"], -p["score"], p["id"], p["slug"]))


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(entries):
    lines = ["| OpenCode model | AA configuration | Score | AA $/task |",
             "|---|---|---:|---:|"]
    for entry in entries:
        lines.append(f"| `{cell(entry['id'])}` | [{cell(entry['aa_name'])}]"
                     f"(https://artificialanalysis.ai/models/{entry['slug']}) | "
                     f"{entry['score']:g} | {entry['cost']:.4f} |")
    return lines if entries else ["No comparable models found."]


def render(version, aa_models, catalogs, date):
    scored = sum(usable_number(measures(m)[0]) for m in aa_models)
    lines = ["# OpenCode model Pareto frontiers", "", f"Fetched {date}; AA Intelligence Index version {version:g} "
             "(API reports major.minor, not patch).", "",
             f"AA catalog: {len(aa_models)} configurations, {scored} with a current score.", "",
             "## How to read this", "",
             "Higher intelligence and lower AA cost per task are better. A frontier entry is not "
             "strictly dominated on both axes. Equal points are retained; effort variants are separate points.",
             "", "Both tables use **AA cost per Intelligence Index task**, not token prices, "
             "OpenCode charges, or measured Go allowance consumption. Go is the Go-available subset, "
             "not an allowance-adjusted frontier. AA costs are a proxy; discounts, caching and routing "
             "can make actual OpenCode costs differ. Cost is per benchmark task, not per successful task.",
             "", "Matching preserves versions and dates; no fuzzy or cross-version score substitution. "
             "Named/default AA configurations remain named/default; explicit effort settings must be "
             "supported by the catalog. Availability does not imply privacy-policy approval.", ""]
    for channel, catalog in catalogs.items():
        entries, missing, offers = intersect(catalog, aa_models)
        front = frontier(entries)
        lines += [f"## {channel} frontier", "",
                  f"{len(catalog)} catalog endpoints; {len(set(e['id'] for e in entries))} matched paid-price "
                  f"endpoints; {len(entries)} comparable configurations; {len(front)} frontier points.", ""]
        lines += table(front) + ["", "<details>", "<summary>All comparable configurations</summary>", ""]
        lines += table(sorted(entries, key=lambda e: (e['id'], e['cost']))) + ["", "</details>", ""]
        lines += [f"### {channel}: free endpoints and special pricing (separate)", "",
                  "These do not change the AA cost axis. Free endpoints are excluded from the frontier. "
                  "Discounted paid models remain eligible using AA reference costs. OpenCode rates below "
                  "are input/output dollars per million tokens, for context only.", ""]
        for offer in offers:
            lines += [f"- `{offer['id']}`: catalog rates ${offer['input']:g}/${offer['output']:g}."
                      + (" Free endpoint; regular price not supplied by this catalog entry." if offer['free'] else "")]
            if offer['factor'] != 1:
                lines += [f"  - Post-promotion rates inferred from the date-only multiplier: "
                          f"${offer['input'] * offer['factor']:g}/${offer['output'] * offer['factor']:g}."]
            if offer['counterpart']:
                lines += [f"  - Nonfree counterpart in this catalog: {offer['counterpart']}."]
            if offer['rules']:
                lines += [f"  - Published pricing rules: `{json.dumps(offer['rules'], sort_keys=True)}`"]
        if not offers:
            lines += ["None reported by the catalog."]
        lines += ["", "<details>", "<summary>Unmatched or insufficient data</summary>", ""]
        lines += [f"- `{cell(mid)}`: {cell(reason)}" for mid, reason in missing] or ["None."]
        lines += ["", "</details>", ""]
    lines += ["## Sources", "", "Scores and benchmark task costs: [Artificial Analysis](https://artificialanalysis.ai/) "
              f"([free API]({AA_URL})).", ""]
    lines += [f"- OpenCode {channel}: {url}" for channel, url in CATALOG_URLS.items()]
    lines += ["", "No model selections or local configuration are changed by this report."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "MODELS.md")
    args = parser.parse_args()
    key = os.environ.get("AA_API_KEY")
    if not key:
        parser.error("AA_API_KEY is required")
    version, models = fetch_aa(key)
    catalogs = {}
    for channel, url in CATALOG_URLS.items():
        catalog = fetch(url)["data"]
        if not catalog:
            raise ValueError(f"Empty {channel} catalog")
        catalogs[channel] = catalog
    report = render(version, models, catalogs, datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    args.output.write_text(report)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
