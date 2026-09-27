"""Tests for the plugin's two scripts and for finding the binder.

Every test uses a throwaway binder in a temp folder, never the real one. The HEIC conversion
tests that need real iPhone photos are skipped when pillow-heif isn't installed.

Run: python -m pytest -q tests      or, without pytest:  python tests/test_scripts.py
"""
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
HEIC_SCRIPT = PLUGIN / "scripts" / "heic_to_jpg.py"
DROP_SCRIPT = PLUGIN / "scripts" / "drop_to_inbox.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PLUGIN / "hooks"))
sys.path.insert(0, str(PLUGIN / "scripts"))
import drop_to_inbox  # noqa: E402
import guard  # noqa: E402
import heic_to_jpg  # noqa: E402

HAS_HEIF = importlib.util.find_spec("pillow_heif") is not None


class Lab:
    """A throwaway home folder with a binder in "My Drive", and a temp folder."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="re-binder-scripts-"))
        self.home = self.dir / "home"
        self.binder = self.home / "My Drive (tester@example.com)" / "R&E Binder"
        self.inbox = self.binder / "Inbox - Drop Here"
        self.inbox.mkdir(parents=True)
        self.temp = self.dir / "temp"
        self.temp.mkdir()
        self.env = dict(os.environ)
        self.env.update({"CLAUDE_PLUGIN_OPTION_BINDER_FOLDER": str(self.binder),
                         "USERPROFILE": str(self.home), "HOME": str(self.home),
                         "CLAUDE_CONFIG_DIR": str(self.home / ".claude"),
                         "TEMP": str(self.temp), "TMP": str(self.temp), "TMPDIR": str(self.temp),
                         "PYTHONDONTWRITEBYTECODE": "1"})

    def run(self, script, *args, env=None):
        done = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True,
                              env=env or self.env, timeout=120)
        return (done.returncode, done.stdout.decode("utf-8", "replace"),
                done.stderr.decode("utf-8", "replace"))

    def snapshot(self):
        """Every file in the binder with its bytes, to prove nothing in it changed."""
        return {p.relative_to(self.binder).as_posix(): p.read_bytes()
                for p in sorted(self.binder.rglob("*")) if p.is_file()}

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def with_lab(test):
    def run():
        lab = Lab()
        try:
            test(lab)
        finally:
            lab.cleanup()
    run.__name__, run.__doc__ = test.__name__, test.__doc__
    return run


def photo_bytes(width=40, height=20, orientation=None, fmt="JPEG"):
    """A small picture, optionally with an EXIF orientation tag (6 = turned sideways)."""
    from PIL import Image
    image = Image.new("RGB", (width, height), (200, 30, 30))
    data = io.BytesIO()
    if orientation:
        exif = Image.Exif()
        exif[0x0112] = orientation
        image.save(data, fmt, exif=exif.tobytes())
    else:
        image.save(data, fmt)
    return data.getvalue()


# ---------------------------------------------------------------- finding the binder

@with_lab
def test_the_binder_folder_setting_wins(lab):
    other = lab.dir / "Somewhere Else" / "R&E Binder"
    other.mkdir(parents=True)
    found, _ = guard.find_binder({"CLAUDE_PLUGIN_OPTION_BINDER_FOLDER": str(other)}, home=lab.home,
                                 settings_file=lab.dir / "none.json", drive_letters=False)
    assert found == other
    missing, why = guard.find_binder({"CLAUDE_PLUGIN_OPTION_BINDER_FOLDER": str(lab.dir / "gone")},
                                     home=lab.home, drive_letters=False)
    assert missing is None and "isn't there" in why


@with_lab
def test_the_scripts_read_the_setting_from_his_claude_settings(lab):
    other = lab.dir / "Elsewhere" / "R&E Binder"
    other.mkdir(parents=True)
    settings = lab.dir / "settings.json"
    settings.write_text(json.dumps({"pluginConfigs": {"re-binder@re-binder": {
        "options": {"binder_folder": str(other)}}}}), encoding="utf-8")
    found, _ = guard.find_binder({}, home=lab.home, settings_file=settings, drive_letters=False)
    assert found == other


@with_lab
def test_the_search_finds_my_drive_and_skips_the_lab_copy(lab):
    (lab.binder.parent / "R&E Binder (lab Sep 24)").mkdir()
    found, _ = guard.find_binder({}, home=lab.home, settings_file=lab.dir / "none.json",
                                 drive_letters=False)
    assert found == lab.binder


@with_lab
def test_the_search_never_guesses_between_two_binders(lab):
    (lab.home / "My Drive (second@example.com)" / "R&E Binder").mkdir(parents=True)
    found, why = guard.find_binder({}, home=lab.home, settings_file=lab.dir / "none.json",
                                   drive_letters=False)
    assert found is None and "More than one" in why


@with_lab
def test_the_search_says_so_when_there_is_no_binder(lab):
    shutil.rmtree(lab.binder)
    found, why = guard.find_binder({}, home=lab.home, settings_file=lab.dir / "none.json",
                                   drive_letters=False)
    assert found is None and "No \"R&E Binder\" folder" in why


# ---------------------------------------------------------------- drop_to_inbox.py

@with_lab
def test_drop_copies_into_the_inbox_and_never_overwrites(lab):
    paper = lab.dir / "Downloads" / "Receipt & Co (Sep).pdf"
    paper.parent.mkdir()
    paper.write_bytes(b"%PDF-1.4 receipt")
    made = []
    for _ in range(3):
        code, out, err = lab.run(DROP_SCRIPT, paper)
        assert code == 0, err
        made.append(Path(out.splitlines()[0]))
    assert [p.name for p in made] == ["Receipt & Co (Sep).pdf", "Receipt & Co (Sep) (2).pdf",
                                      "Receipt & Co (Sep) (3).pdf"]
    assert all(p.parent == lab.inbox and p.read_bytes() == b"%PDF-1.4 receipt" for p in made)
    assert paper.read_bytes() == b"%PDF-1.4 receipt", "the paper he dropped must not change"


@with_lab
def test_drop_refuses_what_isnt_a_new_paper(lab):
    inside = lab.inbox / "already.pdf"
    inside.write_bytes(b"%PDF")
    program = lab.dir / "setup.exe"
    program.write_bytes(b"MZ")
    before = lab.snapshot()
    for path, words in ((lab.dir / "missing.pdf", "wasn't found"), (lab.dir, "wasn't found"),
                        (inside, "already in the binder"), (program, "doesn't look like a paper")):
        code, out, err = lab.run(DROP_SCRIPT, path)
        assert code == 1 and words in err, (path, out, err)
    assert lab.snapshot() == before
    shutil.rmtree(lab.inbox)
    paper = lab.dir / "r.pdf"
    paper.write_bytes(b"%PDF")
    code, _, err = lab.run(DROP_SCRIPT, paper)
    assert code == 1 and "set up my binder" in err


# ---------------------------------------------------------------- heic_to_jpg.py

@with_lab
def test_heic_finds_iphone_photos_in_any_letter_case(lab):
    for name in ("A.HEIC", "b.heic", "c.Heif", "d.HEIF", "e.jpg", "f.pdf"):
        (lab.inbox / name).write_bytes(b"x")
    (lab.inbox / "sub").mkdir()
    (lab.inbox / "sub" / "g.heic").write_bytes(b"x")
    assert [p.name for p in heic_to_jpg.iphone_photos(lab.inbox)] == ["A.HEIC", "b.heic", "c.Heif", "d.HEIF"]


@with_lab
def test_heic_copy_is_upright_outside_the_binder_and_made_once(lab):
    # Pillow reads a file by its contents, so a JPEG saved under a .HEIC name stands in for an
    # iPhone photo here. That tests everything but the HEIC decoding itself.
    photo = lab.inbox / "IMG_5684.HEIC"
    photo.write_bytes(photo_bytes(40, 20, orientation=6))
    before = lab.snapshot()
    out_dir = heic_to_jpg.out_folder(lab.binder, temp_root=lab.temp)
    jpg, made = heic_to_jpg.convert_one(photo, out_dir)
    assert made and jpg.parent == out_dir and not guard.is_inside(jpg, lab.binder)
    assert jpg.name.startswith("IMG_5684.HEIC - ") and jpg.suffix == ".jpg"
    from PIL import Image
    with Image.open(jpg) as image:
        assert image.size == (20, 40), "turned upright from the EXIF orientation"
    again, made_again = heic_to_jpg.convert_one(photo, out_dir)
    assert again == jpg and not made_again
    assert sorted(p.name for p in out_dir.iterdir()) == [jpg.name]
    assert lab.snapshot() == before, "the binder must not change"


@with_lab
def test_heic_never_overwrites_a_file(lab):
    photo = lab.inbox / "IMG_1.heic"
    photo.write_bytes(photo_bytes())
    out_dir = heic_to_jpg.out_folder(lab.binder, temp_root=lab.temp)
    taken = out_dir / f"IMG_1.heic - {heic_to_jpg.fingerprint(photo)}.jpg"
    taken.write_bytes(b"already here")
    jpg, made = heic_to_jpg.convert_one(photo, out_dir)
    assert jpg == taken and not made and taken.read_bytes() == b"already here"


@with_lab
def test_heic_refuses_a_temp_folder_inside_the_binder(lab):
    try:
        heic_to_jpg.out_folder(lab.binder, temp_root=lab.binder)
    except heic_to_jpg.PhotoError:
        return
    raise AssertionError("a temp folder inside the binder must be refused")


@with_lab
def test_heic_script_with_no_iphone_photos(lab):
    (lab.inbox / "receipt.jpg").write_bytes(photo_bytes())
    code, out, err = lab.run(HEIC_SCRIPT)
    assert code == 0 and "No iPhone photos" in out, err


@with_lab
def test_heic_script_says_how_to_install_pillow_heif(lab):
    if HAS_HEIF:
        raise unittest.SkipTest("pillow-heif is installed here")
    (lab.inbox / "IMG_5684.HEIC").write_bytes(photo_bytes())
    before = lab.snapshot()
    code, out, err = lab.run(HEIC_SCRIPT)
    assert code == 3 and "-m pip install pillow-heif" in err and "Ask him first" in err, (out, err)
    assert lab.snapshot() == before


@with_lab
def test_heic_script_finds_no_binder(lab):
    env = dict(lab.env, CLAUDE_PLUGIN_OPTION_BINDER_FOLDER=str(lab.dir / "gone"))
    code, _, err = lab.run(HEIC_SCRIPT, env=env)
    assert code == 1 and "isn't there" in err


@with_lab
def test_heic_script_converts_real_iphone_photos(lab):
    if not HAS_HEIF:
        raise unittest.SkipTest("pillow-heif isn't installed, so real HEIC photos can't be made")
    import pillow_heif
    from PIL import Image
    pillow_heif.register_heif_opener()
    Image.new("RGB", (64, 32), (10, 120, 200)).save(lab.inbox / "IMG_0001.HEIC", format="HEIF")
    Image.new("RGB", (32, 64), (10, 120, 200)).save(lab.inbox / "img_0002.heif", format="HEIF")
    before = lab.snapshot()
    code, out, err = lab.run(HEIC_SCRIPT)
    assert code == 0, err
    paths = [Path(line) for line in out.splitlines() if line.endswith(".jpg")]
    assert len(paths) == 2 and all(p.is_file() and not guard.is_inside(p, lab.binder) for p in paths)
    code, out_again, _ = lab.run(HEIC_SCRIPT)
    assert code == 0 and out_again == out, "a second run gives the same copies"
    assert lab.snapshot() == before


def run_all():
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    passed = skipped = 0
    failed = []
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"ok    {name}")
        except unittest.SkipTest as why:
            skipped += 1
            print(f"skip  {name}: {why}")
        except Exception as err:  # noqa: BLE001 - report every failure, keep going
            failed.append(name)
            print(f"FAIL  {name}: {type(err).__name__}: {err}")
    print(f"\n{passed} passed, {skipped} skipped, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run_all())
