#!/usr/bin/env python3
"""Put one paper into the binder's Inbox, from the Code tab.

When he drops a paper into the chat, Claude runs this with that file's path. It copies the file
into "Inbox - Drop Here" in the binder on this PC, and Google Drive for desktop uploads it.
Then it gets filed like any other paper, after his Allow.

- It never overwrites: if the name is taken, it adds " (2)", " (3)" and so on.
- The file he dropped isn't changed.
- It finds the binder itself (the plugin's binder folder setting, or Google Drive on this PC),
  so the binder's path is never typed into a command.
- It prints the new file's path.

Usage: python drop_to_inbox.py "<path of the paper>"
Exit codes: 0 done, 1 a problem (the message says what).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from guard import INBOX_NAME, find_binder, is_inside  # noqa: E402

PAPER_TYPES = {".pdf", ".jpg", ".jpeg", ".png", ".heic", ".heif", ".gif", ".webp", ".tif",
               ".tiff", ".bmp", ".doc", ".docx", ".xls", ".xlsx"}


class DropError(Exception):
    """A problem to tell Claude in plain words."""


def drop(source, binder: Path) -> Path:
    """Copy one paper into the binder's Inbox. Returns the new file's path."""
    source = Path(source)
    if not source.is_file():
        raise DropError(f"That file wasn't found: {source}")
    if is_inside(source, binder):
        raise DropError("That file is already in the binder, so it wasn't copied.")
    if source.suffix.lower() not in PAPER_TYPES:
        raise DropError(f"\"{source.name}\" doesn't look like a paper (a PDF, a photo or an "
                        "Office file), so it wasn't put in the Inbox.")
    inbox = binder / INBOX_NAME
    if not inbox.is_dir():
        raise DropError(f"The binder has no \"{INBOX_NAME}\" folder. Say \"set up my binder\" first.")
    for number in range(1, 1000):
        name = source.name if number == 1 else f"{source.stem} ({number}){source.suffix}"
        target = inbox / name
        try:
            handle = open(target, "xb")  # "x" never replaces a file that's already there
        except FileExistsError:
            continue
        try:
            with handle, open(source, "rb") as original:
                shutil.copyfileobj(original, handle)
        except BaseException:
            try:
                target.unlink()  # only our own half-made copy, never one of his papers
            except OSError:
                pass
            raise
        try:
            shutil.copystat(source, target)
        except OSError:
            pass
        return target
    raise DropError("The Inbox already has too many papers with that name.")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("Give one file: python drop_to_inbox.py \"<path of the paper>\"", file=sys.stderr)
        return 1
    binder, note = find_binder()
    if binder is None:
        print(note, file=sys.stderr)
        return 1
    try:
        target = drop(argv[0], binder)
    except (DropError, OSError) as err:
        print(err, file=sys.stderr)
        return 1
    print(target)
    print("It will show up in the Inbox in Google Drive in a few seconds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
