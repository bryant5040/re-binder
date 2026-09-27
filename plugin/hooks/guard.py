#!/usr/bin/env python3
"""The binder lock for the Code tab.

Claude Code runs this file at the hook events listed in hooks.json. In plain words:

- A move or rename in Google Drive passes only after his Allow, and only as many as he allowed.
  His tap on "Move these N? Allow" (an AskUserQuestion button) gives an Allow for N moves,
  good for 15 minutes. Asking a new "Move these N?" question cancels the old Allow.
  The one exception is retiring the old Job Tracker: only a Sheet the lock has seen in Drive
  named exactly "Job Tracker", into an "Old Trackers" folder it has seen, once.
- New files are only folders, and Claude's own Docs and Sheets made from plain text (Read Me
  First, Job Overview, notes, the Job Tracker, Filing Records). Never an upload or a paper.
- Trash, share and copy never pass. Helpers (subagents) can't change anything in Google Drive.
- Claude's own file and shell tools can't write into the binder's folder on this PC. The one
  exception is running the plugin's two scripts. Reading is always fine.
- Every Google Drive action is written to a log, one line each.

Exit code 2 means "blocked", with a plain reason. Exit code 0 means "no objection".
hooks.json starts this file in a way that turns a missing Python, or a crash here, into a block.

Usage (from hooks.json): guard.py pre | post | start
  pre    PreToolUse: decide whether the tool call may run
  post   PostToolUse and PostToolUseFailure: read his answer, confirm moves, write the log
  start  SessionStart: print one health line

The scripts in ../scripts import find_binder() from here, so the binder is found one way only.
"""
from __future__ import annotations

import json
import os
import posixpath
import re
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

ALLOW_SECONDS = 15 * 60
LOCK_WAIT_SECONDS = 5.0
STALE_LOCK_SECONDS = 30.0

BINDER_NAME = "R&E Binder"
INBOX_NAME = "Inbox - Drop Here"
OWN_SCRIPTS = ("heic_to_jpg.py", "drop_to_inbox.py")
TOKEN_FILE = "allow-tokens.json"
LOG_FILE = "action-log.jsonl"
BINDER_CACHE = "binder-path.txt"
OWN_FILES = "own-files.json"  # which file is the Job Tracker, which folders are Old Trackers

# Google's Drive connector. Its server id differs per person, so any id matches.
DRIVE_TOOL = re.compile(
    r"^mcp__.+__(?P<name>update_file|copy_file|trash_file|share_file|create_file|search_files|"
    r"read_file_content|download_file_content|get_file_metadata|get_file_permissions|"
    r"list_recent_files)$")
DRIVE_WRITES = ("update_file", "copy_file", "trash_file", "share_file", "create_file")
# Drive answers the lock learns the Job Tracker and Old Trackers from.
LEARN_FROM = ("search_files", "get_file_metadata", "list_recent_files", "create_file", "update_file")
FOLDER_TYPE = "application/vnd.google-apps.folder"
SHEET_TYPE = "application/vnd.google-apps.spreadsheet"
GOOGLE_TYPES = ("", "application/vnd.google-apps.document", SHEET_TYPE)
# Besides folders, Claude only makes these, from plain text.
OWN_FILE_TITLE = re.compile(r"^(?:Read Me First|Job Overview|Job Tracker|\d{4}-\d{2}-\d{2} Note - [^\n]{1,80}"
                            r"|Filing Record \d{4}-\d{2}-\d{2} \d{1,4})$")
# "Move these 7?", "Move these 4 back?", "Move this 1?", or a one-item question such as
# "Move Henderson to Finished Jobs?", which counts as 1 move.
MOVE_QUESTION = re.compile(r"\bmove\s+(?:(?:these|this)\s+(\d{1,4})\b)?[^?\n]{0,80}\?", re.IGNORECASE)
TRACKER_TITLE = re.compile(r"^Job Tracker \d{4}-\d{2}-\d{2} \d{4}$")
FILE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
SHELL_TOOLS = ("Bash", "PowerShell", "Monitor")

MESSAGES = {
    "trash": "Blocked by the binder lock: nothing in the binder is ever deleted or put in the "
             "trash (rule 3). To take a paper out, move it to Archived after his Allow. "
             "Nothing was changed.",
    "share": "Blocked by the binder lock: files in the binder are never shared (rule 5). "
             "Nothing was changed.",
    "copy": "Blocked by the binder lock: copying files in Google Drive is never needed. Move the "
            "paper instead, after his Allow. Nothing was changed.",
    "helper": "Blocked by the binder lock: helpers only read. Only the main assistant changes "
              "the binder, and only after his Allow. Nothing was changed.",
    "not-tracker": "Blocked by the binder lock: without his Allow, only the binder's current Job "
                   "Tracker can get a dated name, in one call that also puts it in Archived › Old "
                   "Trackers. The lock hasn't seen this file as the Job Tracker, or that folder as "
                   "Old Trackers. Look both up with search_files, then try again. For any other "
                   "file, show him the list and ask. Nothing was moved.",
    "new-file": "Blocked by the binder lock: Claude only makes folders and its own files (Read Me "
                "First, Job Overview, dated notes, the Job Tracker and Filing Records), each from "
                "plain text: textContent, with contentMimeType text/plain for a Doc or text/csv for "
                "a Sheet. It never uploads, copies or re-makes a paper (rule 4). Nothing was made.",
    "no-allow": "Blocked by the binder lock: he hasn't tapped Allow for this move. Show him the "
                "whole list, then ask with AskUserQuestion: \"Move these N? Allow / Change "
                "something / Deny\". Move only after he taps Allow. Nothing was moved.",
    "expired": "Blocked by the binder lock: his Allow was more than 15 minutes ago, so it ran "
               "out. Show him the list again and ask again. Nothing was moved.",
    "used-up": "Blocked by the binder lock: his Allow covered {n}, and they're all used. For "
               "anything else, show him the list and ask again. Nothing was moved.",
    "cant-ask": "Blocked by the binder lock: it couldn't read his answer, and in this permission "
                "mode it can't ask him again. Switch to the normal mode, show him the list and "
                "ask again. Nothing was moved.",
    "busy": "Blocked by the binder lock: it was busy for a moment. Try again. Nothing was moved.",
    "local-write": "Blocked by the binder lock: Claude never writes, moves or deletes files in "
                   "the binder's folder on this PC (rules 2 and 4). Papers are moved and renamed "
                   "only with Google Drive, after his Allow. Reading them is fine. Nothing was "
                   "changed.",
    "state": "Blocked by the binder lock: that's the lock's own record, and Claude can't change "
             "it. Nothing was changed.",
    "prefilled": "Blocked by the binder lock: only he can answer \"Move these N?\". Ask the "
                 "question with no answers filled in.",
    "unreadable": "Blocked by the binder lock: it couldn't read this request, so it stopped it "
                  "to be safe. Nothing was changed.",
    "crash": "Blocked by the binder lock: it hit a problem and stopped this to be safe. Nothing "
             "was changed.",
}


class LockBusy(Exception):
    """Another hook held the lock's record for too long."""


# ---------------------------------------------------------------- paths and finding the binder

def norm_path(path) -> str:
    """One spelling for comparing paths: forward slashes, lower case, C:/ not /c/."""
    text = str(path).strip().strip("\"'").replace("\\", "/")
    match = re.match(r"^/(?:mnt/)?([a-zA-Z])(/.*)?$", text)
    if match:
        text = match.group(1) + ":" + (match.group(2) or "/")
    text = re.sub(r"/{2,}", "/", text)
    if text:
        text = posixpath.normpath(text)
    return text.lower()


def is_inside(child, parent) -> bool:
    """True if child is parent, or somewhere inside it."""
    kid = norm_path(os.path.abspath(str(child)))
    top = norm_path(os.path.abspath(str(parent))).rstrip("/")
    return kid == top or kid.startswith(top + "/")


def configured_binder(env=None, settings_file=None) -> str:
    """The binder folder he set in the plugin's options, or "".

    Hooks get it as CLAUDE_PLUGIN_OPTION_BINDER_FOLDER. Commands Claude runs don't, so the
    scripts read it from his Claude settings instead (pluginConfigs)."""
    env = os.environ if env is None else env
    value = str(env.get("CLAUDE_PLUGIN_OPTION_BINDER_FOLDER") or "").strip()
    if value:
        return value
    if settings_file is None:
        config_dir = str(env.get("CLAUDE_CONFIG_DIR") or "").strip()
        settings_file = Path(config_dir) if config_dir else Path.home() / ".claude"
        settings_file = settings_file / "settings.json"
    try:
        data = json.loads(Path(settings_file).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    configs = data.get("pluginConfigs") if isinstance(data, dict) else None
    if not isinstance(configs, dict):
        return ""
    for key, entry in configs.items():
        if str(key).split("@")[0] != "re-binder" or not isinstance(entry, dict):
            continue
        options = entry.get("options")
        value = options.get("binder_folder") if isinstance(options, dict) else None
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def local_drive_letters() -> list:
    """Windows drive letters worth checking for Google Drive. Network drives are skipped,
    because checking a disconnected one can hang."""
    if os.name != "nt":
        return []
    try:
        import ctypes
        import string
        kernel = ctypes.windll.kernel32
        mask = kernel.GetLogicalDrives()
        letters = []
        for index, letter in enumerate(string.ascii_uppercase):
            if letter in "AB" or not mask & (1 << index):
                continue
            if kernel.GetDriveTypeW(f"{letter}:\\") in (2, 3):  # removable or fixed
                letters.append(letter)
        return letters
    except Exception:
        return ["G"]


def drive_folders(home=None, drive_letters=True) -> list:
    """Where Google Drive for desktop keeps "My Drive" on this PC, in two tiers: folders in his
    home folder first, then drive letters such as G:."""
    home = Path(home) if home else Path.home()
    first = []
    for pattern in ("My Drive*", "Library/CloudStorage/GoogleDrive-*/My Drive"):
        try:
            first += sorted(p for p in home.glob(pattern) if p.is_dir())
        except OSError:
            pass
    first += [home / "Google Drive" / "My Drive", home / "Google Drive"]
    second = [Path(f"{letter}:/My Drive") for letter in local_drive_letters()] if drive_letters else []
    return [first, second]


def find_binder(env=None, home=None, settings_file=None, drive_letters=True):
    """Find his binder folder on this PC. Returns (path, note) or (None, a plain reason).

    Order: the plugin's binder folder setting; then a folder named exactly "R&E Binder" in
    Google Drive for desktop. "R&E Binder (lab Sep 24)" is not his binder. Two binders at the
    same level means no guess."""
    env = os.environ if env is None else env
    value = configured_binder(env, settings_file)
    if value:
        path = Path(value).expanduser()
        if path.is_dir():
            return path, "set in the plugin's settings"
        return None, f"The binder folder in the plugin's settings isn't there: {value}"
    for tier in drive_folders(home, drive_letters):
        found, seen = [], set()
        for base in tier:
            candidate = base / BINDER_NAME
            try:
                if not candidate.is_dir():
                    continue
            except OSError:
                continue
            key = norm_path(candidate)
            if key not in seen:
                seen.add(key)
                found.append(candidate)
        if len(found) == 1:
            return found[0], "found in Google Drive on this PC"
        if len(found) > 1:
            listed = "; ".join(str(p) for p in found)
            return None, (f"More than one \"{BINDER_NAME}\" folder is on this PC ({listed}). "
                          "Set the right one as the plugin's binder folder.")
    return None, f"No \"{BINDER_NAME}\" folder was found in Google Drive on this PC."


# ---------------------------------------------------------------- the lock's own record

def state_dirs(env) -> list:
    """Where the lock keeps his Allow and the log: the plugin's data folder, or a temp folder."""
    folders = []
    data = str(env.get("CLAUDE_PLUGIN_DATA") or "").strip()
    if data:
        folders.append(Path(data))
    folders.append(Path(tempfile.gettempdir()) / "re-binder" / "lock")
    return folders


def ensure_state(env) -> Path:
    folder = state_dirs(env)[0]
    folder.mkdir(parents=True, exist_ok=True)
    return folder


class StateLock:
    """Only one hook at a time reads or changes the record."""

    def __init__(self, folder: Path):
        self.path = folder / ".lock"
        self.handle = None

    def __enter__(self):
        deadline = time.monotonic() + LOCK_WAIT_SECONDS
        while True:
            try:
                self.handle = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.handle, str(os.getpid()).encode("ascii"))
                return self
            except (FileExistsError, PermissionError):
                try:
                    if time.time() - self.path.stat().st_mtime > STALE_LOCK_SECONDS:
                        self.path.unlink()
                        continue
                except OSError:
                    pass
            if time.monotonic() > deadline:
                raise LockBusy()
            time.sleep(0.03)

    def __exit__(self, *exc):
        try:
            os.close(self.handle)
        finally:
            try:
                self.path.unlink()
            except OSError:
                pass


def load_tokens(folder: Path) -> dict:
    try:
        data = json.loads((folder / TOKEN_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def number_or_zero(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def save_tokens(folder: Path, tokens: dict) -> None:
    now = time.time()
    for session in [s for s, t in tokens.items()
                    if not isinstance(t, dict) or number_or_zero(t.get("expires")) < now - 3600]:
        del tokens[session]
    temp = folder / f"{TOKEN_FILE}.{os.getpid()}.tmp"
    temp.write_text(json.dumps(tokens, indent=1), encoding="utf-8")
    os.replace(temp, folder / TOKEN_FILE)


def set_allow(env, session: str, count: int, question: str, confirmed: bool) -> None:
    folder = ensure_state(env)
    with StateLock(folder):
        tokens = load_tokens(folder)
        now = time.time()
        tokens[session] = {"moves_left": count, "allowed": count, "issued": now,
                           "expires": now + ALLOW_SECONDS, "question": question[:300],
                           "confirmed": confirmed, "pending": []}
        save_tokens(folder, tokens)


def clear_allow(env, session: str) -> None:
    folder = ensure_state(env)
    with StateLock(folder):
        tokens = load_tokens(folder)
        if tokens.pop(session, None) is not None:
            save_tokens(folder, tokens)


def spend_allow(env, session: str, tool_use_id: str, mode: str):
    """Use one move of his Allow. Returns (outcome, number, token).

    ok: allowed, number = moves left. ask: his answer couldn't be read, so Claude Code asks him
    (number = moves in the pile). Otherwise the move is blocked: no-allow, expired, used-up
    (number = moves he allowed) or cant-ask."""
    folder = ensure_state(env)
    with StateLock(folder):
        tokens = load_tokens(folder)
        token = tokens.get(session) if session else None
        if not isinstance(token, dict):
            return "no-allow", 0, None
        try:
            left = int(token.get("moves_left", 0))
            expires = float(token.get("expires", 0))
        except (TypeError, ValueError):
            return "no-allow", 0, None
        if time.time() > expires:
            return "expired", 0, token
        if left <= 0:
            return "used-up", int(token.get("allowed", 0) or 0), token
        if token.get("confirmed") is True:
            token["moves_left"] = left - 1
            save_tokens(folder, tokens)
            return "ok", left - 1, token
        if mode in ("bypassPermissions", "dontAsk"):
            return "cant-ask", left, token
        pending = [p for p in token.get("pending") or [] if isinstance(p, str)]
        pending.append(tool_use_id)
        token["pending"] = pending[-50:]
        save_tokens(folder, tokens)
        return "ask", left, token


def confirm_move(env, session: str, tool_use_id: str) -> None:
    """A move that Claude Code asked him about ran, so he said yes: his Allow now counts."""
    folder = ensure_state(env)
    with StateLock(folder):
        tokens = load_tokens(folder)
        token = tokens.get(session)
        if not isinstance(token, dict) or tool_use_id not in (token.get("pending") or []):
            return
        token["pending"] = [p for p in token["pending"] if p != tool_use_id]
        token["confirmed"] = True
        token["moves_left"] = max(0, int(token.get("moves_left", 0) or 0) - 1)
        save_tokens(folder, tokens)


# ---------------------------------------------------------------- the Job Tracker, learned from Drive

def drive_files(value, depth: int = 0):
    """Every file a connector answer describes (an id and a title), whatever shape it came in."""
    if depth > 8:
        return
    if isinstance(value, str):
        text = value.strip()
        if text[:1] in ("{", "["):
            try:
                value = json.loads(text)
            except ValueError:
                return
            yield from drive_files(value, depth + 1)
        return
    if isinstance(value, dict):
        if isinstance(value.get("id"), str) and isinstance(value.get("title"), str):
            yield value
        for item in value.values():
            yield from drive_files(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            yield from drive_files(item, depth + 1)


def load_own(folder: Path) -> dict:
    try:
        data = json.loads((folder / OWN_FILES).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    data = data if isinstance(data, dict) else {}
    return {key: data[key] if isinstance(data.get(key), dict) else {}
            for key in ("trackers", "old_tracker_folders")}


def save_own(folder: Path, own: dict) -> None:
    temp = folder / f"{OWN_FILES}.{os.getpid()}.tmp"
    temp.write_text(json.dumps(own, indent=1), encoding="utf-8")
    os.replace(temp, folder / OWN_FILES)


def learn(env, response) -> None:
    """Remember each Google Sheet named exactly "Job Tracker" and each "Old Trackers" folder that
    Drive shows Claude. A tracker that shows up under another name is forgotten."""
    seen = [f for f in drive_files(response)]
    if not seen:
        return
    folder = ensure_state(env)
    known = load_own(folder)["trackers"]
    if not any(f["title"].strip() in ("Job Tracker", "Old Trackers") or f["id"] in known for f in seen):
        return
    with StateLock(folder):
        own = load_own(folder)
        before = json.dumps(own, sort_keys=True)
        for f in seen:
            title, kind = f["title"].strip(), str(f.get("mimeType") or "")
            if title == "Job Tracker":
                if kind == SHEET_TYPE:
                    own["trackers"].setdefault(f["id"], time.time())
            else:
                own["trackers"].pop(f["id"], None)
            if title == "Old Trackers" and kind == FOLDER_TYPE:
                own["old_tracker_folders"].setdefault(f["id"], time.time())
        if json.dumps(own, sort_keys=True) != before:
            save_own(folder, own)


def retire_tracker(env, file_id: str, parent_id: str) -> bool:
    """True, once, when the Job Tracker the lock has seen goes into an Old Trackers folder it has
    seen. Anything else that gets a tracker's dated name needs his Allow like any move."""
    if not file_id or not parent_id:
        return False
    folder = ensure_state(env)
    with StateLock(folder):
        own = load_own(folder)
        if file_id not in own["trackers"] or parent_id not in own["old_tracker_folders"]:
            return False
        del own["trackers"][file_id]
        save_own(folder, own)
    return True


def own_new_file(tool_input: dict) -> bool:
    """A folder, or one of Claude's own Docs and Sheets made from plain text. Never an upload."""
    kind = str(tool_input.get("mimeType") or "").strip()
    content_kind = str(tool_input.get("contentMimeType") or "").strip()
    uploads = any(tool_input.get(key) for key in ("base64Content", "content"))
    if FOLDER_TYPE in (kind, content_kind):
        return not uploads and not tool_input.get("textContent")
    title = str(tool_input.get("title") or "").strip()
    return (not uploads and isinstance(tool_input.get("textContent"), str)
            and content_kind in ("text/plain", "text/csv") and kind in GOOGLE_TYPES
            and bool(OWN_FILE_TITLE.match(title)))


def log_event(env, data: dict, **fields) -> None:
    """Add one line to the action log. A problem here never changes a decision."""
    try:
        folder = ensure_state(env)
        tool = str(data.get("tool_name") or "")
        tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
        match = DRIVE_TOOL.match(tool)
        line = {"time": datetime.now().astimezone().isoformat(timespec="seconds"),
                "session": data.get("session_id"),
                "tool": match.group("name") if match else tool,
                "tool_use_id": data.get("tool_use_id")}
        if data.get("agent_id"):
            line["helper"] = data.get("agent_type") or data.get("agent_id")
        for key in ("fileId", "title", "parentId"):
            if isinstance(tool_input.get(key), str):
                line[key] = tool_input[key]
        if tool in FILE_TOOLS:
            line["path"] = tool_input.get("file_path") or tool_input.get("notebook_path")
        if tool in SHELL_TOOLS and isinstance(tool_input.get("command"), str):
            line["command"] = tool_input["command"][:300]
        line.update(fields)
        with StateLock(folder):
            with open(folder / LOG_FILE, "a", encoding="utf-8") as log:
                log.write(json.dumps(line, ensure_ascii=False) + "\n")
    except Exception as err:  # the log must never break a decision
        sys.stderr.write(f"binder lock: couldn't write the log ({err})\n")


# ---------------------------------------------------------------- answers to his questions

def emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=True))
    sys.stdout.flush()


def deny(message: str) -> int:
    emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                 "permissionDecisionReason": message}})
    sys.stderr.write(message + "\n")
    return 2


def decide(decision: str, shown_to_him: str, for_claude: str = "") -> int:
    out = {"hookEventName": "PreToolUse", "permissionDecision": decision,
           "permissionDecisionReason": shown_to_him}
    if for_claude:
        out["additionalContext"] = for_claude
    emit({"hookSpecificOutput": out})
    return 0


def context(event: str, text: str) -> int:
    emit({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}})
    return 0


def blocked(env, data: dict, key: str, **values) -> int:
    message = MESSAGES[key].format(**values) if values else MESSAGES[key]
    log_event(env, data, stage="before", decision="denied", why=key)
    return deny(message)


def moves(n: int) -> str:
    return f"{n} move" if n == 1 else f"{n} moves"


def question_texts(obj) -> list:
    if not isinstance(obj, dict) or not isinstance(obj.get("questions"), list):
        return []
    return [q["question"] for q in obj["questions"]
            if isinstance(q, dict) and isinstance(q.get("question"), str)]


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip().casefold()


def lookup(mapping, question: str):
    if not isinstance(mapping, dict):
        return None
    if question in mapping:
        return mapping[question]
    for key, value in mapping.items():
        if squash(key) == squash(question):
            return value
    return None


def is_allow(answer) -> bool:
    if not isinstance(answer, str):
        return False
    text = re.sub(r"\(recommended\)\s*$", "", answer.strip(), flags=re.IGNORECASE)
    return text.strip().rstrip(".!").strip().casefold() == "allow"


# ---------------------------------------------------------------- shell commands

WRITE_COMMANDS = {
    # Git Bash and Unix tools
    "cp", "mv", "rm", "rmdir", "touch", "tee", "mkdir", "ln", "install", "rsync", "dd",
    "truncate", "shred", "unlink", "chmod", "chown", "chgrp", "chattr", "patch", "unzip", "tar",
    "gzip", "gunzip", "bzip2", "bunzip2", "xz", "unxz", "zip", "7z", "7za", "wget", "split",
    "mkfifo", "mknod", "setfacl",
    # Windows commands
    "copy", "xcopy", "robocopy", "move", "del", "erase", "ren", "rename", "md", "rd", "mklink",
    "attrib", "icacls", "takeown", "cipher", "compact", "expand", "replace", "fsutil",
    # PowerShell commands and their short names
    "set-content", "add-content", "out-file", "new-item", "remove-item", "move-item",
    "copy-item", "rename-item", "clear-content", "clear-item", "set-item", "tee-object",
    "export-csv", "export-clixml", "expand-archive", "compress-archive", "start-bitstransfer",
    "new-itemproperty", "set-itemproperty", "remove-itemproperty", "rename-itemproperty",
    "set-acl", "ni", "ri", "mi", "cpi", "rni", "sc", "ac", "clc", "cli", "si", "epcsv",
}
PREFIX_WORDS = {
    "sudo", "env", "nohup", "time", "command", "exec", "builtin", "nice", "stdbuf", "timeout",
    "xargs", "then", "do", "else", "elif", "if", "while", "until", "!", "call", "start",
    "start-process", "saps", "foreach-object", "%", "where-object", "?", "-exec", "-execdir",
    "-ok", "-okdir",
}
SHELL_WRAPPERS = {"bash", "sh", "zsh", "dash", "ksh", "wsl", "cmd", "powershell", "pwsh",
                  "iex", "invoke-expression"}
POWERSHELL_WORDS = {"powershell", "pwsh", "iex", "invoke-expression"}
FLAG_VALUES = {"bypass", "unrestricted", "remotesigned", "allsigned", "default", "undefined",
               "restricted", "hidden", "normal", "minimized", "maximized", "text", "xml"}
NULL_TARGETS = {"/dev/null", "nul", "$null", "/dev/stdout", "/dev/stderr", "nul:"}
CODE_WRITES = re.compile(
    r"open\s*\((?:[^()]|\([^()]*\))*?,\s*(?:mode\s*=\s*)?[rbuf]*['\"][^'\"]*[wax+][^'\"]*['\"]"
    r"|\.write_(?:text|bytes)\s*\("
    r"|\.(?:unlink|rmdir|mkdir|touch|rename|symlink_to|hardlink_to)\s*\("
    r"|\bos\.(?:remove|unlink|rename|renames|replace|rmdir|removedirs|makedirs|mkdir|link|"
    r"symlink|truncate|chmod|utime|chown)\s*\("
    r"|\bshutil\.(?:copy\w*|move|rmtree|make_archive|unpack_archive|chown)\s*\("
    r"|\.save\s*\("
    r"|\bfs\.(?:write|append|rename|unlink|rm|copy|cp|mkdir|truncate|symlink|link|"
    r"createwritestream)\w*\s*\("
    r"|\[(?:system\.)?io\.(?:file|directory)\]::\s*(?:write|append|delete|move|copy|replace|"
    r"create|open|setattributes|encrypt|decrypt)"
    r"|\.(?:copyto|moveto|delete|createtext|appendtext|openwrite|encrypt|decrypt)\s*\("
    r"|streamwriter|filestream",
    re.IGNORECASE)
MARKER = re.compile("\x00(\\d+)\x00")
BINDER_IN_PATH = re.compile(r"(?:^|/)(?:my drive|google drive)[^/]*/(?:[^/]+/)*r&e binder[^/]*(?:/|$)")
BINDER_IN_TEXT = re.compile(r"(?:my drive|google drive)[^;|<>\n]*?/r(?:&e(?: binder|[*?])|[*?])")


def mask_quotes(command: str, powershell: bool):
    """Hide quoted text and escaped characters behind markers, so their spaces, ; & | and >
    aren't read as shell syntax. Returns (masked text, list of hidden pieces)."""
    out, pieces = [], []
    escape = "`" if powershell else "\\"

    def hide(text):
        pieces.append(text)
        out.append(f"\x00{len(pieces) - 1}\x00")

    i, n = 0, len(command)
    while i < n:
        c = command[i]
        if c == "'":
            j, buf = i + 1, []
            while j < n:
                if command[j] == "'":
                    if powershell and j + 1 < n and command[j + 1] == "'":
                        buf.append("'")
                        j += 2
                        continue
                    break
                buf.append(command[j])
                j += 1
            hide("".join(buf))
            i = j + 1
        elif c == '"':
            j, buf = i + 1, []
            while j < n:
                ch = command[j]
                if powershell and ch == "`" and j + 1 < n:
                    buf.append(command[j + 1])
                    j += 2
                elif not powershell and ch == "\\" and j + 1 < n and command[j + 1] in '"\\$`\n':
                    buf.append(command[j + 1])
                    j += 2
                elif powershell and ch == '"' and j + 1 < n and command[j + 1] == '"':
                    buf.append('"')
                    j += 2
                elif ch == '"':
                    break
                else:
                    buf.append(ch)
                    j += 1
            hide("".join(buf))
            i = j + 1
        elif c == escape and i + 1 < n:
            hide(command[i + 1])
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out), pieces


def unmask(text: str, pieces: list) -> str:
    return MARKER.sub(lambda m: pieces[int(m.group(1))], text)


def flatten(command: str, powershell: bool, home: str) -> str:
    """The command as one plain lower-case string with quotes and escapes gone, forward slashes,
    and C:/ instead of /c/, ready for spotting paths."""
    masked, pieces = mask_quotes(command, powershell)
    text = unmask(masked, pieces).replace("\\", "/").lower()
    text = re.sub(r"/{2,}", "/", text)
    text = re.sub(r"(?:^|(?<=[\s=(<>|;&,]))/(?:mnt/)?([a-z])/", r"\1:/", text)
    for alias in ("~/", "$home/", "${home}/", "$env:userprofile/", "${env:userprofile}/",
                  "%userprofile%/", "$env:home/"):
        text = text.replace(alias, home.rstrip("/") + "/")
    return text


def command_name(word: str) -> str:
    name = re.split(r"[\\/]", word.strip())[-1].lower()
    return re.sub(r"\.(exe|cmd|bat|com)$", "", name)


def first_command(words: list, pieces: list):
    """Skip prefixes like sudo, env, VAR=1 and "$x =", and return (command name, its arguments)."""
    i = 0
    while i < len(words):
        word = unmask(words[i], pieces)
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", word):
            i += 1
            continue
        if word.startswith("$") and (word.endswith("=") or (i + 1 < len(words) and words[i + 1] == "=")):
            i += 1 if word.endswith("=") else 2
            continue
        name = command_name(word)
        if name in PREFIX_WORDS:
            i += 1
            while i < len(words) and unmask(words[i], pieces).startswith("-") and name in (
                    "sudo", "env", "nice", "stdbuf", "timeout", "xargs", "nohup", "command"):
                flag = unmask(words[i], pieces)
                i += 1
                if (name == "xargs" and flag in ("-I", "-n", "-L", "-P", "-d", "-a", "-s", "-E")) or (
                        name == "nice" and flag == "-n"):
                    i += 1
            if name == "timeout" and i < len(words) and re.match(r"^\d", unmask(words[i], pieces)):
                i += 1
            continue
        return name, [unmask(w, pieces) for w in words[i + 1:]]
    return None, []


def is_write_command(name: str, args: list, depth: int) -> bool:
    lowered = [a.lower() for a in args]
    if name in WRITE_COMMANDS:
        return True
    if name in ("sed", "perl"):
        return any(re.match(r"^-[a-z]*i", a) or a.startswith("--in-place") for a in lowered)
    if name in ("curl", "invoke-webrequest", "iwr", "invoke-restmethod", "irm"):
        return any(re.match(r"^-[a-zA-Z]*[oO]", a) or a in ("--output", "--remote-name",
                   "--output-dir", "--remote-name-all") for a in args)
    if name == "find":
        if any(a in ("-delete", "-fprint", "-fprint0", "-fprintf", "-fls") for a in lowered):
            return True
        for index, arg in enumerate(lowered):
            if arg in ("-exec", "-execdir", "-ok", "-okdir") and index + 1 < len(args):
                inner = [a for a in args[index + 1:] if a not in (";", "+", "{}")]
                sub, sub_args = first_command(inner, [])
                if sub and is_write_command(sub, sub_args, depth):
                    return True
        return False
    if name in SHELL_WRAPPERS:
        if name in ("powershell", "pwsh") and any(
                re.match(r"^-e(n(c(odedcommand)?)?|c)?$", a) for a in lowered):
            return True  # a hidden command can't be checked
        inner = [a for a in args if not a.startswith(("-", "/")) and a.lower() not in FLAG_VALUES]
        return looks_like_write(" ".join(inner), name in POWERSHELL_WORDS, depth + 1)
    return False


def redirect_writes(masked: str, pieces: list) -> bool:
    """True if a > or >> sends output into a real file."""
    for match in re.finditer(r"(?:\d+|&|\*)?>>?\|?", masked):
        rest = masked[match.end():]
        if rest.startswith("&"):
            continue  # 2>&1 and >&2 only join streams
        target = re.match(r"\s*(\S+)", rest)
        if not target:
            continue
        if unmask(target.group(1), pieces).strip().lower() in NULL_TARGETS:
            continue
        return True
    return False


def looks_like_write(command: str, powershell: bool, depth: int = 0) -> bool:
    """True if the command looks like it writes, moves or deletes files."""
    if depth > 3:
        return True
    if CODE_WRITES.search(command):
        return True
    masked, pieces = mask_quotes(command, powershell)
    if redirect_writes(masked, pieces):
        return True
    splitter = r"\|\||&&|[;|&\n(){}]|\$\(" if powershell else r"\|\||&&|[;|&\n(){}`]|\$\("
    for segment in re.split(splitter, masked):
        name, args = first_command(segment.split(), pieces)
        if name and is_write_command(name, args, depth):
            return True
    return False


def runs_own_script(command: str, powershell: bool, env) -> bool:
    """True if the command only runs one of the plugin's two scripts with python."""
    root = str(env.get("CLAUDE_PLUGIN_ROOT") or "").strip()
    if not root:
        return False
    masked, pieces = mask_quotes(command, powershell)
    body = masked.strip()
    if powershell:
        body = re.sub(r"^&\s*", "", body)
    if re.search(r"[;&|<>\n`]|\$\(", body):
        return False
    words = [unmask(w, pieces) for w in body.split()]
    if not words or command_name(words[0]) not in ("python", "python3", "py", "pythonw"):
        return False
    i = 1
    while i < len(words) and words[i].startswith("-"):
        if words[i] in ("-c", "-m", "-"):
            return False
        i += 2 if words[i] in ("-X", "-W") else 1
    if i >= len(words):
        return False
    script = norm_path(words[i])
    return any(script == norm_path(f"{root}/scripts/{name}") for name in OWN_SCRIPTS)


# ---------------------------------------------------------------- what's protected

def protected_binders(env) -> list:
    """Binder folders to protect, from his setting and from the last session start.
    Nothing here searches the disk, so a slow Google Drive can't stall a check."""
    found = []
    value = str(env.get("CLAUDE_PLUGIN_OPTION_BINDER_FOLDER") or "").strip()
    if value:
        found.append(value)
    for folder in state_dirs(env)[:1]:
        try:
            cached = (folder / BINDER_CACHE).read_text(encoding="utf-8").strip()
        except OSError:
            cached = ""
        if cached:
            found.append(cached)
    return [norm_path(p) for p in found]


def path_in_binder(path: str, binders: list) -> bool:
    if not path:
        return False
    target = norm_path(path)
    for binder in binders:
        if binder and (target == binder or target.startswith(binder.rstrip("/") + "/")):
            return True
    return bool(BINDER_IN_PATH.search(target))


def path_in_state(path: str, env) -> bool:
    target = norm_path(path)
    return any(target == norm_path(d) or target.startswith(norm_path(d) + "/") for d in state_dirs(env))


def mentions_binder(text: str, binders: list) -> bool:
    return any(b and b in text for b in binders) or bool(BINDER_IN_TEXT.search(text))


def mentions_state(text: str, env) -> bool:
    return (any(norm_path(d) in text for d in state_dirs(env))
            or any(name in text for name in (TOKEN_FILE, LOG_FILE, OWN_FILES)))


# ---------------------------------------------------------------- the three modes

def pre(data: dict, env) -> int:
    tool = str(data.get("tool_name") or "")
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    match = DRIVE_TOOL.match(tool)
    if match:
        if match.group("name") in DRIVE_WRITES:
            return pre_drive(data, env, match.group("name"), tool_input)
        return 0
    if tool == "AskUserQuestion":
        return pre_question(data, env, tool_input)
    if tool in FILE_TOOLS:
        return pre_file(data, env, tool_input)
    if tool in SHELL_TOOLS:
        return pre_shell(data, env, tool, tool_input)
    return 0


def pre_drive(data: dict, env, name: str, tool_input: dict) -> int:
    if data.get("agent_id"):
        return blocked(env, data, "helper")
    if name in ("trash_file", "share_file", "copy_file"):
        return blocked(env, data, name.split("_")[0])
    if name == "create_file":
        if not own_new_file(tool_input):
            return blocked(env, data, "new-file")
        log_event(env, data, stage="before", decision="allowed",
                  why="making folders and Claude's own files needs no tap")
        return 0
    title = tool_input.get("title")
    if isinstance(title, str) and TRACKER_TITLE.match(title.strip()):
        try:
            retired = retire_tracker(env, str(tool_input.get("fileId") or ""),
                                     str(tool_input.get("parentId") or ""))
        except LockBusy:
            return blocked(env, data, "busy")
        if not retired:
            return blocked(env, data, "not-tracker")
        log_event(env, data, stage="before", decision="allowed", why="old Job Tracker")
        return decide("allow", "Retiring the old Job Tracker. It's Claude's own file, so no tap "
                               "is needed.")
    session = str(data.get("session_id") or "")
    try:
        outcome, number, token = spend_allow(env, session, str(data.get("tool_use_id") or ""),
                                             str(data.get("permission_mode") or ""))
    except LockBusy:
        return blocked(env, data, "busy")
    if outcome == "ok":
        until = time.strftime("%H:%M", time.localtime(float(token["expires"])))
        log_event(env, data, stage="before", decision="allowed", why="his Allow", moves_left=number)
        return decide("allow", f"Allowed by your tap. {moves(number)} left.",
                      f"The binder lock allowed this move with his Allow. It covers "
                      f"{moves(number)} more, until {until}.")
    if outcome == "ask":
        log_event(env, data, stage="before", decision="ask",
                  why="his answer couldn't be read, so Claude Code asks him")
        rest = f" It's 1 of {number}. A yes here lets all {number} move." if number > 1 else ""
        return decide("ask", f"Binder lock: move this paper as listed?{rest}")
    if outcome == "used-up":
        return blocked(env, data, "used-up", n=moves(number))
    return blocked(env, data, outcome)


def pre_question(data: dict, env, tool_input: dict) -> int:
    if not any(MOVE_QUESTION.search(q) for q in question_texts(tool_input)):
        return 0
    session = str(data.get("session_id") or "")
    if session:
        try:
            clear_allow(env, session)  # a new "Move these N?" replaces his last Allow
        except LockBusy:
            return blocked(env, data, "busy")
    if tool_input.get("answers"):
        return blocked(env, data, "prefilled")
    return 0


def pre_file(data: dict, env, tool_input: dict) -> int:
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not isinstance(path, str) or not path.strip():
        return 0
    if not os.path.isabs(path) and isinstance(data.get("cwd"), str):
        path = os.path.join(data["cwd"], path)
    if path_in_binder(path, protected_binders(env)):
        return blocked(env, data, "local-write")
    if path_in_state(path, env):
        return blocked(env, data, "state")
    return 0


def pre_shell(data: dict, env, tool: str, tool_input: dict) -> int:
    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        return 0
    powershell = tool == "PowerShell"
    binders = protected_binders(env)
    text = flatten(command, powershell, norm_path(Path.home()))
    in_binder = path_in_binder(str(data.get("cwd") or ""), binders) or mentions_binder(text, binders)
    in_state = mentions_state(text, env)
    if not in_binder and not in_state:
        return 0
    if runs_own_script(command, powershell, env):
        return 0
    if not looks_like_write(command, powershell):
        return 0
    return blocked(env, data, "local-write" if in_binder else "state")


def post(data: dict, env) -> int:
    tool = str(data.get("tool_name") or "")
    event = str(data.get("hook_event_name") or "PostToolUse")
    if tool == "AskUserQuestion":
        return post_question(data, env) if event == "PostToolUse" else 0
    match = DRIVE_TOOL.match(tool)
    if not match:
        return 0
    name = match.group("name")
    if event == "PostToolUse":
        log_event(env, data, stage="after", result="done")
        if name in LEARN_FROM:
            try:
                learn(env, data.get("tool_response"))
            except LockBusy:
                pass  # a later look in Drive teaches it again
        if name == "update_file" and not data.get("agent_id"):
            try:
                confirm_move(env, str(data.get("session_id") or ""), str(data.get("tool_use_id") or ""))
            except LockBusy:
                pass
    else:
        log_event(env, data, stage="after", result="failed",
                  error=str(data.get("error") or "")[:300])
    return 0


def post_question(data: dict, env) -> int:
    try:
        return read_his_answer(data, env)
    except LockBusy:
        return context("PostToolUse", "The binder lock was busy and couldn't save his answer, so "
                                      "nothing may move. Ask him again.")


def read_his_answer(data: dict, env) -> int:
    if data.get("agent_id"):
        return 0  # helpers can't give an Allow
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    response = data.get("tool_response")
    questions = question_texts(tool_input) or question_texts(response)
    asked = []
    for question in questions:
        found = MOVE_QUESTION.search(question)
        if found:
            asked.append((question, int(found.group(1) or 1)))
    if not asked:
        return 0
    session = str(data.get("session_id") or "")
    event = "PostToolUse"
    if not session:
        return context(event, "The binder lock couldn't tell which session this is, so nothing "
                              "may move.")
    if len(asked) > 1:
        clear_allow(env, session)
        return context(event, "Two \"Move these\" questions came at once, so the binder lock "
                              "can't tell which one he answered. Nothing may move. Ask one at "
                              "a time.")
    question, count = asked[0]
    if count < 1:
        clear_allow(env, session)
        return context(event, "The question asked to move 0 papers, so nothing may move.")
    if isinstance(response, dict) and response.get("afkTimeoutMs"):
        clear_allow(env, session)
        return context(event, "The question closed by itself while he was away, so nothing may "
                              "move. Ask again when he's back.")
    if isinstance(response, dict) and str(response.get("response") or "").strip():
        clear_allow(env, session)
        return context(event, "He wrote a reply instead of tapping a button, so nothing may move "
                              "yet. Follow his reply, show the whole list again and ask again.")
    answers = None
    for source in (response, tool_input):
        if isinstance(source, dict) and isinstance(source.get("answers"), dict):
            answers = source["answers"]
            break
    if answers is None:
        set_allow(env, session, count, question, confirmed=False)
        log_event(env, data, stage="after", result="answer not readable", moves=count)
        return context(event, "The binder lock couldn't read his answer. If he tapped Allow, "
                              "the first move will ask him once more. If he didn't tap Allow, "
                              "move nothing.")
    answer = lookup(answers, question)
    if answer is None and len(questions) == 1 and len(answers) == 1:
        answer = next(iter(answers.values()))  # one question, one answer: it's his answer to it
    notes = None
    for source in (response, tool_input):
        if isinstance(source, dict):
            note = lookup(source.get("annotations"), question)
            if isinstance(note, dict) and str(note.get("notes") or "").strip():
                notes = note["notes"]
    if is_allow(answer) and not notes:
        set_allow(env, session, count, question, confirmed=True)
        log_event(env, data, stage="after", result="his Allow", moves=count)
        return context(event, f"The binder lock has his Allow for {moves(count)}, good for 15 "
                              "minutes. Move exactly the list, in order.")
    clear_allow(env, session)
    log_event(env, data, stage="after", result="not Allow", answer=str(answer)[:60])
    if is_allow(answer):
        return context(event, "He tapped Allow but added a note, so nothing may move yet. Do "
                              "what the note says, show the whole list again and ask again.")
    return context(event, "His answer wasn't Allow, so nothing may move.")


def start(data: dict, env) -> int:
    binder, note = find_binder(env)
    lock_ok = True
    try:
        folder = ensure_state(env)
        if binder is not None:
            (folder / BINDER_CACHE).write_text(str(binder), encoding="utf-8")
        with StateLock(folder):
            pass
    except Exception:
        lock_ok = False
    try:
        import importlib.util
        heic_ready = all(importlib.util.find_spec(m) is not None for m in ("PIL", "pillow_heif"))
    except Exception:
        heic_ready = False
    python = f"{sys.version_info.major}.{sys.version_info.minor}"
    line = (f"Binder lock is {'on' if lock_ok else 'NOT working: it cannot save his Allow, so moves will be blocked'}. "
            f"Python {python} found. Binder folder on this PC: {'found' if binder else 'not found'}. "
            f"iPhone photo reader: {'ready' if heic_ready else 'not installed'}.")
    facts = [line,
             "In this session, moves and renames in Google Drive pass only after he taps Allow on "
             "an AskUserQuestion that says \"Move these N?\" (or \"Move this 1?\"), with the "
             "buttons Allow / Change something / Deny. One Allow covers N moves for 15 minutes. "
             "Retiring the old Job Tracker needs no tap, but only after a search_files shows it "
             "and the Old Trackers folder. New files: only folders, and Claude's own Docs and "
             "Sheets made from plain text. Trash, share and copy are always blocked, helpers only "
             "read, and the binder's folder on this PC is read-only for Claude."]
    facts.append(f"The binder's local copy on this PC: {binder}" if binder else note)
    if not heic_ready:
        facts.append("Reading iPhone (HEIC) photos here needs the pillow-heif add-on. Installing "
                     f"it needs his OK first. The line is: \"{sys.executable}\" -m pip install "
                     "pillow-heif")
    emit({"systemMessage": line,
          "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(facts)}})
    return 0


def main(argv=None) -> int:
    argv = sys.argv if argv is None else argv
    mode = argv[1] if len(argv) > 1 else ""
    try:
        raw = sys.stdin.buffer.read()
    except Exception:
        raw = b""
    try:
        data = json.loads(raw.decode("utf-8-sig", "replace")) if raw.strip() else None
    except ValueError:
        data = None
    if not isinstance(data, dict):
        data = None
    env = os.environ
    try:
        if mode == "pre":
            return pre(data, env) if data is not None else deny(MESSAGES["unreadable"])
        if mode == "post":
            return post(data or {}, env)
        if mode == "start":
            return start(data or {}, env)
        return deny(MESSAGES["unreadable"])
    except Exception as err:
        if mode in ("post", "start"):
            sys.stderr.write(f"binder lock: {type(err).__name__}: {err}\n")
            return 0
        return deny(f"{MESSAGES['crash']} ({type(err).__name__}: {err})")


if __name__ == "__main__":
    sys.exit(main())
