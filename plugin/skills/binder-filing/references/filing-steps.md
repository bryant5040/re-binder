# The Inbox round, step by step

The details behind each step of [the skill](../SKILL.md). He never sees this page.

## 1. The binder's folders

Find the binder ([drive-basics.md](drive-basics.md)). Then four listings, each with
`excludeContentSnippets` and every page to the end:
1. `parentId = '<binder>'`: the Inbox, Jobs, Finished Jobs, Truck & Shop, Archived, the Job Tracker.
2. `parentId = '<Jobs>' or parentId = '<Finished Jobs>' or parentId = '<Archived>'`: every job, and
   Archived's folders (Truck & Shop, Old Trackers, Filing Records, one per job).
3. All the job folders at once: their 8 numbered folders.
4. All the numbered folders and Truck & Shop at once: the papers already filed. Their names are
   enough to spot duplicates and to spell a Who the same way. Open one only to check a possible
   duplicate (step 6).

Keep every id. If a job has no folder in Archived when a duplicate needs one, make it (folders need no
Allow).

## 2. The Inbox

`parentId = '<Inbox>'`, every page. Keep each file's id, name, type (mimeType), size and created time.
Then one line to him, so he knows you're on it: "Reading your 15 papers now." Don't narrate each read.

## 3. Reading

- read_file_content, once per paper. Make several calls in one step when you can.
- Note one line of facts per paper (not in the chat), then never open that paper again:
  `f04 IMG_20260916_071522.jpg | Receipt | 2026-09-16 | Riverbend Building Supply | $784.74 | Job/PO: Henderson - 412 Oak`
- A personal paper's note is just `personal`. Card and account numbers: the last 4 digits at most.
- Not read: iPhone photos ([photos.md](photos.md)). A read that fails: the paper stays
  ([special-papers.md](special-papers.md)).

## 4. Matching

Look in Jobs and Finished Jobs, in this order:
1. **The street number and street:** "412 OAK" is `2026 Henderson - 412 Oak St`.
2. **No street:** the customer's name.
3. **Neither:** the PO or job line.

- His own company (the letterhead, "Bill to", "Insured") is never the job.
- **Clues that disagree** (a PO for Henderson, delivered to 27 Maple Ave): it stays in the Inbox,
  with one question: "Henderson or Martinez?" Never pick one yourself.
- **Gas, tools, the truck, shop supplies,** with no job clue: Truck & Shop.
- **Unsure** (materials with no job clue, a name that fits two jobs, no clue at all): it stays, with
  one question ([special-papers.md](special-papers.md)).
- **Photos with no writing** (a roof or a job site): one question for all of them, before the list
  ([special-papers.md](special-papers.md)).
- **A street that fits no job, for a customer who has one:** ask "Is this Henderson's 412 Oak St job,
  or a new job at 99 Pine St?"
- **A customer and street with no job, or a job in Finished Jobs:** see
  [special-papers.md](special-papers.md).

## 5. Naming

[naming.md](naming.md) is the rule: its date, kind, Who and detail tables, and its short-name rule.
Name each paper from your facts list, never from its old file name.

## 6. Duplicates

Two papers are the same paper when:
- they have the same number, amount and date (a scan and a photo of one paper), or
- they're the same size, with the same kind, number and amount (a second copy of one file).

Check papers already filed against their names. If the name has no number to compare (receipts),
open that filed paper once and compare its number or time. Two receipts with no number at all match
only if the time matches too. Not sure: ask.

- **Keep the clearer copy:** a scan beats a photo. If they're alike, the one that came in first.
- **The other copy** is a numbered line under "Duplicates". It goes to the job's folder in Archived
  (Truck & Shop papers: Archived › Truck & Shop), named like the kept paper plus ` (2)`, with its own
  extension.
- **Already filed:** the Inbox copy goes to Archived the same way.

## 7. The list

The shape is [allow-list.md](allow-list.md)'s. On top of that:
- Groups in this order: jobs (by name), finished jobs, Truck & Shop, New job?, Duplicates, Staying in
  your Inbox.
- A job's title is its folder name without the year: `Henderson - 412 Oak St`.
- Inside a job, folder order (1 to 8), then date. Number the lines 1 to N straight through.
- A line is what he'd know the paper by, then its folder: `Haul-Away bill 5521, Sep 22, $434.00 → 4
  Bills & Receipts`. Truck & Shop lines need no arrow.

## 8. Asking

- **First the list, typed in the chat as your own message.** Never the question first, and never the
  list only inside the question.
- **Then the buttons** (AskUserQuestion in the Code tab, the question tool in a regular chat):
  question `Move these 12?`, header `Filing`, and exactly these options: `Allow` ("Move and rename all
  12 as listed"), `Change something` ("Tell me what to change"), `Deny` ("Nothing moves").
- One paper: `Move this 1?`. Keep the number: the Code tab's lock reads it.
- His own typed answer is a change, unless it's a clear yes.
- After a change, number the lines again, show the whole list, and ask again. A yes covers only the
  list it answered, once.

## 9. Moving

- One update_file per line, in list order: `fileId`, `title` (the new name) and `parentId` (the
  folder), all in the same call.
- **A "New job?" line:** make the job ([start-a-job.md](start-a-job.md)), then move the paper into its
  1 Estimate & Measurements.
- **A move fails, or the Code tab's lock blocks it:** stop. Never try another way, like moving files
  on his PC. Make the Filing Record for what did move, and the tracker. Then, instead of "Done":
  "Moved 6 of 12. Number 7 didn't move, so I stopped. 7 to 12 are still in your Inbox."

## 10. The Filing Record

The columns are in [allow-list.md](allow-list.md). One row per line that moved. A name with a comma
goes in double quotes:

```
n,file id,name before,name after,from folder id,to folder id,kind
1,f01,Estimate E-2026-031 - Henderson.pdf,"2026-09-08 Estimate - Henderson - E-2026-031 - $13,650.00.pdf",INBOX,J1F1,move
11,f15,Estimate E-2026-044 - Okafor.pdf,"2026-09-24 Estimate - Okafor - E-2026-044 - $11,400.00.pdf",INBOX,J4F1,new job
12,f14,Invoice 5521 - Haul-Away (1).pdf,2026-09-22 Bill - Sample Haul-Away - 5521 - $434.00 (2).pdf,INBOX,AJ1,duplicate
```

If it can't be made, tell him: "Your papers are filed, but I couldn't save the filing record, so
"undo that" won't work for this round."

## 11. The last words

After the fresh tracker ([tracker.md](tracker.md)), two lines:

```
Done: 12 papers filed. Your Job Tracker is up to date.
Next: send me the iPhone photo IMG_5684 here in the chat, and I'll file it.
```

The next step is the first of these that fits:
1. after a stop: "Say "file my inbox" to try the rest again."
2. what he can do for a paper still in the Inbox: send a photo, take a new one, or answer a question
3. "Put new papers in "Inbox - Drop Here", then say "file my inbox"."
