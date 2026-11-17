#!/usr/bin/env python3
"""Validate and merge OpenCode V2 fragments. Requires jsonschema."""
import argparse
import json
from pathlib import Path
import urllib.request

SCHEMA_URL = "https://opencode.ai/config.json"
MODEL_FIELDS = {"providers", "model"}


def download(url):
    if not url.startswith("https://"):
        raise ValueError("HTTPS required")
    request = urllib.request.Request(url, headers={"User-Agent": "opencode-config-sync/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if not response.url.startswith("https://"):
            raise ValueError("Insecure redirect")
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Config exceeds size limit")
    return data


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def decode(data):
    def invalid(value):
        raise ValueError(f"Invalid JSON number: {value}")
    result = json.loads(data, object_pairs_hook=unique_object, parse_constant=invalid)
    if not isinstance(result, dict):
        raise ValueError("Config must be a JSON object")
    return result


def merge(models, settings):
    overlap = models.keys() & settings.keys()
    if overlap:
        raise ValueError(f"Conflicting fields: {sorted(overlap)}")
    if models.keys() - MODEL_FIELDS or settings.keys() & MODEL_FIELDS:
        raise ValueError("Models owns providers/model; settings owns all other fields")
    return {"$schema": SCHEMA_URL, **settings, **models}


def validate(document, schema=None):
    import jsonschema
    schema = schema if schema is not None else decode(download(SCHEMA_URL))
    jsonschema.validators.validator_for(schema)(schema).validate(document)
    # Additional curation invariants, beyond JSON Schema's shape checks.
    for provider in ("opencode", "opencode-go"):
        models = document.get("providers", {}).get(provider, {}).get("models", {})
        if not models or not any(m.get("disabled") is False for m in models.values()):
            raise ValueError(f"No enabled curated models for {provider}")
        for mid, model in models.items():
            if not isinstance(model.get("disabled"), bool):
                raise ValueError(f"Missing explicit enablement: {provider}/{mid}")
            if "modelID" in model:
                # Aliases resolve their target from the catalog, so the target only has to exist here.
                if model.get("modelID") not in models:
                    raise ValueError(f"Alias target missing: {provider}/{mid}")
    default = document.get("model")
    if default is not None:
        if not isinstance(default, str) or "/" not in default or "#" in default:
            raise ValueError("Default must be provider/model without a variant")
        provider, mid = default.split("/", 1)
        model = document.get("providers", {}).get(provider, {}).get("models", {}).get(mid)
        if model is None or model.get("disabled") is not False:
            raise ValueError("Default model is not enabled in the generated inventory")
    validate_agents(document)


def agent_settings(directory, settings):
    agents = dict(settings.get("agents", {}))
    for path in sorted((directory / "agents").glob("*.json")):
        fragment = decode(path.read_bytes())
        if set(fragment) != {"agents"} or not isinstance(fragment["agents"], dict):
            raise ValueError(f"Expected an agents object: {path}")
        overlap = agents.keys() & fragment["agents"].keys()
        if overlap:
            raise ValueError(f"Duplicate agents: {sorted(overlap)}")
        agents.update(fragment["agents"])
    root = (directory / "prompts").resolve()
    for name, definition in agents.items():
        agent = agents[name] = dict(definition)
        system = agent.get("system", "")
        if system.startswith("{file:") and system.endswith("}"):
            path = (directory / system[6:-1]).resolve()
            if not path.is_relative_to(root):
                raise ValueError(f"Prompt outside prompts directory: {name}")
            agent["system"] = path.read_text().strip()
            if not agent["system"]:
                raise ValueError(f"Empty prompt: {name}")
        if "{file:" in agent.get("system", ""):
            raise ValueError(f"Unresolved prompt reference: {name}")
    return {**settings, "agents": agents} if agents else settings


def validate_agents(document):
    agents = document.get("agents", {})
    for name, agent in agents.items():
        reference = agent.get("model")
        if reference is not None:
            if not isinstance(reference, str) or "/" not in reference or "#" in reference:
                raise ValueError(f"Expected provider/model for agent: {name}")
            provider, mid = reference.split("/", 1)
            model = document.get("providers", {}).get(provider, {}).get("models", {}).get(mid)
            if model is None or model.get("disabled") is not False:
                raise ValueError(f"Agent model is not enabled: {name}: {reference}")


def build(directory):
    document = merge(decode((directory / "models.json").read_bytes()),
                     agent_settings(directory, decode((directory / "settings.json").read_bytes())))
    validate(document)
    output = directory / "opencode.json"
    output.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(build(args.directory))
