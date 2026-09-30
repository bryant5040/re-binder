"""Checks that catch mistakes before anything ships. Exit code 0 means all good.

- every skill's copies of shared/ match (run tools/sync_shared.py to fix)
- every skill's frontmatter: allowed keys only, the name matches its folder, lowercase letters, digits
  and hyphens, no "claude" or "anthropic", and a description of 200 characters or less with no tags
- plugin.json: valid, a description of 200 characters or less, and no web address in it
- no bin/ folder in the plugin (claude.ai refuses it)
- every relative link in the top pages, plugin/, shared/, docs/, guardrails/ and evals/ points at a
  real file
- the tests in tests/ pass (each test file runs on its own, so pytest isn't needed)
- `claude plugin validate` passes (if the bundled Claude Code is found)

Usage: python tools/check.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_shared  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CLAUDE_EXE = sorted(Path.home().glob("AppData/Roaming/Claude/claude-code/*/claude.exe"))

problems = []


def frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fields = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def check_copies():
    for path, text in sync_shared.expected_copies():
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            problems.append(f"{path.relative_to(ROOT)} doesn't match shared/ (run tools/sync_shared.py)")


def check_skills():
    for skill_md in sorted((PLUGIN / "skills").glob("*/SKILL.md")):
        folder = skill_md.parent.name
        fields = frontmatter(skill_md.read_text(encoding="utf-8"))
        where = skill_md.relative_to(ROOT)
        if fields is None:
            problems.append(f"{where}: no frontmatter")
            continue
        extra = set(fields) - ALLOWED_KEYS
        if extra:
            problems.append(f"{where}: keys claude.ai refuses: {sorted(extra)}")
        name = fields.get("name", "")
        if name != folder:
            problems.append(f"{where}: name '{name}' doesn't match its folder '{folder}'")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or "claude" in name or "anthropic" in name:
            problems.append(f"{where}: name '{name}' breaks claude.ai's naming rules")
        description = fields.get("description", "")
        if not description:
            problems.append(f"{where}: no description")
        if len(description) > 200:
            problems.append(f"{where}: description is {len(description)} characters (200 max)")
        if re.search(r"<[^>]+>", description):
            problems.append(f"{where}: description has a tag in it")
        if ": " in description or description.startswith(("'", '"', "[", "{", "&", "*", "!", "|", ">", "%", "@")):
            problems.append(f"{where}: description isn't safe for strict YAML (no ': ' inside, no special first character)")


def check_plugin_json():
    path = PLUGIN / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        problems.append(f"plugin.json can't be read: {err}")
        return
    description = data.get("description", "")
    if len(description) > 200:
        problems.append(f"plugin.json description is {len(description)} characters (200 max)")
    if re.search(r"https?://|www\.", description):
        problems.append("plugin.json description has a web address (claude.ai refuses it)")
    if (PLUGIN / "bin").exists():
        problems.append("plugin/bin exists (claude.ai refuses plugins with a bin folder)")


def check_links():
    pages = [p for p in ROOT.glob("*.md")]
    for folder in ("plugin", "shared", "docs", "guardrails", "evals"):
        pages += list((ROOT / folder).rglob("*.md"))
    for page in pages:
        for target in LINK.findall(page.read_text(encoding="utf-8")):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            path = target.split("#")[0]
            if path and not (page.parent / path).exists():
                problems.append(f"{page.relative_to(ROOT)}: broken link to {target}")


def run_tests():
    for test_file in sorted((ROOT / "tests").glob("test_*.py")):
        result = subprocess.run([sys.executable, str(test_file)],
                                capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
        summary = result.stdout.strip().splitlines()
        print(f"  {test_file.name}: {summary[-1] if summary else 'no output'}")
        if result.returncode != 0:
            problems.append(f"{test_file.name} failed:\n" + (result.stdout + result.stderr)[-2000:])


def validate_plugin():
    if not CLAUDE_EXE:
        print("  (Claude Code wasn't found, so `plugin validate` was skipped)")
        return
    for target in (PLUGIN, ROOT):
        result = subprocess.run([str(CLAUDE_EXE[-1]), "plugin", "validate", str(target)],
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0:
            problems.append(f"plugin validate {target.name}:\n{result.stdout}{result.stderr}")


if __name__ == "__main__":
    check_copies()
    check_skills()
    check_plugin_json()
    check_links()
    run_tests()
    validate_plugin()
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print("All checks passed.")
