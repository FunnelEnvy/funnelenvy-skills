#!/usr/bin/env python3
"""registry_check.py -- verify skill registration consistency across the repo.

Source of truth: skills/*/SKILL.md YAML frontmatter (name, version). Every other
place a skill or its version appears is a registry that must match:

  1. README.md skills table: a row linking skills/<name>/SKILL.md with the exact version
  2. CLAUDE.md "Available Skills": a "### <name> (v<version>)" header per skill
  3. .claude-plugin/marketplace.json: plugins[].skills lists ./skills/<name>
  4. marketplace.json plugin description "N skills" count matches the actual count
  5. The skill's changelog top entry matches the frontmatter version
     (separate CHANGELOG.md "## [x.y.z]" or inline "## Changelog" table "| x.y.z |")
  6. KB-mode drift canary: every skill listed in modules/kb-mode.md carries the canonical
     section header, the module pointer, and the invariant sentences (HARD STOP scope
     semantics, no --kb force flag, do-not-guess). Full semantics live in the module;
     this only catches a copy drifting away from the contract.

Also fails on registry entries pointing at skills that do not exist on disk.
The repo's "README Sync Rule" and "skill registration is a package deal" practice
make every mismatch here a bug, not noise.

Stdlib only. Run from anywhere inside the repo. Exit 0 clean, 1 on drift.
"""

import json
import os
import re
import subprocess
import sys


def repo_root():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                      stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return os.getcwd()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def skill_frontmatter(skill_md_text):
    """Return (name, version) from SKILL.md YAML frontmatter, or (None, None)."""
    m = re.match(r"---\n(.*?)\n---", skill_md_text, re.S)
    if not m:
        return None, None
    fm = m.group(1)
    name = re.search(r'^name:\s*"?([\w-]+)"?\s*$', fm, re.M)
    version = re.search(r'^version:\s*"?(\d+\.\d+\.\d+)"?\s*$', fm, re.M)
    return (name.group(1) if name else None,
            version.group(1) if version else None)


def changelog_top_version(skill_dir, skill_md_text):
    """Top changelog version: separate CHANGELOG.md or inline '## Changelog' table.
    Returns None if the skill has no changelog (itself reported as an error)."""
    cl = os.path.join(skill_dir, "CHANGELOG.md")
    if os.path.exists(cl):
        m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", read(cl), re.M)
        return m.group(1) if m else None
    m = re.search(r"^## Changelog\s*\n+\|[^\n]*\|\s*\n\|[-| ]*\|\s*\n\|\s*(\d+\.\d+\.\d+)\s*\|",
                  skill_md_text, re.M)
    return m.group(1) if m else None


def main():
    root = repo_root()
    errors = []

    skills = {}
    skills_dir = os.path.join(root, "skills")
    for d in sorted(os.listdir(skills_dir)):
        skill_md = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isdir(os.path.join(skills_dir, d)):
            continue
        if not os.path.exists(skill_md):
            errors.append("skills/%s/ has no SKILL.md (dead directory or unfinished skill)" % d)
            continue
        text = read(skill_md)
        name, version = skill_frontmatter(text)
        if name != d:
            errors.append("skills/%s/SKILL.md frontmatter name is %r, expected %r" % (d, name, d))
        if not version:
            errors.append("skills/%s/SKILL.md has no parseable semver version" % d)
            continue
        skills[d] = version
        cl_ver = changelog_top_version(os.path.join(skills_dir, d), text)
        if cl_ver is None:
            errors.append("skills/%s has no changelog (CHANGELOG.md or inline ## Changelog table)" % d)
        elif cl_ver != version:
            errors.append("skills/%s changelog top entry is %s, frontmatter is %s" % (d, cl_ver, version))

    readme = read(os.path.join(root, "README.md"))
    claude = read(os.path.join(root, "CLAUDE.md"))
    for name, version in skills.items():
        row = "[%s](skills/%s/SKILL.md) | %s |" % (name, name, version)
        if row not in readme:
            errors.append("README.md skills table missing or version-stale for %s (expected '| %s')" % (name, version))
        header = "### %s (v%s" % (name, version)
        if header not in claude:
            errors.append("CLAUDE.md Available Skills missing or version-stale for %s (expected '%s')" % (name, header))

    # Registry rows pointing at skills that do not exist
    for m in re.finditer(r"\[([\w-]+)\]\(skills/([\w-]+)/SKILL\.md\)", readme):
        if m.group(2) not in skills:
            errors.append("README.md links skills/%s/SKILL.md which does not exist" % m.group(2))

    mp_path = os.path.join(root, ".claude-plugin", "marketplace.json")
    mp = json.loads(read(mp_path))
    listed = set()
    for plugin in mp.get("plugins", []):
        for entry in plugin.get("skills", []):
            listed.add(entry.rstrip("/").split("/")[-1])
        desc = plugin.get("description", "")
        m = re.search(r"(\d+) skills", desc)
        if m and int(m.group(1)) != len(skills):
            errors.append("marketplace.json plugin description says '%s skills', actual count is %d"
                          % (m.group(1), len(skills)))
    for name in skills:
        if name not in listed:
            errors.append("marketplace.json does not list skills/%s" % name)
    for name in listed:
        if name not in skills:
            errors.append("marketplace.json lists skills/%s which does not exist" % name)

    # KB-mode drift canary: dual-mode skills derived from the module's own table
    kb_module = os.path.join(root, "modules", "kb-mode.md")
    if os.path.exists(kb_module):
        table_skills = re.findall(r"^\| ([\w-]+) \| KB Mode", read(kb_module), re.M)
        if not table_skills:
            errors.append("modules/kb-mode.md dual-mode table parsed to zero skills (table format changed?)")
        for name in table_skills:
            if name not in skills:
                errors.append("modules/kb-mode.md lists dual-mode skill %s which does not exist" % name)
                continue
            text = read(os.path.join(skills_dir, name, "SKILL.md"))
            for marker, why in (
                ("KB Mode (Dual-Mode Output)", "canonical section header"),
                ("modules/kb-mode.md", "pointer to the canonical contract"),
                ("no `--kb` force flag", "no-force-flag invariant"),
                ("HARD STOP", "scope hard-stop invariant"),
                ("Do not guess a scope", "do-not-guess invariant"),
            ):
                if marker not in text:
                    errors.append("skills/%s/SKILL.md KB-mode copy drifted: missing %s (%r)" % (name, why, marker))
    else:
        errors.append("modules/kb-mode.md missing (canonical KB-mode contract)")

    if errors:
        sys.stderr.write("registry-check: %d inconsistencies\n" % len(errors))
        for e in errors:
            sys.stderr.write("  - %s\n" % e)
        return 1
    sys.stderr.write("registry-check: clean (%d skills, all registries in sync)\n" % len(skills))
    return 0


if __name__ == "__main__":
    sys.exit(main())
