# The scored runs, Sep 26, 2026

The 32 scored papers (30 papers: two come as 2 files each) went into the Inbox with the plugin's drop
script. The Martinez and Okafor jobs were started first; Henderson was already finished, and Brooks
was left for the "new job" test. The answer key was written and approved before any paper existed
([`scored_key.csv`](../paperwork/scored/scored_key.csv)). Claude drove each run the way the owner
would: one line, then one tap on Allow for the list as it was shown. Nothing on the list was changed.

## The numbers

| | Run 1: a regular Claude chat | Run 2: the Code tab |
|---|---|---|
| Plugin | 0.7.3 | 0.7.0: the Code tab's synced copy hadn't caught up with the day's updates yet |
| Right folder | **29 of 32** (91%) | **32 of 32** (100%) |
| Name parts right | 92 of 104 (88%). Every paper it filed was named right; the 12 misses are the 3 photos it didn't file | **104 of 104** (100%) |
| Tricky papers handled | **8 of 8** | **8 of 8** |
| Papers changed | **0** | **0** |
| Papers missing | **0** | **0** |
| Moves before his Allow | **0** (24 moves, all after it) | **0** (29 Drive updates, all after it) |
| Owner's part | "file my inbox", then one tap | "file my inbox", then one tap |
| Claude's time | **6 min 55 s** (3:31 to the list, 3:24 to move and record) | **about 26 min** (17:17 to the list, about 8:30 to move and record) |

Results, one row per paper: [run 1](2026-09-26-run1-chat-result.csv) and
[run 2](2026-09-26-run2-codetab-result.csv). Scored with
`python evals/score.py --key evals/paperwork/scored/scored_key.csv --binder <binder folder>`.

## What made the difference

- **The 3 roof photos.** In a chat, Google Drive's reader returns no text for a photo of a roof, so
  Claude can't see the date and street stamped on it. It asked which job instead of guessing, which
  is what rule 8 wants, but those 3 count as misses. In the Code tab, Claude opens the photo on the
  PC and reads the stamp.
- **The iPhone photo.** In a chat it stays in the Inbox with "please send me that photo here" (the
  key counts that as right). In the Code tab, the plugin's script makes a readable copy, and the
  original is filed, renamed.
- **Speed.** The chat was about 4 times faster. The Code tab opened every photo on the PC and had its
  filing-checker helper review the list before asking.

## What the runs found and fixed

| Found | Fix |
|---|---|
| The chat looked for the rule files in the wrong folder, then read only the first page of the Inbox (5 of 32 papers). It stopped before filing anything | 0.7.3: every skill says where its files are, and to follow every page of a Drive list |
| Mid-run, the Claude app synced the newer plugin and removed the 0.7.0 folder that session was using, so the lock's checks stopped running (Claude Code treats a missing plugin folder as a non-blocking error). The skill still asked first, so nothing moved without his tap | 0.7.4: in the Code tab, the skill moves only after the lock's own note follows his Allow. No note, nothing moves, and it asks him to start a new session |

## About the papers

The public copy of this repo prints a made-up city and area code on the fake papers. Nothing else on
them differs from the papers the test ran on.

## Not measured

- **Minutes by hand.** Bryant chose not to time filing the pile by hand, so there's no "minutes
  saved" number. Only Claude's measured times are reported.
