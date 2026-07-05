"""Unit tests for scripts/registry_check.py (skill registration consistency)."""
import importlib.util
import os
import shutil
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stderr

_MODULE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "registry_check.py")


def _load():
    spec = importlib.util.spec_from_file_location("registry_check", _MODULE_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


rc = _load()

SKILL_MD = """---
name: demo-skill
version: 1.2.3
description: "A demo."
---
# Demo

## KB Mode (Dual-Mode Output)

Canonical contract: modules/kb-mode.md. There is deliberately no `--kb` force flag.
If `--scope` is missing or invalid: HARD STOP. Do not guess a scope.
"""

KB_MODE = """# KB Mode: Canonical Dual-Mode Contract

| Skill | Section | Resolution point | KB-mode gate |
|---|---|---|---|
| demo-skill | KB Mode (Dual-Mode Output) | pre-flight | demo-gate |
"""

CHANGELOG = """# Changelog

## [1.2.3] - 2026-07-05

### Added
- Demo.
"""

README = """# Repo

| Skill | Version | Description |
|-------|---------|-------------|
| [demo-skill](skills/demo-skill/SKILL.md) | 1.2.3 | Demo |
"""

CLAUDE = """# Repo

## Available Skills

### demo-skill (v1.2.3)
Demo.
"""

MARKETPLACE = """{
  "plugins": [
    {
      "name": "x",
      "description": "1 skills for demos",
      "skills": ["./skills/demo-skill"]
    }
  ]
}
"""


class _Fixture:
    def __enter__(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "skills", "demo-skill"))
        os.makedirs(os.path.join(self.d, ".claude-plugin"))
        self.write("skills/demo-skill/SKILL.md", SKILL_MD)
        self.write("skills/demo-skill/CHANGELOG.md", CHANGELOG)
        self.write("README.md", README)
        self.write("CLAUDE.md", CLAUDE)
        self.write(".claude-plugin/marketplace.json", MARKETPLACE)
        self.write("modules/kb-mode.md", KB_MODE)
        return self

    def write(self, rel, content):
        p = os.path.join(self.d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(content)

    def __exit__(self, *a):
        shutil.rmtree(self.d, ignore_errors=True)


def _run(fixture_dir):
    orig = rc.repo_root
    rc.repo_root = lambda: fixture_dir
    try:
        buf = StringIO()
        with redirect_stderr(buf):
            code = rc.main()
        return code, buf.getvalue()
    finally:
        rc.repo_root = orig


class TestRegistryCheck(unittest.TestCase):
    def test_clean_fixture_passes(self):
        with _Fixture() as f:
            code, out = _run(f.d)
            self.assertEqual(code, 0, out)

    def test_stale_readme_version_fails(self):
        with _Fixture() as f:
            f.write("README.md", README.replace("| 1.2.3 |", "| 1.2.2 |"))
            code, out = _run(f.d)
            self.assertEqual(code, 1)
            self.assertIn("README.md", out)

    def test_missing_claude_header_fails(self):
        with _Fixture() as f:
            f.write("CLAUDE.md", CLAUDE.replace("(v1.2.3)", "(v1.0.0)"))
            code, out = _run(f.d)
            self.assertEqual(code, 1)
            self.assertIn("CLAUDE.md", out)

    def test_changelog_drift_fails(self):
        with _Fixture() as f:
            f.write("skills/demo-skill/CHANGELOG.md", CHANGELOG.replace("[1.2.3]", "[1.2.2]"))
            code, out = _run(f.d)
            self.assertEqual(code, 1)
            self.assertIn("changelog top entry", out)

    def test_inline_changelog_table_parsed(self):
        with _Fixture() as f:
            os.remove(os.path.join(f.d, "skills/demo-skill/CHANGELOG.md"))
            f.write("skills/demo-skill/SKILL.md", SKILL_MD + """
## Changelog

| Version | Changes |
|---------|---------|
| 1.2.3 | Demo. |
""")
            code, out = _run(f.d)
            self.assertEqual(code, 0, out)

    def test_unlisted_marketplace_skill_fails(self):
        with _Fixture() as f:
            f.write(".claude-plugin/marketplace.json", MARKETPLACE.replace(
                '"skills": ["./skills/demo-skill"]', '"skills": []'))
            code, out = _run(f.d)
            self.assertEqual(code, 1)
            self.assertIn("marketplace.json does not list", out)

    def test_dead_skill_dir_fails(self):
        with _Fixture() as f:
            os.makedirs(os.path.join(f.d, "skills", "ghost"))
            code, out = _run(f.d)
            self.assertEqual(code, 1)
            self.assertIn("no SKILL.md", out)

    def test_kb_mode_drift_fails(self):
        with _Fixture() as f:
            f.write("skills/demo-skill/SKILL.md",
                    SKILL_MD.replace("There is deliberately no `--kb` force flag.", ""))
            code, out = _run(f.d)
            self.assertEqual(code, 1)
            self.assertIn("KB-mode copy drifted", out)

    def test_missing_kb_module_fails(self):
        with _Fixture() as f:
            os.remove(os.path.join(f.d, "modules", "kb-mode.md"))
            code, out = _run(f.d)
            self.assertEqual(code, 1)
            self.assertIn("kb-mode.md missing", out)

    def test_wrong_count_in_description_fails(self):
        with _Fixture() as f:
            f.write(".claude-plugin/marketplace.json", MARKETPLACE.replace("1 skills", "7 skills"))
            code, out = _run(f.d)
            self.assertEqual(code, 1)
            self.assertIn("skills', actual count", out)


if __name__ == "__main__":
    unittest.main()
