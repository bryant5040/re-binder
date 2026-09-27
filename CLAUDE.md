# Project R&E Binder: read this before doing anything

Claude reads this at the start of every session in this folder. It keeps every session on the plan.
Keep it short: history goes in the director's log, status goes on the dashboard.

> This is the public copy of the brief Bryant gave Claude Code while building this project. Private
> links, paths and the client's details are removed; everything about how the work was directed is
> as written.

## Start every session here

1. **Check the live state** on the project dashboard (a private page Claude updates after every task),
   and run `git log --oneline -5`.
2. **Draw one diagram in chat:** the journey, the steps done in each part, "you are here", and the
   finish line.
3. **Explain in plain words:** what this is for (3 lines), where we are, and the one next task.
4. **Let him pick** (AskUserQuestion), with the next task first. If his first message already names the
   task, that's his pick: give a two-line recap and do it.

## While working, and at the end

- **Every time a task finishes,** update the dashboard: mark it done with the date (green), mark the
  next one doing (yellow, only one at a time), and update the "Now" card. Bryant only reads the
  dashboard; Claude does all the updating.
- **Every finished workstream:** a director's log entry, then commit and push.
- **Every finished step:** Bryant's project tracker (a Word doc) gets the step's status and notes, plus
  a journal row.
- **Before every commit:**
  - run `python tools/sync_shared.py`, then `python tools/check.py`
  - after a change to `plugin/`, reload the plugin in the Code tab
- **End of session:** update the handoff, commit and push, and close with a progress diagram in chat
  and the one line to type next time.

## The big picture

- **Why:** Bryant is job hunting for AI adoption and enablement roles. This project proves he can take
  a real small business, find where AI helps, build it safely, and show with numbers that it works.
- **Where it came from:** a real 40-question assessment of a roofing contractor. It found three
  problems:
  - lost receipts and lien waivers
  - a schedule kept in his head
  - getting more work

  The Binder fixes the first. The other two are a roadmap. The public repo never names the business.
- **The finish line:** a tested build with real numbers, a short video, and the last bullet of his AI
  Solutions resume filled in.

## How we work

**Bryant directs, Claude builds.** The showcase has two halves: how he directed the build, then a demo
where he plays the owner.

| Who | Does |
|---|---|
| **Claude** | Builds everything: skills, helper agents, hooks, tests, fake papers, docs, the dashboard. Helper agents build workstreams in parallel; Claude integrates |
| **Bryant, building** | Directs in his own words, approves the plan, decides at each stop-and-ask point, reviews the result. No code or setup by hand |
| **Bryant, in the demo** | Plays the owner: puts papers in, asks Claude, taps Allow or Deny |

**Test lean:**
- Only test what's genuinely unknown, and do it on the PC.
- The phone isn't needed: chats and skills sync to it.
- Build, then check once.

## Rules that never bend

@guardrails/rules.md

## The design

- **Google's Drive connector does the moving.** Claude reads each paper and shows the list of where
  every paper goes. The owner changes anything he wants, then one tap files them all with clear
  names. We build the thinking and the guarding: skills, helper agents, hooks and rules, tests, docs.
- **The package is `plugin/`.** It holds:
  - 5 skills: `binder-setup`, `job-organizer`, `binder-filing`, `binder-lookup`, `binder-secretary`
  - helper agents, the Code-tab hooks, and 2 scripts

  `shared/` is the one source for the rules, folder map, names, the list, the tracker, the job
  checklist and Drive basics; `tools/sync_shared.py` copies it into every skill. Evals and docs stay
  out of the package.
- **Install:** this public GitHub repo, added as a Claude plugin. This needs Pro or Max. It syncs into
  the Code tab.
- **Mostly a regular Claude chat,** on his phone or PC. There, the rules are the skills' instructions,
  not a lock.
- **The Code tab is an optional extra.** The hooks are the hard lock: moves only after his tap, and no
  trash, share, or writes into the binder's files. Helper agents only read.
- **Ways in:**
  - the Inbox, through the Drive app. Scans are PDFs, and the connector reads them.
  - a photo sent in a chat: Claude makes an exact copy, he taps "Open in Google Drive" once, and
    Claude files it
  - in the Code tab, a paper dropped into the chat
- **iPhone (HEIC) photos:** the connector can't read them, and a chat can't convert them.
  - Setup tells him to turn on the iPhone's "Most Compatible".
  - If a HEIC still shows up, Claude asks him to send that photo in the chat, reads it, and files the
    Inbox original, renamed.
  - At the PC, the plugin's script converts it automatically.
- **Job Tracker:** the connector can't edit a file, so Claude makes a fresh Google Sheet after every
  change and moves the old one to `Archived › Old Trackers`. Undo reads the Filing Records.
- **Folders:** [the folder map](shared/folder-map.md) is the only copy. Making folders never asks;
  moving or renaming always does.

## Where things live

| Thing | Where |
|---|---|
| How each piece was built | [`docs/directors-log.md`](docs/directors-log.md) |
| The rules, and how each is kept | [`guardrails/rules.md`](guardrails/rules.md) |
| The folder map | [`shared/folder-map.md`](shared/folder-map.md) |
| The test results | [`evals/results/`](evals/results) |

## House style

- **A 13-year-old can follow every page:** short sentences, everyday words, one idea per line, tech
  words explained once.
- Tables instead of paragraphs where possible.
- State honest limits rather than hiding them.
- Numbers over adjectives.
- Nothing the owner reads needs translating.
- **Every paper used here is fake**, from a made-up company called Sample Roofing Co. No client paper is
  ever used, shown or committed.
