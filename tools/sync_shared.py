"""Copy the shared pieces (rules, folder map, naming, the Allow list, tracker, checklist, Drive basics)
from shared/ into every skill's references/ folder.

A regular Claude chat can only see files inside a skill, so each skill carries its own copy. The one
source stays in shared/: edit there, then run this. tools/check.py fails if a copy has drifted.

Usage: python tools/sync_shared.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"
SKILLS = ROOT / "plugin" / "skills"


def header(name):
    return f"<!-- Made from shared/{name}. Edit shared/{name}, then run: python tools/sync_shared.py -->\n\n"


def expected_copies():
    """Yield (copy path, expected text) for every shared file in every skill."""
    for skill in sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").exists()):
        for src in sorted(SHARED.glob("*.md")):
            yield skill / "references" / src.name, header(src.name) + src.read_text(encoding="utf-8")


def main():
    changed = 0
    for path, text in expected_copies():
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
            changed += 1
            print(f"updated {path.relative_to(ROOT)}")
    print(f"{changed} copies updated")


if __name__ == "__main__":
    main()
