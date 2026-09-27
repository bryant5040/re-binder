"""Tests for the binder lock (plugin/hooks/guard.py and hooks.json).

Each test feeds the guard the same JSON Claude Code sends on stdin, and checks the exit code:
2 means blocked, 0 means no objection. Every test uses a throwaway binder in a temp folder,
never the real one, and never touches Google Drive.

Run: python -m pytest -q tests      or, without pytest:  python tests/test_guard.py
"""
import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
GUARD = PLUGIN / "hooks" / "guard.py"
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"
DRIVE = "mcp__370cf63d-065d-41e0-ab1c-045f9cdb9c96__"  # the connector's id on one PC; any id works
OTHER_DRIVE = "mcp__1a2b3c4d__"
IDS = itertools.count(1)


class Lab:
    """A throwaway home folder, binder and lock record for one test."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="re-binder-guard-"))
        self.home = self.dir / "home"
        self.binder = self.home / "My Drive (tester@example.com)" / "R&E Binder"
        self.inbox = self.binder / "Inbox - Drop Here"
        self.inbox.mkdir(parents=True)
        self.data = self.dir / "plugin-data"
        self.env = dict(os.environ)
        self.env.update({
            "CLAUDE_PLUGIN_DATA": str(self.data),
            "CLAUDE_PLUGIN_ROOT": PLUGIN.as_posix(),
            "CLAUDE_PLUGIN_OPTION_BINDER_FOLDER": str(self.binder),
            "USERPROFILE": str(self.home),
            "HOME": str(self.home),
            "CLAUDE_CONFIG_DIR": str(self.home / ".claude"),
            "PYTHONDONTWRITEBYTECODE": "1",
        })

    def guard(self, mode, payload, raw=None):
        """Run guard.py like Claude Code does. Returns (exit code, JSON output or None, stderr)."""
        body = raw if raw is not None else json.dumps(payload).encode("utf-8")
        done = subprocess.run([sys.executable, str(GUARD), mode], input=body, capture_output=True,
                              env=self.env, timeout=120)
        out = done.stdout.decode("utf-8", "replace").strip()
        return done.returncode, (json.loads(out) if out.startswith("{") else None), \
            done.stderr.decode("utf-8", "replace")

    def tokens(self):
        path = self.data / "allow-tokens.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def log(self):
        path = self.data / "action-log.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]

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


# ---------------------------------------------------------------- the JSON Claude Code sends

def pre(tool, tool_input, session="s1", **extra):
    data = {"session_id": session, "hook_event_name": "PreToolUse", "tool_name": tool,
            "tool_input": tool_input, "tool_use_id": f"toolu_{next(IDS)}", "cwd": str(ROOT),
            "permission_mode": "default"}
    data.update(extra)
    return data


def post(tool, tool_input, tool_use_id, session="s1", response=None):
    return {"session_id": session, "hook_event_name": "PostToolUse", "tool_name": tool,
            "tool_input": tool_input, "tool_response": response or {}, "tool_use_id": tool_use_id,
            "cwd": str(ROOT), "permission_mode": "default"}


def question(text):
    return {"question": text, "header": "Filing", "multiSelect": False,
            "options": [{"label": "Allow", "description": "Move them all as listed"},
                        {"label": "Change something", "description": "Say what to change"},
                        {"label": "Deny", "description": "Nothing moves"}]}


def answered(text, answer, session="s1", **response_extra):
    """His answer to one AskUserQuestion, as PostToolUse sees it."""
    asked = {"questions": [question(text)]}
    response = {"questions": [question(text)], "answers": {text: answer}}
    response.update(response_extra)
    return post("AskUserQuestion", asked, f"toolu_{next(IDS)}", session, response)


def move(n, session="s1", **extra):
    return pre(DRIVE + "update_file", {"fileId": f"file{n}", "parentId": "folderX",
                                       "title": f"2026-09-16 Receipt - Riverbend Supply - $78{n}.00.jpg"},
               session, **extra)


SHEET = "application/vnd.google-apps.spreadsheet"
FOLDER = "application/vnd.google-apps.folder"
TRACKER = {"id": "t1", "title": "Job Tracker", "mimeType": SHEET, "parentId": "binder"}
OLD_TRACKERS = {"id": "oldTrackers", "title": "Old Trackers", "mimeType": FOLDER, "parentId": "archived"}
PERMIT = {"id": "p1", "title": "2026-09-11 Permit - Sample City - BP-2026-00417.pdf",
          "mimeType": "application/pdf", "parentId": "permitFolder"}


def drive_answer(body, shape="blocks"):
    """A connector answer, in each shape PostToolUse might hand it over."""
    if shape == "blocks":
        return [{"type": "text", "text": json.dumps(body)}]
    if shape == "text":
        return json.dumps(body)
    return body


def lab_sees(lab, files, shape="blocks", tool="search_files"):
    """Claude looks something up in Drive, and the lock reads the answer."""
    call = pre(DRIVE + tool, {"query": "title = 'Job Tracker'"})
    code, out, err = lab.guard("post", post(call["tool_name"], call["tool_input"], call["tool_use_id"],
                                            response=drive_answer({"files": files}, shape)))
    assert code == 0, (out, err)


def retire(file_id="t1", parent="oldTrackers", title="Job Tracker 2026-09-25 1423"):
    return pre(DRIVE + "update_file", {"fileId": file_id, "parentId": parent, "title": title})


def give_allow(lab, count, session="s1"):
    code, out, _ = lab.guard("post", answered(f"Move these {count}? Allow / Change something / Deny",
                                              "Allow", session))
    assert code == 0, out
    assert "Allow for" in out["hookSpecificOutput"]["additionalContext"]


def decision(out):
    return (out or {}).get("hookSpecificOutput", {}).get("permissionDecision")


def assert_blocked(result, words=""):
    code, out, err = result
    assert code == 2, f"expected a block, got exit {code}: {out} {err}"
    assert decision(out) == "deny"
    assert words.lower() in out["hookSpecificOutput"]["permissionDecisionReason"].lower()
    assert err.strip(), "a block must also give a plain message on stderr"


def assert_passes(result):
    code, out, err = result
    assert code == 0, f"expected no objection, got exit {code}: {out} {err}"
    assert decision(out) in (None, "allow"), out


def bash_path(path):
    """A path written the way Git Bash users escape it: /c/Users/.../My\\ Drive\\ \\(x\\)/R\\&E\\ Binder"""
    text = Path(path).as_posix()
    if len(text) > 1 and text[1] == ":":
        text = "/" + text[0].lower() + text[2:]
    for ch in " &()":
        text = text.replace(ch, "\\" + ch)
    return text


# ---------------------------------------------------------------- Google Drive moves

@with_lab
def test_trash_share_and_copy_are_always_blocked(lab):
    give_allow(lab, 5)
    assert_blocked(lab.guard("pre", pre(DRIVE + "trash_file", {"fileId": "f1"})), "trash")
    assert_blocked(lab.guard("pre", pre(OTHER_DRIVE + "share_file", {"fileId": "f1",
                   "emailAddress": "someone@example.com", "role": "reader"})), "never shared")
    assert_blocked(lab.guard("pre", pre(DRIVE + "copy_file", {"fileId": "f1"})), "copying")
    assert lab.tokens()["s1"]["moves_left"] == 5, "a blocked call must not use up his Allow"


@with_lab
def test_moves_sent_at_the_same_time_never_use_more_than_his_allow(lab):
    text = ("Here's where your 3 papers go:\n1. Riverbend receipt, Sep 16, $784.74 → 4 Bills & "
            "Receipts\nMove these 3? Allow / Change something / Deny")
    raw = json.dumps(answered(text, "Allow"), ensure_ascii=False).encode("utf-8")  # real UTF-8 bytes
    assert "Allow for 3 moves" in lab.guard("post", None, raw=raw)[1]["hookSpecificOutput"]["additionalContext"]
    running = []
    for n in range(8):
        body = lab.dir / f"move{n}.json"
        body.write_text(json.dumps(move(n)), encoding="utf-8")
        with open(body, "rb") as stdin:
            running.append(subprocess.Popen([sys.executable, str(GUARD), "pre"], stdin=stdin,
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                            env=lab.env))
    codes = sorted(p.wait(timeout=120) for p in running)
    assert codes == [0, 0, 0, 2, 2, 2, 2, 2], codes


@with_lab
def test_a_move_without_his_allow_is_blocked(lab):
    assert_blocked(lab.guard("pre", move(1)), "hasn't tapped Allow")


@with_lab
def test_an_allow_for_three_moves_allows_exactly_three(lab):
    give_allow(lab, 3)
    for n in (1, 2, 3):
        code, out, _ = lab.guard("pre", move(n))
        assert code == 0 and decision(out) == "allow", out
    assert_blocked(lab.guard("pre", move(4)), "all used")


@with_lab
def test_an_allow_older_than_15_minutes_is_blocked(lab):
    give_allow(lab, 3)
    tokens = lab.tokens()
    tokens["s1"]["expires"] = time.time() - 1
    (lab.data / "allow-tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
    assert_blocked(lab.guard("pre", move(1)), "ran out")


@with_lab
def test_deny_change_away_or_a_typed_reply_gives_no_allow(lab):
    text = "Move these 2? Allow / Change something / Deny"
    for payload in (answered(text, "Deny"), answered(text, "Change something"),
                    answered(text, "Allow", afkTimeoutMs=600000),
                    answered(text, "Allow", response="wait, #2 is Martinez"),
                    answered(text, "Allow", annotations={text: {"notes": "leave #2"}})):
        assert lab.guard("post", payload)[0] == 0
        assert_blocked(lab.guard("pre", move(1)), "hasn't tapped Allow")


@with_lab
def test_a_new_move_question_cancels_the_old_allow(lab):
    give_allow(lab, 3)
    assert_passes(lab.guard("pre", pre("AskUserQuestion", {"questions": [question("Move these 2?")]})))
    assert_blocked(lab.guard("pre", move(1)), "hasn't tapped Allow")


@with_lab
def test_claude_cannot_fill_in_his_answer(lab):
    asked = {"questions": [question("Move these 3?")], "answers": {"Move these 3?": "Allow"}}
    assert_blocked(lab.guard("pre", pre("AskUserQuestion", asked)), "only he can answer")


@with_lab
def test_an_allow_only_counts_in_its_own_session(lab):
    give_allow(lab, 3, session="s1")
    assert_blocked(lab.guard("pre", move(1, session="s2")), "hasn't tapped Allow")


@with_lab
def test_only_the_real_tracker_goes_to_old_trackers_without_his_allow(lab):
    lab_sees(lab, [TRACKER, OLD_TRACKERS, PERMIT])
    assert_blocked(lab.guard("pre", retire(parent="permitFolder")), "Old Trackers")
    assert_blocked(lab.guard("pre", pre(DRIVE + "update_file", {"fileId": "t1",
                                                                "title": "Job Tracker 2026-09-25 1423"})))
    code, out, _ = lab.guard("pre", retire())
    assert code == 0 and decision(out) == "allow"
    assert_blocked(lab.guard("pre", retire()), "Old Trackers")  # once only
    for title in ("Job Tracker", "Job Tracker 2026-09-25 1423 (2)", "Receipt 2026-09-25 1423"):
        assert_blocked(lab.guard("pre", pre(DRIVE + "update_file", {"fileId": "p1", "title": title})))


@with_lab
def test_a_paper_renamed_like_an_old_tracker_still_needs_his_allow(lab):
    lab_sees(lab, [TRACKER, OLD_TRACKERS, PERMIT])
    assert_blocked(lab.guard("pre", retire("p1")), "Old Trackers")
    assert_blocked(lab.guard("pre", retire("never-seen")), "Old Trackers")


def test_the_lock_learns_the_tracker_from_any_answer_shape():
    for shape in ("blocks", "text", "dict"):
        lab = Lab()
        try:
            lab_sees(lab, [TRACKER, OLD_TRACKERS], shape)
            code, out, _ = lab.guard("pre", retire())
            assert code == 0 and decision(out) == "allow", shape
        finally:
            lab.cleanup()


@with_lab
def test_the_lock_learns_a_tracker_claude_just_made(lab):
    made = pre(DRIVE + "create_file", {"title": "Job Tracker", "textContent": "Job,Status\n",
                                       "contentMimeType": "text/csv", "parentId": "binder"})
    assert_passes(lab.guard("pre", made))
    lab.guard("post", post(made["tool_name"], made["tool_input"], made["tool_use_id"],
                           response=drive_answer(dict(TRACKER, id="t2"))))
    lab_sees(lab, [OLD_TRACKERS], tool="get_file_metadata")
    code, out, _ = lab.guard("pre", retire("t2"))
    assert code == 0 and decision(out) == "allow"


@with_lab
def test_helpers_can_never_change_google_drive(lab):
    give_allow(lab, 3)
    helper = {"agent_id": "a12", "agent_type": "re-binder:paper-reader"}
    assert_blocked(lab.guard("pre", move(1, **helper)), "helpers only read")
    assert_blocked(lab.guard("pre", pre(DRIVE + "create_file", {"title": "x"}, **helper)), "helpers")
    assert lab.tokens()["s1"]["moves_left"] == 3


@with_lab
def test_the_main_assistant_can_make_folders_and_its_own_files(lab):
    folder = {"title": "Jobs", "mimeType": "application/vnd.google-apps.folder", "parentId": "b1"}
    code, out, err = lab.guard("pre", pre(DRIVE + "create_file", folder))
    assert code == 0 and out is None, (out, err)
    own = [("Read Me First", "text/plain"), ("Job Overview", "text/plain"),
           ("2026-09-25 Note - customer wants gutters", "text/plain"), ("Job Tracker", "text/csv"),
           ("Filing Record 2026-09-26 0907", "text/csv"), ("Filing Record 2026-09-25 2", "text/csv")]
    for title, kind in own:
        made = {"title": title, "textContent": "x", "contentMimeType": kind, "parentId": "b1"}
        assert_passes(lab.guard("pre", pre(DRIVE + "create_file", made)))


@with_lab
def test_uploads_and_look_alike_papers_are_never_made(lab):
    tries = [
        {"title": "2026-09-11 Permit - Sample City - BP-2026-00417.pdf", "base64Content": "JVBERi0xLjQ=",
         "contentMimeType": "application/pdf"},
        {"title": "IMG_5684.jpg", "base64Content": "/9j/4AAQ", "contentMimeType": "image/jpeg"},
        {"title": "2026-09-11 Permit - Sample City - BP-2026-00417", "textContent": "BUILDING PERMIT",
         "contentMimeType": "text/plain"},
        {"title": "Job Tracker", "content": "Sm9i", "contentMimeType": "text/csv"},
        {"title": "Job Tracker", "base64Content": "UEsDBA==",
         "contentMimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
        {"title": "Read Me First", "textContent": "x", "contentMimeType": "text/html"},
        {"title": "Jobs", "mimeType": FOLDER, "base64Content": "JVBERi0xLjQ=", "contentMimeType": "application/pdf"},
    ]
    for tool_input in tries:
        made = pre(DRIVE + "create_file", dict(tool_input, parentId="b1"))
        assert_blocked(lab.guard("pre", made), "own files")


@with_lab
def test_when_his_answer_cant_be_read_the_first_move_asks_him(lab):
    asked = {"questions": [question("Move these 2?")]}
    hidden = post("AskUserQuestion", asked, "toolu_q", response="He answered the questions.")
    assert "couldn't read" in lab.guard("post", hidden)[1]["hookSpecificOutput"]["additionalContext"]
    first = move(1)
    code, out, _ = lab.guard("pre", first)
    assert code == 0 and decision(out) == "ask", out
    lab.guard("post", post(first["tool_name"], first["tool_input"], first["tool_use_id"]))  # he said yes
    code, out, _ = lab.guard("pre", move(2))
    assert code == 0 and decision(out) == "allow", out
    assert_blocked(lab.guard("pre", move(3)), "all used")


# ---------------------------------------------------------------- the binder's folder on this PC

@with_lab
def test_writing_into_the_binder_on_this_pc_is_blocked(lab):
    note = str(lab.inbox / "note.txt")
    assert_blocked(lab.guard("pre", pre("Write", {"file_path": note, "content": "x"})), "never writes")
    assert_blocked(lab.guard("pre", pre("Edit", {"file_path": note, "old_string": "a", "new_string": "b"})))
    assert_blocked(lab.guard("pre", pre("NotebookEdit", {"notebook_path": str(lab.binder / "a.ipynb")})))
    lab_copy = lab.home / "My Drive (tester@example.com)" / "R&E Binder (lab Sep 24)" / "x.txt"
    assert_blocked(lab.guard("pre", pre("Write", {"file_path": str(lab_copy), "content": "x"})))


@with_lab
def test_writing_elsewhere_is_fine(lab):
    for path in (ROOT / "notes.txt", lab.home / "Downloads" / "receipt.txt",
                 lab.home / "My Drive (tester@example.com)" / "Other Folder" / "x.txt"):
        code, out, _ = lab.guard("pre", pre("Write", {"file_path": str(path), "content": "x"}))
        assert code == 0 and out is None, path


@with_lab
def test_reading_the_binder_is_always_fine(lab):
    b, ps = lab.binder.as_posix(), str(lab.binder)
    for tool, command in (
            ("Bash", f'cat "{b}/Inbox - Drop Here/receipt.txt"'),
            ("Bash", f'ls -la "{b}/Inbox - Drop Here" 2>/dev/null'),
            ("Bash", f'find "{b}" -iname "*.heic"'),
            ("Bash", f'cat "{b}/Inbox - Drop Here/Copy of estimate.pdf" | head -5'),
            ("Bash", f'python -c "print(open(r\'{b}/Inbox - Drop Here/r.txt\').read())"'),
            ("PowerShell", f"Get-ChildItem -LiteralPath '{ps}\\Inbox - Drop Here' | Select-Object Name"),
            ("PowerShell", f'Get-Content "{ps}\\Job Tracker.csv" 2>$null')):
        code, out, err = lab.guard("pre", pre(tool, {"command": command}))
        assert code == 0 and out is None, (command, out, err)


@with_lab
def test_shell_writes_into_the_binder_are_blocked(lab):
    b, ps = lab.binder.as_posix(), str(lab.binder)
    for tool, command in (
            ("Bash", f'cp ~/Downloads/receipt.pdf "{b}/Inbox - Drop Here/"'),
            ("Bash", f"cp receipt.pdf {bash_path(lab.inbox)}/"),
            ("Bash", f'echo hi > "{b}/notes.txt"'),
            ("Bash", f'mkdir -p "{b}/Jobs/2026 Test - 1 Main St"'),
            ("Bash", f'rm -rf "{b}/Archived"'),
            ("Bash", f'find "{b}" -name "*.tmp" -delete'),
            ("Bash", f"sed -i 's/a/b/' \"{b}/Job Tracker.csv\""),
            ("Bash", f'python -c "open(r\'{b}/x.txt\', \'w\').write(\'x\')"'),
            ("Bash", f'cmd /c del "{ps}\\x.pdf"'),
            ("Bash", f'touch "{lab.home.as_posix()}/My Drive (tester@example.com)/R&E Binder (lab Sep 24)/x"'),
            ("Monitor", f'tail -f build.log > "{b}/log.txt"'),
            ("PowerShell", f"Copy-Item -LiteralPath 'C:\\Temp\\r.pdf' -Destination '{ps}\\Inbox - Drop Here'"),
            ("PowerShell", f"Set-Content -Path '{ps}\\notes.txt' -Value 'x'"),
            ("PowerShell", f"Get-ChildItem '{ps}\\Inbox - Drop Here' | Remove-Item"),
            ("PowerShell", f'powershell -NoProfile -Command "Remove-Item \'{ps}\\x.pdf\'"')):
        assert_blocked(lab.guard("pre", pre(tool, {"command": command})), "never writes")
    inside = pre("Bash", {"command": "touch note.txt"}, cwd=str(lab.inbox))
    assert_blocked(lab.guard("pre", inside), "never writes")


@with_lab
def test_running_the_plugins_two_scripts_is_fine(lab):
    scripts = PLUGIN.as_posix() + "/scripts"
    for command in (f'python "{scripts}/heic_to_jpg.py"',
                    f'python "{scripts}/drop_to_inbox.py" "{lab.inbox.as_posix()}/receipt.pdf"'):
        code, out, _ = lab.guard("pre", pre("Bash", {"command": command}))
        assert code == 0 and out is None, command
    chained = f'python "{scripts}/drop_to_inbox.py" "C:/x.pdf"; rm "{lab.binder.as_posix()}/y"'
    assert_blocked(lab.guard("pre", pre("Bash", {"command": chained})))


@with_lab
def test_the_locks_own_record_cant_be_changed(lab):
    give_allow(lab, 1)
    token_file = lab.data / "allow-tokens.json"
    assert_blocked(lab.guard("pre", pre("Write", {"file_path": str(token_file), "content": "{}"})),
                   "own record")
    assert_blocked(lab.guard("pre", pre("Bash", {"command": f'echo "{{}}" > "{token_file.as_posix()}"'})),
                   "own record")
    # Its list of trackers too, even when the folder hides behind a variable.
    assert_blocked(lab.guard("pre", pre("Bash", {"command": 'echo "{}" > "$CLAUDE_PLUGIN_DATA/own-files.json"'})),
                   "own record")


# ---------------------------------------------------------------- failing closed, log, health line

@with_lab
def test_a_request_the_lock_cant_read_is_blocked(lab):
    code, out, err = lab.guard("pre", None, raw=b"this is not json")
    assert code == 2 and decision(out) == "deny" and err.strip()


@with_lab
def test_the_log_has_a_line_for_every_drive_action(lab):
    give_allow(lab, 1)
    call = move(1)
    lab.guard("pre", call)
    lab.guard("post", post(call["tool_name"], call["tool_input"], call["tool_use_id"]))
    lab.guard("pre", pre(DRIVE + "trash_file", {"fileId": "f9"}))
    lines = lab.log()
    before = [l for l in lines if l["tool"] == "update_file" and l.get("stage") == "before"]
    after = [l for l in lines if l["tool"] == "update_file" and l.get("stage") == "after"]
    assert before[0]["decision"] == "allowed" and before[0]["why"] == "his Allow"
    assert before[0]["fileId"] == "file1" and before[0]["parentId"] == "folderX" and before[0]["title"]
    assert after[0]["result"] == "done" and after[0]["tool_use_id"] == call["tool_use_id"]
    trash = [l for l in lines if l["tool"] == "trash_file"]
    assert trash and trash[0]["decision"] == "denied"


@with_lab
def test_session_start_prints_one_health_line(lab):
    code, out, _ = lab.guard("start", {"session_id": "s1", "hook_event_name": "SessionStart",
                                       "source": "startup"})
    assert code == 0
    line = out["systemMessage"]
    assert "Binder lock is on" in line and "Python" in line and "Binder folder on this PC: found" in line
    assert "iPhone photo reader" in line
    assert str(lab.binder) in out["hookSpecificOutput"]["additionalContext"]
    assert (lab.data / "binder-path.txt").read_text(encoding="utf-8") == str(lab.binder)


def test_hooks_json_points_every_event_at_the_guard():
    import re
    config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]
    commands = [h["command"] for groups in config.values() for g in groups for h in g["hooks"]]
    assert commands and all("guard.py" in c and "exit $(( 2 * !!$LASTEXITCODE ))" in c for c in commands)
    drive_group = config["PreToolUse"][0]["matcher"]
    for name in ("update_file", "trash_file", "share_file", "copy_file", "create_file"):
        assert re.search(drive_group, DRIVE + name) and re.search(drive_group, OTHER_DRIVE + name)
    assert not re.search(drive_group, DRIVE + "read_file_content")
    local_group = config["PreToolUse"][1]["matcher"]
    for tool in ("Bash", "PowerShell", "Write", "Edit", "NotebookEdit", "AskUserQuestion"):
        assert re.search(local_group, tool)
    assert not re.search(local_group, "Read")
    # The answers the lock learns the tracker from are read before Claude's next step, not later.
    for name in ("search_files", "get_file_metadata", "list_recent_files", "create_file", "update_file"):
        groups = [g for g in config["PostToolUse"] if re.search(g["matcher"], DRIVE + name)]
        assert groups and not any(h.get("async") for g in groups for h in g["hooks"]), name


# ---------------------------------------------------------------- the hook command fails closed

def git_bash():
    if os.name != "nt":
        return shutil.which("sh")
    candidates = [os.environ.get("CLAUDE_CODE_GIT_BASH_PATH", ""),
                  r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files (x86)\Git\bin\bash.exe"]
    git = shutil.which("git")
    if git:
        candidates.append(str(Path(git).resolve().parent.parent / "bin" / "bash.exe"))
    return next((c for c in candidates if c and Path(c).is_file()), None)


def windows_powershell():
    path = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    return str(path) if os.name == "nt" and path.is_file() else None


def hook_command(mode):
    config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]
    group = {"pre": config["PreToolUse"][0], "post": config["PostToolUse"][0]}[mode]
    return group["hooks"][0]["command"]


def run_hook(shell, command, plugin_root, payload, env):
    """Run a hooks.json command the way Claude Code does: Git Bash gets the plugin root filled in;
    PowerShell gets ${env:CLAUDE_PLUGIN_ROOT} in its place."""
    env = dict(env, CLAUDE_PLUGIN_ROOT=Path(plugin_root).as_posix())
    if shell == "bash":
        argv = [git_bash(), "-c", command.replace("${CLAUDE_PLUGIN_ROOT}", Path(plugin_root).as_posix())]
    else:
        argv = [windows_powershell(), "-NoProfile", "-NonInteractive", "-Command",
                command.replace("${CLAUDE_PLUGIN_ROOT}", "${env:CLAUDE_PLUGIN_ROOT}")]
    done = subprocess.run(argv, input=json.dumps(payload).encode("utf-8"), capture_output=True,
                          env=env, timeout=120)
    return done.returncode, done.stdout.decode("utf-8", "replace")


def check_wrapper(shell):
    if (git_bash() if shell == "bash" else windows_powershell()) is None:
        raise unittest.SkipTest(f"{shell} isn't on this PC")
    lab = Lab()
    try:
        command = hook_command("pre")
        trash = pre(DRIVE + "trash_file", {"fileId": "f1"})
        folder = pre(DRIVE + "create_file", {"title": "Jobs", "mimeType": "application/vnd.google-apps.folder"})
        # the real guard, from the real plugin folder (its path has spaces and an &)
        code, out = run_hook(shell, command, PLUGIN, trash, lab.env)
        assert code == 2 and '"deny"' in out, (shell, code, out)
        assert run_hook(shell, command, PLUGIN, folder, lab.env)[0] == 0
        # a guard that crashes, and one that doesn't even compile
        for body in ("raise RuntimeError('boom')\n", "def broken(:\n"):
            fake = lab.dir / f"fake plugin & {len(body)}"
            (fake / "hooks").mkdir(parents=True)
            (fake / "hooks" / "guard.py").write_text(body, encoding="utf-8")
            assert run_hook(shell, command, fake, trash, lab.env)[0] == 2, (shell, body)
        # no Python on the PATH at all
        system = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"
        bare_path = os.pathsep.join([str(system), str(system / "WindowsPowerShell" / "v1.0")]) \
            if os.name == "nt" else "/usr/bin/nonexistent"
        no_python = dict(lab.env, PATH=bare_path)
        assert run_hook(shell, command, PLUGIN, trash, no_python)[0] == 2, shell
        assert run_hook(shell, command, PLUGIN, folder, no_python)[0] == 2, shell
    finally:
        lab.cleanup()


def test_the_hook_command_blocks_when_the_guard_crashes_or_python_is_missing_git_bash():
    check_wrapper("bash")


def test_the_hook_command_blocks_when_the_guard_crashes_or_python_is_missing_powershell_51():
    check_wrapper("powershell")


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
