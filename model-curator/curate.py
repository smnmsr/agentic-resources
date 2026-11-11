#!/usr/bin/env python3
"""Publish AA score/cost Pareto frontiers for OpenCode. Standard library only."""
import argparse
import datetime
import json
import math
import os
from pathlib import Path
import re
from xml.sax.saxutils import escape
import urllib.request

AA_URL = "https://artificialanalysis.ai/api/v2/language/models/free"
CATALOG_URLS = {
    "Go": "https://opencode.ai/inference/go/v1/models",
    "Paid": "https://opencode.ai/inference/v1/models",
}
HERE = Path(__file__).resolve().parent
CLIENT_CATALOG_URL = "https://models.dev/api.json"
SELECTION = {
    "Go": [("Small", 25), ("Medium", 40), ("Strong", None)],
    "Paid": [("Small", 25), ("Medium", 40), ("Strong", 55), ("Flagship", None)],
}
MIN_SCORE_GAP = 3  # Editorial spacing, not a claim about benchmark uncertainty.


def fetch(url, headers=None):
    request_headers = {"User-Agent": "agentic-resources-model-curator/1.0", **(headers or {})}
    with urllib.request.urlopen(urllib.request.Request(url, headers=request_headers), timeout=60) as response:
        return json.load(response)


def fetch_catalogs(key):
    """Models the OpenCode workspace behind `key` can call (public lists include disabled ones)."""
    catalogs = {}
    for channel, url in CATALOG_URLS.items():
        catalog = fetch(url, {"Authorization": f"Bearer {key}"})["data"]
        if not catalog:
            raise ValueError(f"Empty {channel} catalog")
        catalogs[channel] = catalog
    return catalogs


def fetch_aa(key):
    models, version, page = [], None, 1
    while True:
        data = fetch(f"{AA_URL}?page={page}", {"x-api-key": key})
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


def gain_per_doubling(a, b):
    return (b["score"] - a["score"]) / math.log2(b["cost"] / a["cost"])


def upper_hull(entries):
    """Supported choices for score - lambda * log2(cost), lambda >= 0."""
    hull = []
    for point in frontier(entries):
        if hull and point["cost"] == hull[-1]["cost"]:
            continue  # Identical score/cost: retain the deterministic first alias.
        while len(hull) >= 2 and gain_per_doubling(hull[-2], hull[-1]) <= gain_per_doubling(hull[-1], point):
            hull.pop()
        hull.append(point)
    return hull


def shortlist(entries, channel, bands=None, min_score_gap=MIN_SCORE_GAP):
    """One strongest slope-drop corner per band; cheaper near-ties survive."""
    bands = SELECTION[channel] if bands is None else bands
    candidates = []
    lower = -math.inf
    front = frontier(entries)
    for _, upper in bands:
        upper = math.inf if upper is None else upper
        hull = upper_hull([p for p in front if lower <= p["score"] < upper])
        for i, point in enumerate(hull):
            # Endpoints have no knee; use strongest endpoint only as fallback.
            knee = (gain_per_doubling(hull[i - 1], point) - gain_per_doubling(point, hull[i + 1])
                    if 0 < i < len(hull) - 1 else 0)
            candidates.append((point, knee))
        lower = upper
    # Apply tolerance globally, not just within bands; avoid chaining small
    # improvements by comparing to the last retained (cheaper) candidate.
    distinct = []
    for candidate in candidates:
        if not distinct or candidate[0]["score"] - distinct[-1][0]["score"] >= min_score_gap:
            distinct.append(candidate)
    selected = []
    lower = -math.inf
    for label, upper in bands:
        upper = math.inf if upper is None else upper
        eligible = [(p, k) for p, k in distinct if lower <= p["score"] < upper]
        if eligible:
            point, knee = max(eligible, key=lambda item: (item[1], item[0]["score"], -item[0]["cost"]))
            selected.append((label, point))
        lower = upper
    return selected


def selection_table(front, channel):
    picks = shortlist(front, channel)
    if not picks:
        return ["No curated candidates."]
    lines = ["| Tier | Plot # | AA configuration | Score | AA $/task |",
             "|---|---:|---|---:|---:|"]
    for label, point in picks:
        lines.append(f"| {label} | {front.index(point) + 1} | {cell(point['aa_name'])} | "
                     f"{point['score']:g} | {point['cost']:.4f} |")
    return lines


def alias_settings(point):
    """V2 native effort settings, matching core/src/variant.ts (v2.2.7).

    Fail closed for new model families rather than publish an alias at the
    wrong effort. Aliases deliberately have no selectable reasoning variants.
    """
    effort = point["effort"]
    if effort is None:
        return {}
    if effort not in {"none", "minimal", "low", "medium", "high", "xhigh", "max"}:
        raise ValueError(f"Unreviewed alias effort: {effort}")
    if point["id"].startswith("claude-"):
        if effort == "none":
            return {"thinking": {"type": "disabled"}}
        return {"effort": effort, "thinking": {"type": "adaptive", "display": "summarized"}}
    if point["id"].startswith("gpt-"):
        return {"reasoningEffort": effort}
    if point["id"].startswith("gemini-"):
        if effort == "none":
            return {"thinkingConfig": {"includeThoughts": False, "thinkingBudget": 0}}
        return {"thinkingConfig": {"includeThoughts": True, "thinkingLevel": effort}}
    raise ValueError(f"Unreviewed alias effort mapping: {point['id']} ({effort})")


def model_config(aa_models, catalogs, public_catalogs, policy, client_catalog=None):
    providers = {}
    for channel, catalog in catalogs.items():
        if not public_catalogs[channel]:
            raise ValueError(f"Empty {channel} public catalog")
        approved, _ = filter_privacy(catalog, channel, policy)
        front = frontier(intersect(approved, aa_models)[0])
        if not front:
            raise ValueError(f"No {channel} frontier; refusing to disable every model")
        picks = shortlist(front, channel)
        enabled = {point["id"] for _, point in picks}
        known = {m["id"] for m in public_catalogs[channel] + catalog}
        provider_id = "opencode-go" if channel == "Go" else "opencode"
        if client_catalog is not None:
            client_models = client_catalog[provider_id]["models"]
            if not client_models:
                raise ValueError(f"Empty {provider_id} client inventory")
            known.update(client_models)
        models = {mid: {"disabled": mid not in enabled} for mid in sorted(known)}
        for tier, point in picks:
            alias = f"curated-{tier.lower()}"
            if alias in known:
                raise ValueError(f"Alias collides with catalog model: {alias}")
            models[alias] = {
                "modelID": point["id"], "name": f"{tier} — {point['aa_name']}",
                "disabled": False, "settings": alias_settings(point),
            }
            if point["effort"] is not None:
                models[alias]["capabilities"] = {"reasoning": {"supported": point["effort"] != "none"}}
        providers[provider_id] = {"models": dict(sorted(models.items()))}
    # No implicit default choice: defaults can be added here once explicitly chosen.
    return {"providers": providers}


def table(entries):
    lines = ["| # | OpenCode model | AA configuration | Score | AA $/task |",
             "|---:|---|---|---:|---:|"]
    for number, entry in enumerate(entries, 1):
        lines.append(f"| {number} | `{cell(entry['id'])}` | [{cell(entry['aa_name'])}]"
                     f"(https://artificialanalysis.ai/models/{entry['slug']}) | "
                     f"{entry['score']:g} | {entry['cost']:.4f} |")
    return lines if entries else ["No comparable models found."]


def svg_plot(entries, title, x_min, x_max, y_max):
    """Dependency-free SVG XY plot using actual log-scaled cost coordinates."""
    if x_min >= x_max:
        x_min, x_max = x_min / math.sqrt(10), x_max * math.sqrt(10)
    width, height = 960, 500
    left, right, top, bottom = 82, 24, 54, 68
    plot_w, plot_h = width - left - right, height - top - bottom
    log_min, log_max = math.log10(x_min), math.log10(x_max)

    def px(cost):
        return left + (math.log10(cost) - log_min) / (log_max - log_min) * plot_w

    def py(score):
        return top + (y_max - score) / y_max * plot_h

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width / 2:g}" y="30" text-anchor="middle" font-family="sans-serif" '
             f'font-size="20" font-weight="600">{escape(title)}</text>']

    for score in range(0, y_max + 1, 10):
        y = py(score)
        parts += [f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}" stroke="#e5e7eb"/>',
                  f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" font-family="sans-serif" '
                  f'font-size="12" fill="#374151">{score}</text>']

    ticks = [x_min]
    ticks += [10 ** p for p in range(math.ceil(log_min), math.floor(log_max) + 1)]
    if x_max > ticks[-1] * (1 + 1e-9):
        ticks.append(x_max)
    for cost in sorted(set(ticks)):
        x = px(cost)
        parts += [f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}" stroke="#e5e7eb"/>',
                  f'<text x="{x:.2f}" y="{top + plot_h + 22}" text-anchor="middle" font-family="sans-serif" '
                  f'font-size="12" fill="#374151">${cost:.4g}</text>']

    parts += [f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#111827"/>',
              f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#111827"/>']
    ordered = sorted(entries, key=lambda point: point["cost"])
    coords = " ".join(f'{px(point["cost"]):.2f},{py(point["score"]):.2f}' for point in ordered)
    if coords:
        parts.append(f'<polyline points="{coords}" fill="none" stroke="#2563eb" stroke-width="2"/>')
    positions = [(px(point["cost"]), py(point["score"])) for point in ordered]
    labels = []
    for number, (point, (x, y)) in enumerate(zip(ordered, positions), 1):
        tooltip = escape(f'{number}. {point.get("aa_name", point["id"])}: score {point["score"]:g}, ${point["cost"]:.4f}/task')
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" '
                     f'r="4.5" fill="#2563eb" stroke="white" stroke-width="1.5"><title>{tooltip}</title></circle>')
        # Place compact numbered labels without covering other labels or points.
        label_w, label_h = 8 * len(str(number)) + 8, 18
        candidates = [(dx, dy) for dy in (-24, 10, -44, 30, -64, 50)
                      for dx in (10, -label_w - 10, -label_w / 2)]
        for dx, dy in candidates:
            bx, by = x + dx, y + dy
            if not (left <= bx and bx + label_w <= left + plot_w
                    and top <= by and by + label_h <= top + plot_h):
                continue
            if any(bx < ox + ow + 3 and bx + label_w + 3 > ox
                   and by < oy + oh + 3 and by + label_h + 3 > oy
                   for ox, oy, ow, oh in labels):
                continue
            if any(bx - 6 <= ox <= bx + label_w + 6 and by - 6 <= oy <= by + label_h + 6
                   for ox, oy in positions):
                continue
            break
        else:
            bx = min(max(x + 10, left), left + plot_w - label_w)
            by = min(max(y - 24, top), top + plot_h - label_h)
        labels.append((bx, by, label_w, label_h))
        parts += [f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{bx + label_w / 2:.2f}" '
                  f'y2="{by + label_h / 2:.2f}" stroke="#9ca3af" stroke-width="1"/>',
                  f'<rect x="{bx:.2f}" y="{by:.2f}" width="{label_w}" height="{label_h}" '
                  'rx="3" fill="white" stroke="#d1d5db"/>',
                  f'<text x="{bx + label_w / 2:.2f}" y="{by + 13:.2f}" text-anchor="middle" '
                  f'font-family="sans-serif" font-size="12" fill="#111827">{number}</text>']
    if not ordered:
        parts.append(f'<text x="{width / 2:g}" y="{height / 2:g}" text-anchor="middle" '
                     'font-family="sans-serif">No comparable models</text>')
    parts += [f'<text x="{left + plot_w / 2:g}" y="{height - 16}" text-anchor="middle" font-family="sans-serif" '
              'font-size="14" fill="#111827">AA cost per Intelligence Index task (USD, log scale)</text>',
              f'<text x="20" y="{top + plot_h / 2:g}" text-anchor="middle" font-family="sans-serif" '
              'font-size="14" fill="#111827" '
              f'transform="rotate(-90 20 {top + plot_h / 2:g})">AA Intelligence Index score</text>',
              '</svg>', '']
    return "\n".join(parts)


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
             "Point numbers match table rows. Both plots share numeric axes; task cost is logarithmic.",
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
        plot_file = "go.svg" if channel == "Go" else "paid.svg"
        lines += [f"![{channel} Pareto plot](plots/{plot_file})", ""]
        bands = SELECTION[channel]
        bounds = ", ".join(f"{label} <{upper:g}" if upper is not None else f"{label} ≥{bands[-2][1]:g}"
                           for label, upper in bands)
        lines += ["### Curated picks", "",
                  f"Score bands: {bounds} (lower bounds inclusive). "
                  f"Log-cost upper hull within each band; largest slope drop per band. "
                  f"Candidates less than {MIN_SCORE_GAP:g} score points apart keep the cheaper one. "
                  "Empty bands are omitted; endpoint fallback uses the highest score. "
                  "These are selection heuristics, not measured score uncertainty.", ""]
        lines += selection_table(front, channel) + ["", "### Full frontier", ""]
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
              f"[Go catalog]({CATALOG_URLS['Go']}) · [Paid catalog]({CATALOG_URLS['Paid']}), "
              "authenticated: workspace-enabled models only."]
    return "\n".join(lines) + "\n"


def write_plots(aa_models, catalogs, policy, plot_dir):
    chart_data = {}
    for channel, catalog in catalogs.items():
        if policy is not None:
            catalog, _ = filter_privacy(catalog, channel, policy)
        entries, _, _ = intersect(catalog, aa_models)
        chart_data[channel] = frontier(entries)
    points = [point for channel_points in chart_data.values() for point in channel_points]
    x_min = min((point["cost"] for point in points), default=0.01)
    x_max = max((point["cost"] for point in points), default=10)
    y_max = max(10, int(math.ceil(max((point["score"] for point in points), default=10) / 10) * 10))
    plot_dir.mkdir(parents=True, exist_ok=True)
    for channel, channel_points in chart_data.items():
        filename = "go.svg" if channel == "Go" else "paid.svg"
        (plot_dir / filename).write_text(svg_plot(channel_points, f"{channel} Pareto frontier",
                                                x_min, x_max, y_max))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "MODELS.md")
    parser.add_argument("--models-output", type=Path,
                        default=HERE.parent / "opencode-config" / "models.json")
    args = parser.parse_args()
    key = os.environ.get("AA_API_KEY")
    opencode_key = os.environ.get("OPENCODE_API_KEY")
    if not key or not opencode_key:
        parser.error("AA_API_KEY and OPENCODE_API_KEY are required")
    version, models = fetch_aa(key)
    catalogs = fetch_catalogs(opencode_key)
    public_catalogs = {channel: fetch(url)["data"] for channel, url in CATALOG_URLS.items()}
    policy = json.loads((HERE / "privacy.json").read_text())
    config = model_config(models, catalogs, public_catalogs, policy, fetch(CLIENT_CATALOG_URL))
    report = render(version, models, catalogs, datetime.datetime.now(datetime.timezone.utc).date().isoformat(), policy)
    args.output.write_text(report)
    write_plots(models, catalogs, policy, args.output.parent / "plots")
    args.models_output.parent.mkdir(parents=True, exist_ok=True)
    args.models_output.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
