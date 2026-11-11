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


def filter_privacy(catalog, channel, policy):
    approved = set(policy["allowed"][channel])
    return ([m for m in catalog if m["id"] in approved],
            [m["id"] for m in catalog if m["id"] not in approved])


def render(version, aa_models, catalogs, date, policy=None):
    scored = sum(usable_number(measures(m)[0]) for m in aa_models)
    version_label = str(version) if "." in str(version) else f"{version}.0"
    lines = ["# OpenCode model frontiers", "",
             f"**AA Intelligence Index v{version_label} · {date} · {scored} scored configurations**", "",
             "Higher score, lower AA $/task is better. Each row is a non-dominated model/effort combination.",
             "AA benchmark-task cost is a proxy—not your OpenCode bill or Go allowance usage. "
             "API version excludes patch numbers. [Methodology](README.md).", ""]
    all_offers = {}
    excluded = {}
    for channel, catalog in catalogs.items():
        total = len(catalog)
        if policy is not None:
            catalog, excluded[channel] = filter_privacy(catalog, channel, policy)
        entries, missing, offers = intersect(catalog, aa_models)
        front = frontier(entries)
        lines += [f"## {channel} frontier", "",
                  f"**{len(set(e['id'] for e in entries))}/{total} endpoints matched · "
                  f"{len(entries)} configurations · {len(front)} frontier points**", ""]
        lines += table(front) + [""]
        if missing:
            reasons = {}
            for _, reason in missing:
                category = ("unsupported effort" if "effort" in reason else
                            "missing score/cost" if "AA score" in reason else "unmatched identity/pricing")
                reasons[category] = reasons.get(category, 0) + 1
            lines += ["Not ranked: " + "; ".join(f"{count} {reason}" for reason, count in sorted(reasons.items())) + ".", ""]
        for offer in offers:
            key = (offer['id'], offer['input'], offer['output'], json.dumps(offer['rules'], sort_keys=True))
            if key not in all_offers:
                all_offers[key] = (offer, [])
            all_offers[key][1].append(channel)
    if policy is not None:
        lines += ["## Privacy filter", "",
                  f"No request-data training; US/EU hosting only. Unknown endpoints excluded. Reviewed {policy['verified_on']}."]
        for channel, ids in excluded.items():
            lines += [f"- {channel}: " + (", ".join(f"`{mid}`" for mid in sorted(ids)) or "none excluded") + "."]
        lines += ["Policy sources: " + " · ".join(f"[{channel}]({url})" for channel, url in policy['sources'].items()) + ".", ""]
    lines += ["## Special pricing", "", "OpenCode input/output $ per million tokens; does not alter AA $/task.", "",
              "| Model | Available on | Catalog rates | Regular rates / condition |", "|---|---|---:|---|"]
    free_counts = {}
    for offer, channels in all_offers.values():
        if offer['free']:
            for channel in channels:
                free_counts[channel] = free_counts.get(channel, 0) + 1
            continue
        condition = "Conditional pricing; see catalog"
        if offer['factor'] != 1:
            starts = offer['rules'][0]['when']['date']['gte']
            condition = (f"${offer['input'] * offer['factor']:g}/${offer['output'] * offer['factor']:g} "
                         f"from {starts}")
        elif offer['rules']:
            condition = "; ".join(f"×{r.get('factor', '?')} under catalog conditions" for r in offer['rules'])
        lines += [f"| `{offer['id']}` | {', '.join(channels)} | ${offer['input']:g}/${offer['output']:g} | {condition} |"]
    lines += ["", "Free endpoints excluded: " + (", ".join(f"{count} {channel}" for channel, count in free_counts.items()) or "none") + ".", "",
              "Sources: [Artificial Analysis](https://artificialanalysis.ai/) · "
              f"[Go catalog]({CATALOG_URLS['Go']}) · [Paid catalog]({CATALOG_URLS['Paid']})."]
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
    policy = json.loads((HERE / "privacy.json").read_text())
    report = render(version, models, catalogs, datetime.datetime.now(datetime.timezone.utc).date().isoformat(), policy)
    args.output.write_text(report)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
