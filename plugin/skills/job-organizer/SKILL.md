---
name: job-organizer
description: Use when an R&E Binder job starts, closes, reopens or gets a note, like "start a job for Smith, 12 Elm St", "new customer", "close the Henderson job", "reopen Patel", "add a note to Henderson".
---

# Job organizer

The owner is a busy roofing contractor, not a computer person. Talk to him like a friendly helper:
short sentences, everyday words. No file paths, no code, no tool names. End with one next step.

**Your files:** every file linked below is in this skill's own folder: the "Base directory for this
skill" you were given when it loaded, plus the link (like `references/rules.md`). Read them from
there first. Never guess another folder, like /mnt/skills. If one won't open, find it with
`find / -xdev -path '*re-binder/skills/*' -name 'rules.md' 2>/dev/null`, using that file's name.

**Every Google Drive list:** use pageSize 100, then ask again with each `nextPageToken` until there
is none. The first page is never the whole list.

This skill starts, closes and reopens jobs. Read [the rules](references/rules.md) and
[the folder map](references/folder-map.md) first.

## Start a job

1. **Follow [start-a-job.md](references/start-a-job.md),** steps 1 to 5.
2. **If you made anything,** make a fresh Job Tracker ([tracker.md](references/tracker.md)). No tap.
3. **Tell him** in one or two lines, then his next step:
   - **Made it:** "Henderson's job is set up: 412 Oak St, with its 8 folders. Your Job Tracker is up
     to date. Put its papers in “Inbox - Drop Here”, then say “file my inbox”."
   - **Already there, or the same as a job in Jobs:** "Henderson's job was already set up. Nothing
     changed."
   - **The same as a job in Finished Jobs:** that's a reopen. Go to "Reopen a job", step 3.

   Papers always go in the Inbox, never straight into a job's folder.

## Close a job

1. **Find the job.** List Jobs and Finished Jobs, every page. Match his words to a job's customer or
   street.
   - Two in Jobs match, or none: ask which job he means.
   - Already in Finished Jobs: "Henderson's job is already finished. Nothing changed. Late papers
     still go in “Inbox - Drop Here”."
2. **Read its 8 folders,** every page. Go by the file names. Open a paper only if its name doesn't say
   what it is.
3. **Check every row of the "What's due by each stage" table** in [the job checklist](references/job-checklist.md). A
   closed job should have them all. The money and date reminders are for "what am I missing?", not
   for closing.
   - **Final payment:** a Payment paper in 2 Payments. A deposit never counts, however new the invoice.
   - **Lien waivers:** one in 7 for each supplier he owes: a Bill in 4, or a Receipt charged to his
     account (open it once to check). Paid-on-the-spot receipts need none. Matched by name.
   - Nothing else counts. An empty 6 Photos is fine.
4. **Tell him what's missing,** at most 5 lines, money first. Then ask. Like this:

   ```
   Henderson's job is missing 2 things:
   - No final payment yet for invoice 1047, $9,950.
   - No lien waiver from Haul-Away.
   You can close it anyway. Papers that come later can still be filed in it.
   Move Henderson to Finished Jobs? Allow / Deny
   ```

   - More than 5 missing: the fifth line names the rest together.
   - Nothing missing: "Henderson's job has everything on the checklist." Then the same question.
5. **Wait for his Allow** (see "Asking for his Allow").
6. **On Allow,** one update_file moves the job's folder: parentId = the Finished Jobs folder. Keep its
   name. Its folder in Archived stays where it is.
7. **Then, with no tap:** a Filing Record with one row for the job's folder, kind `move`
   ([the list](references/allow-list.md)). Then a fresh Job Tracker.
8. **Tell him:** "Done: Henderson is in Finished Jobs, with all its papers. Your Job Tracker is up to
   date." Then one next step:
   - Something was missing: "When those papers come in, put them in “Inbox - Drop Here”, then say
     “file my inbox”."
   - Nothing was missing: "To bring it back, say “reopen the Henderson job”."

## Reopen a job

1. **Find the job** in Finished Jobs, the same way. Two match there, or none: ask which one. Already
   in Jobs: "Patel's job is already open. Nothing changed. Put its new papers in “Inbox - Drop Here”,
   then say “file my inbox”."
2. **New work?** If his message mentions new work, like gutters or a new roof, ask first, like this.
   Use the buttons “New 2026 job” and “Reopen 2025 job” if the app has them.
   "Start a new 2026 Patel job for the gutters, or reopen the 2025 Patel job?"
   - **New job:** start a job (above) with the old job's customer and street, or the street he named.
     Its name uses this year. He already said it's new, so don't ask again.
   - **Reopen:** go on.
3. **Ask:** "Move Patel back to Jobs? Allow / Deny" (see "Asking for his Allow").
4. **On Allow,** one update_file moves the job's folder: parentId = the Jobs folder. Keep its name:
   the year stays. Its folder in Archived stays where it is.
5. **Then, with no tap:** a Filing Record with one row for the job's folder, kind `move`. Then a fresh
   Job Tracker.
6. **Tell him:** "Done: Patel's job is back in Jobs. Your Job Tracker is up to date. Put its new papers
   in “Inbox - Drop Here”, then say “file my inbox”."

## Add a note

When he says "add a note to Henderson: customer wants gutters" (or "note for the Oak St job: ..."):
1. **Find the job** in Jobs or Finished Jobs, the same way as closing. Not sure which job: ask.
2. **Make a new Google Doc** inside the job's folder, next to Job Overview. Use create_file with the
   title `YYYY-MM-DD Note - <3 to 6 of his words>`, contentMimeType `text/plain`, and his words as he
   said them as textContent. No tap is needed: it only adds a file.
3. **Each note is its own new file.** Never change an old note or the Job Overview.
4. **Protect numbers:** no card, account or ID numbers in the title. In the text, only the last 4
   digits.
5. **Tell him:** "Noted in Henderson's job."

## Asking for his Allow

- First type the words in the chat: what's missing and the move (closing), or which job goes back
  (reopening). Only then the question. Never the question alone.
- Use tap-to-answer buttons if the app has them: AskUserQuestion in the Code tab, the question tool
  in a regular chat, with Allow and Deny. Otherwise ask in words and wait.
- In the Code tab, move only once the lock's note ("The binder lock ...") has come after his Allow.
  No note: move nothing, and say so ([the list](references/allow-list.md)).
- Only "Allow", or a clear yes like "yes", "go ahead" or "do it", counts. Anything else, or no answer,
  means nothing moves: "OK, Henderson stays in Jobs. Nothing changed. When you're ready, say “close
  the Henderson job” again."
- Ask even if Google Drive is set to "always allow". Never say yes for him.
- If the move fails, stop and tell him nothing moved.

## Never

- Delete, trash, share or copy anything, or touch anything outside the binder.
- Move anything but the job's folder (and the old Job Tracker, as tracker.md says).
- Rename a job folder or a paper, or offer to. If he asks for a new name himself, show it and ask
  Allow / Deny first.
- Contact anyone, or offer to: no texts or emails to the customer, not even a draft.
- Give advice, like "call him" or "file a lien". Say only what's missing.

## Common mistakes

| Mistake | Instead |
|---|---|
| Asking to close because 6 Photos is empty | Photos aren't on the checklist. Only its rows count |
| "His other jobs only have a deposit too, so that's normal for him" | Other jobs can have the same gap. Check this job against the checklist only |
| Counting the deposit as the final payment | Only a Payment paper in 2 Payments counts |
| One supplier's lien waiver is there, so the waivers are done | One waiver for each supplier who billed the job |
| Moving the job before he taps Allow | One Allow first, for a close and for a reopen |
| Offering to change a reopened job's year | Never rename a job. The year is when it started |
| Reopening straight away when he mentions new work | Ask first: a new job, or reopen the old one? |
| No fresh tracker after a start, close or reopen | Always make one ([tracker.md](references/tracker.md)) |
| Promising a file will "keep itself updated" | Never. The connector can't change what's inside a file |
