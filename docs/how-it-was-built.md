# How it was built

I directed; Claude Code built. Claude wrote every file in this repo: the skills, the lock, the tests,
the fake papers and these docs.

## How I directed it

- I set the goal and the rules. I picked the problem from the assessment, and Claude interviewed me
  for the safety rules. My answers became [the 9 rules](../guardrails/rules.md).
- I made the decisions. Claude stopped at each real choice, laid out the options, and I picked. Two
  examples: dropping our own file server for Google's connector, and writing the test's answer key
  before any test paper existed.
- Nothing counted until it was checked. Each skill was first tried without its instructions, to see
  what went wrong. The lock was attacked to find gaps. Nothing is claimed that wasn't measured, which
  is why there's no "minutes saved" figure.

## Timeline

| When | What happened |
|---|---|
| Sep 14–15, 2026 | My 40-question assessment of a real roofing business found three problems: lost receipts and lien waivers, a schedule kept in the owner's head, and getting more work. I picked the first. Claude planned the build and set up a private repo |
| Sep 22–23 | The first version moved files through its own small server (an MCP server). The owner's yes came from Claude Code's "Allow?" prompt |
| Sep 24 | A regular Claude chat on my phone read a receipt straight from Google Drive, through Google's own connector. So I retired our server: Google's connector does the moving, and this project builds everything around it |
| Sep 25 | Claude interviewed me for the safety rules. Then 7 builder agents worked in parallel, one per skill plus one for the lock and one for the test pile, while a lead Claude merged their work and ran the checks |
| Sep 25–26 | Live checks on my own Claude account, attempts to break the lock, and the scored runs on 32 fake papers |
| Sep 27 | This public repo, with the client's name left out, and the plugin installed from it |

## Before and after the skills

Before the skills were built, plain copies of Claude with no skill tried the same jobs on the same fake
binders. Their mistakes became the builders' to-do lists. Then fresh copies of Claude tried the jobs
again with only the finished skills.

| Job | Plain Claude, no skill | With the skill |
|---|---|---|
| Set up the binder | Built no binder folders, made up project files, and renamed my old binder without asking | Built all 11 items, left the old binder alone, and changed nothing when asked twice |
| Close a job | Missed an unpaid $9,950 invoice and a missing lien waiver, and moved the job without asking | Named exactly those 2 gaps, then asked for one Allow |
| File the Inbox | Names drifted, legal papers weren't marked, and the list was a big table | Standard names, legal papers marked, a short numbered list, and one tap |
| Undo | Offered to delete a folder | Never deletes: one list, one tap |
| "What am I missing?" | Found 5 of 8 gaps, raised 1 false alarm, searched outside the binder, and offered to text a customer | Found 8 of 8 gaps, with no false alarm, and stayed inside the binder |

## What testing caught

Testing found 6 problems, and each was fixed.

| Problem | Fix |
|---|---|
| A paper renamed to look like an old tracker could get past the Code tab lock | The lock only lets through the real tracker, one it has already seen in Drive |
| Any new file, even a PDF, could get past the lock | New files can only be folders and Claude's own Docs and Sheets |
| A chat asked "Move this 1?" before showing where the paper would go | Every skill shows the list before it asks |
| A chat looked for its instructions in the wrong folder, then read only 5 of 32 papers | Every skill says where its files are, and reads every page of a Drive list |
| Google Drive renamed a photo saved from a chat, so Claude couldn't find it | Claude matches it by its date and name parts |
| The lock stopped when the plugin updated in the middle of a session | Nothing moves unless the lock confirms the owner's OK |

The two lock gaps were fixed test-first: the new tests failed before the fix and passed after it. The
other four were fixed in the skills' instructions. The full results:
[the scored runs](../evals/results/2026-09-26-scored-runs.md).
