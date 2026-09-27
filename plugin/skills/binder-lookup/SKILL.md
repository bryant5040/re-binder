---
name: binder-lookup
description: Use when the owner wants a paper found, a job's status or an undo, like "where's the Oak St lien waiver?", "find the Riverbend receipt", "how's the Henderson job?", "undo that", "put those back".
---

# Find a paper, job status, undo

The owner is a busy roofing contractor, not a computer person. Talk to him like a friendly helper:
short sentences, everyday words. No file paths, no code, no tool names. End with one next step.

**Your files:** every file linked below is in this skill's own folder: the "Base directory for this
skill" you were given when it loaded, plus the link (like `references/rules.md`). Read them from
there first. Never guess another folder, like /mnt/skills. If one won't open, find it with
`find / -xdev -path '*re-binder/skills/*' -name 'rules.md' 2>/dev/null`, using that file's name.

**Every Google Drive list:** use pageSize 100, then ask again with each `nextPageToken` until there
is none. The first page is never the whole list.

Read [the rules](references/rules.md) and [Drive basics](references/drive-basics.md) first.
- **Stay inside the binder** (the exact title `R&E Binder`). Every search names binder folders
  (`parentId = 'A'`, or many at once with `or`), never the rest of his Drive, and follows
  `nextPageToken` to the end. Never trash, share or copy anything, or contact anyone.
- Finding and job status only read. Undo moves papers only after his Allow.

## Which job?

Match his words to the job folders in Jobs and Finished Jobs, named like `2026 Henderson - 412 Oak St`:
a street ("Oak St"), a customer ("Henderson") or a house number ("412"). A paper's own number
("invoice 1047") is in the file names. Two jobs match: ask which one. None: say so plainly.

## Find a paper

1. **Pick the folder** from "Which paper goes where" in the [folder map](references/folder-map.md): a
   lien waiver is in 7 Invoice & Lien Waiver, a receipt in 4 Bills & Receipts, gas in Truck & Shop.
2. **List it and match the names.** Not there: the job's other folders, then Truck & Shop, the Inbox
   and Archived. No job named ("find the Riverbend receipt"): that folder in every job, in one search.
3. **Answer in 1 to 3 lines** (a found paper needs no next step): the paper's name, where it is, and its link. The link is the file's
   `viewUrl` from the search or metadata result. Never build or guess a link.

   ```
   Found it: “2026-09-15 Lien Waiver - Metro Lumber - $1,318.26.pdf”
   It's in Brooks › 7 Invoice & Lien Waiver.
   [Open it](the file's viewUrl)
   ```

   - **Several:** up to 5, newest first, one line each: name, place ("Walsh (finished job) › 4 Bills &
     Receipts"), link. More than 5: say how many more, and ask for the job or the date.
   - **None:** say so plainly, then offer to look through the papers waiting in his Inbox.

## How's a job?

Build it from the job's 8 folders (not the Job Tracker), so hand-filed papers count. Read only the
newest permit, for its expiry date. Reply with just these lines, at most 6 (a made-up job, Sep 25):

```
Brooks - 60 Pine Rd: billing. The final invoice went out Sep 19.
Money: estimate $9,800.00, deposit $3,000.00, final invoice $9,800.00. Paid so far: $3,000.00.
Missing: a lien waiver from Quick Dumpsters.
Heads up: the permit runs out Oct 2, in 7 days.
Last paper: Sep 19, 6 days ago.
When the Quick Dumpsters lien waiver comes in, put it in your Inbox and say “file my inbox”.
```

- **Money:** only amounts in the file names in 1, 2 and 7. "Paid so far" adds up every payment in 2.
- **Stage** ([the job checklist](references/job-checklist.md)) and what's **missing** at that stage:
  - new: nothing yet
  - waiting on the deposit: the deposit
  - in progress: the estimate, permit and insurance certificate
  - billing or finished: those, plus the final invoice, bills or receipts in 4, a lien waiver in 7 from
    each supplier in 4, and the warranty. The final payment (a Payment in 2, never the deposit) only
    once the final invoice is 14 days old.
  - Nothing missing: "Missing: nothing."
- **Heads up,** jobs in Jobs only: the permit has run out, or runs out within 30 days. Else no line.
- No timeline, no list of papers, no advice.

## Undo ("undo that", "put those back")

1. **Find the last round:** the newest Filing Record in Archived › Filing Records (its name has the
   date and time). If this chat changed something after it was made, undo that instead.
   - No record: "There's nothing to undo yet." Rows of kind `undo`: "That's already been undone."
2. **Check each row is still there:** get_file_metadata for each. Anything no longer in the row's "to
   folder" is left off the list, and named under "Staying where it is".
3. **Show the list** ([the list](references/allow-list.md)), grouped by where each paper is now. Each
   paper goes back to the Inbox with its "name before". A folder (a job closed, reopened or removed)
   goes back to its "from folder". Keep "(legal)" (papers in 1, 3, 5, 7, 8) and "(finished job)".

   ```
   Your last filing was Sep 18 at 4:10 pm. This puts each paper back in your Inbox, with its old name:

   Brooks - 60 Pine Rd
   1. Metro Lumber receipt, Sep 12, $1,318.26 → Inbox, as “IMG_20260912_153301.jpg”
   2. Quick Dumpsters bill 7730, $395.00 → Inbox, as “Invoice 7730.pdf”
   3. Metro Lumber lien waiver, $1,318.26 (legal) → Inbox, as “Scan 2026-09-15.pdf”

   Nguyen - 14 Lake Dr
   4. Nguyen estimate E-2026-052, $12,300.00 (legal) → Inbox, as “Estimate E-2026-052.pdf”

   Staying where it is
   - The Nguyen job and its folders.

   Move these 4 back? Allow / Change something / Deny
   ```

4. **Then ask once,** after the list is in the chat, with tap buttons if the app has them
   (AskUserQuestion in the Code tab, the question tool in a regular chat). Never the question before
   the list. Only Allow or a clear yes moves anything; anything else: "OK, nothing moved." A change:
   show the whole list again. In the Code tab, move only once the lock's note ("The binder lock ...")
   has come; no note: move nothing, and say so ([the list](references/allow-list.md)).
5. **Move exactly the list.** Right before, list those folders again; if anything changed, show the
   list again. Then one update_file per line, in order: title = its name before, parentId = the Inbox
   (a folder: its from folder). If one fails, stop and tell him what moved and what didn't.
6. **Afterwards:** "Done: 4 papers are back in your Inbox, with their old names." Then, with no tap:
   - a new Filing Record, made as [the list](references/allow-list.md) says, a row per line, kind
     `undo`: name before = its name until now, name after = the old name, from = where it was, to =
     where it went. Quote values with commas.
   - a fresh Job Tracker ([tracker.md](references/tracker.md)), then "Your Job Tracker is up to date."
7. **Next step:** "When you're ready, say “file my inbox”."

**Jobs.** A job that round started stays, with its folders. Never offer to delete or trash it. Remove
a job only when he asks, or says "undo that" right after starting it in this chat: say how many papers
are in it, ask "Move the Nguyen job to Archived? Allow / Deny", then one update_file that puts it inside its
folder in Archived (`Archived › 2026 Nguyen - 14 Lake Dr`), a Filing Record row (kind `move`), a fresh tracker.

## Common mistakes

| Mistake | Instead |
|---|---|
| A link you made up | The file's `viewUrl` from the search or metadata result |
| A paragraph, a timeline or advice for "how's the job?" | The 6 lines above, nothing more |
| Calling a final invoice unpaid after a few days | Only once it's 14 days old with no final payment in 2 Payments |
| Reading the status off the Job Tracker or Read Me First | The job's 8 folders |
| Offering to delete or trash the empty job after an undo | It stays. Only if he asks: Archived, after his Allow |
| Renaming the old Filing Record "undone" | Leave it. The new record, kind `undo`, says so |
| "Check the tracker yourself", or talk of what the tools can't do | Make a fresh tracker and say "Your Job Tracker is up to date." |
