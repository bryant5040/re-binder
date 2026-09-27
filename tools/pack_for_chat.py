"""Pack the plugin for claude.ai.

- dist/claude-ai/re-binder-plugin.zip: the whole plugin/ folder, for Customize > Plugins > upload
  (Pro or Max). The normal route is "Add from GitHub" on the public repo; this zip is for testing.
- dist/claude-ai/skills/<skill>.zip: one zip per skill, for Customize > Skills > Upload skill (works on
  the Free plan too). Each skill carries its own copy of shared/, so nothing needs rewriting.

Run tools/check.py first. Usage: python tools/pack_for_chat.py
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
OUT = ROOT / "dist" / "claude-ai"


def add_tree(z, folder, prefix):
    for f in sorted(folder.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts:
            z.write(f, f"{prefix}{f.relative_to(folder).as_posix()}")


def main():
    (OUT / "skills").mkdir(parents=True, exist_ok=True)
    plugin_zip = OUT / "re-binder-plugin.zip"
    with zipfile.ZipFile(plugin_zip, "w", zipfile.ZIP_DEFLATED) as z:
        add_tree(z, PLUGIN, "")
    print(plugin_zip.relative_to(ROOT))
    for skill in sorted(p for p in (PLUGIN / "skills").iterdir() if (p / "SKILL.md").exists()):
        skill_zip = OUT / "skills" / f"{skill.name}.zip"
        with zipfile.ZipFile(skill_zip, "w", zipfile.ZIP_DEFLATED) as z:
            add_tree(z, skill, f"{skill.name}/")
        print(skill_zip.relative_to(ROOT))


if __name__ == "__main__":
    main()
