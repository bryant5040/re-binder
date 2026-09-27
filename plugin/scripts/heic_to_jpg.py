#!/usr/bin/env python3
"""Make the iPhone photos in the binder's Inbox readable, without touching the binder.

Google's Drive connector can't read iPhone photos (HEIC or HEIF). In the Code tab, this script
makes an upright JPG copy of each one in a temp folder outside the binder, for example
%TEMP%\\re-binder\\iphone-photos, and prints each JPG's path so Claude can read it.

- The photo in the Inbox is never changed. The original is what gets filed.
- It finds the binder itself (the plugin's binder folder setting, or Google Drive on this PC),
  so the binder's path is never typed into a command.
- Running it twice is safe: a photo that's already done is skipped, and nothing is overwritten.
- It needs the pillow-heif add-on. If that's missing, it prints the line that installs it.

Usage: python heic_to_jpg.py
Exit codes: 0 done, 1 a problem (the message says what), 3 pillow-heif is missing.
"""
from __future__ import annotations

import hashlib
import io
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from guard import INBOX_NAME, find_binder, is_inside  # noqa: E402

PHOTO_TYPES = (".heic", ".heif")
MISSING_ADDON = (
    "iPhone photos need an add-on called pillow-heif, and it isn't installed on this PC.\n"
    "Ask him first. Then install it with this line:\n"
    "\"{python}\" -m pip install pillow-heif")
MISSING_PILLOW = (
    "Reading photos needs Pillow and pillow-heif, and they aren't installed on this PC.\n"
    "Ask him first. Then install them with this line:\n"
    "\"{python}\" -m pip install pillow pillow-heif")


class PhotoError(Exception):
    """A problem to tell Claude in plain words."""


def iphone_photos(inbox: Path) -> list:
    """Every HEIC or HEIF photo at the top of the Inbox, any letter case."""
    return sorted((p for p in inbox.iterdir() if p.is_file() and p.suffix.lower() in PHOTO_TYPES),
                  key=lambda p: p.name.lower())


def out_folder(binder: Path, temp_root=None) -> Path:
    """The folder for the JPG copies. It's never inside the binder."""
    folder = Path(temp_root or tempfile.gettempdir()) / "re-binder" / "iphone-photos"
    if is_inside(folder, binder):
        raise PhotoError("The temp folder is inside the binder, so no copies were made.")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def fingerprint(path: Path) -> str:
    """Short code from the photo's contents, so a new photo with an old name gets a new copy."""
    digest = hashlib.sha256()
    with open(path, "rb") as photo:
        for chunk in iter(lambda: photo.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()[:8]


def convert_one(source: Path, out_dir: Path):
    """Make an upright JPG of one photo. Returns (the JPG's path, True if it was made just now).
    Only reads the photo. Never overwrites a file."""
    from PIL import Image, ImageOps

    target = out_dir / f"{source.name} - {fingerprint(source)}.jpg"
    if target.exists():
        return target, False
    with Image.open(source) as image:
        upright = ImageOps.exif_transpose(image)
        if upright.mode != "RGB":
            upright = upright.convert("RGB")
        data = io.BytesIO()
        upright.save(data, "JPEG", quality=90)
    part = out_dir / f".{target.name}.{os.getpid()}.part"
    with open(part, "xb") as handle:
        handle.write(data.getvalue())
    try:
        if os.name == "nt":
            os.rename(part, target)  # fails if the target exists, so nothing is overwritten
        else:
            os.link(part, target)
            part.unlink()
    except FileExistsError:
        part.unlink()  # our own half-step file in the temp folder
        return target, False
    return target, True


def main(argv=None) -> int:
    binder, note = find_binder()
    if binder is None:
        print(note, file=sys.stderr)
        return 1
    inbox = binder / INBOX_NAME
    if not inbox.is_dir():
        print(f"The binder has no \"{INBOX_NAME}\" folder. Say \"set up my binder\" first.",
              file=sys.stderr)
        return 1
    photos = iphone_photos(inbox)
    if not photos:
        print("No iPhone photos in the Inbox.")
        return 0
    try:
        import PIL  # noqa: F401
    except ImportError:
        print(MISSING_PILLOW.format(python=sys.executable), file=sys.stderr)
        return 3
    try:
        import pillow_heif
    except ImportError:
        print(MISSING_ADDON.format(python=sys.executable), file=sys.stderr)
        return 3
    pillow_heif.register_heif_opener()
    try:
        out_dir = out_folder(binder)
    except PhotoError as err:
        print(err, file=sys.stderr)
        return 1
    ready, problems = [], []
    for photo in photos:
        try:
            ready.append(convert_one(photo, out_dir)[0])
        except Exception as err:
            problems.append(f"Couldn't read {photo.name}: {err}")
    if ready:
        print(f"{len(ready)} iPhone photo(s) ready to read. The photos in the Inbox weren't changed:")
        for jpg in ready:
            print(jpg)
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
