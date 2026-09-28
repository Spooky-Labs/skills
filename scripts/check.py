#!/usr/bin/env python3
"""Validate this repository as an Agent Plugins 1.0.0 package.

Standard library only, so the check runs anywhere a checkout does. The rules
are the two specifications' own:

- plugin.json (Agent Plugins 1.0.0): a JSON object whose "$schema" is exactly
  https://agent-plugins.org/schemas/1.0.0/plugin.schema.json, whose "name" is
  1-64 characters of lowercase letters, digits, hyphens and periods, starts and
  ends alphanumeric and contains no "--" or "..", and whose other top-level
  fields are only the ones the closed schema permits.
- skills/<dir>/SKILL.md (Agent Skills): YAML front matter with a "name" that
  equals the directory name (1-64 characters, lowercase letters, digits and
  hyphens, no leading, trailing or consecutive hyphen) and a non-empty
  "description" of at most 1024 characters.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MANIFEST_FIELDS = {"$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"}
PLUGIN_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SKILL_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")

problems: list[str] = []


def problem(msg: str) -> None:
    problems.append(msg)
    print(f"error: {msg}", file=sys.stderr)


def check_manifest() -> None:
    path = ROOT / "plugin.json"
    if not path.is_file():
        problem("plugin.json is missing at the package root")
        return
    try:
        manifest = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        problem(f"plugin.json is not JSON: {e}")
        return
    if not isinstance(manifest, dict):
        problem("plugin.json must hold a JSON object")
        return
    if manifest.get("$schema") != SCHEMA:
        problem(f'plugin.json "$schema" must be exactly {SCHEMA}')
    name = manifest.get("name")
    if not isinstance(name, str) or not (1 <= len(name) <= 64) or not PLUGIN_NAME.match(name) or "--" in name or ".." in name:
        problem(f'plugin.json "name" {name!r} breaks the Agent Plugins name rules')
    for field in manifest:
        if field not in MANIFEST_FIELDS:
            problem(f'plugin.json field "{field}" is not in the closed manifest schema')
    for field in ("version", "description", "homepage", "repository", "license"):
        if field in manifest and not isinstance(manifest[field], str):
            problem(f'plugin.json "{field}" must be a string')
    if "keywords" in manifest and not (isinstance(manifest["keywords"], list) and all(isinstance(k, str) for k in manifest["keywords"])):
        problem('plugin.json "keywords" must be an array of strings')


def front_matter(doc: str) -> dict[str, str]:
    body = doc.lstrip("﻿\n\r ")
    if not body.startswith("---"):
        raise ValueError("no front matter")
    rest = body[3:]
    end = rest.find("\n---")
    if end < 0:
        raise ValueError("unterminated front matter")
    fields: dict[str, str] = {}
    for line in rest[:end].splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def check_skills() -> None:
    skills = ROOT / "skills"
    if not skills.is_dir():
        problem("skills/ is missing; the package would carry no skills")
        return
    seen = 0
    for entry in sorted(skills.iterdir()):
        if not entry.is_dir():
            problem(f"skills/{entry.name} is a file; only skill directories belong under skills/")
            continue
        doc = entry / "SKILL.md"
        if not doc.is_file():
            problem(f"skills/{entry.name}/SKILL.md is missing; the runtime would not see the skill")
            continue
        seen += 1
        try:
            fields = front_matter(doc.read_text())
        except ValueError as e:
            problem(f"skills/{entry.name}/SKILL.md: {e}")
            continue
        name = fields.get("name", "")
        if name != entry.name:
            problem(f"skills/{entry.name}/SKILL.md: name {name!r} must equal the directory name")
        if not (1 <= len(name) <= 64) or not SKILL_NAME.match(name) or "--" in name:
            problem(f"skills/{entry.name}/SKILL.md: name {name!r} breaks the Agent Skills name rules")
        description = fields.get("description", "")
        if not (1 <= len(description) <= 1024):
            problem(f"skills/{entry.name}/SKILL.md: description must be 1-1024 characters")
        if ": " in description:
            problem(f"skills/{entry.name}/SKILL.md: description contains a colon and a space, which is not a valid unquoted YAML scalar")
    if seen == 0:
        problem("skills/ holds no skill")


check_manifest()
check_skills()
if problems:
    print(f"{len(problems)} problem(s)", file=sys.stderr)
    sys.exit(1)
print("package ok")
