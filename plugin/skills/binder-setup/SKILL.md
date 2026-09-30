---
name: binder-setup
description: Use when the roofing owner says "set up my binder" or "make my binder", asks "how does my binder work?", or his R&E Binder or its folders in Google Drive are missing.
---

# Set up the binder

The owner is a busy roofing contractor, not a computer person. Talk to him like a friendly helper:
short sentences, everyday words. No file paths, no code, no tool names. End every reply with one next
step.

**Your files:** every file linked below is in this skill's own folder: the "Base directory for this
skill" you were given when it loaded, plus the link (like `references/rules.md`). Read them from
there first. Never guess another folder, like /mnt/skills. If one won't open, find it with
`find / -xdev -path '*re-binder/skills/*' -name 'rules.md' 2>/dev/null`, using that file's name.

**Every Google Drive list:** use pageSize 100, then ask again with each `nextPageToken` until there
is none. The first page is never the whole list.

Read first: "The whole binder" in [the folder map](references/folder-map.md), [the rules](references/rules.md)
and [Drive basics](references/drive-basics.md).

| He says | Do |
|---|---|
| "set up my binder", "make my binder", or asks you to fix missing folders | Steps 1 to 6 |
| "how does my binder work?", or anything like it | Step 1 only, to look. Then the explanation and the next step (step 6). Make nothing |
| Anything else, and his binder or its folders are missing | Say "Your binder isn't set up yet. Say “set up my binder” first." Make nothing |

## Set up the binder

Touch Drive only through the Google Drive connector. Making folders and your own files needs no Allow
(rule 1). Never move, rename, copy, share or trash anything, even if it looks out of place. Make
nothing that isn't in "The whole binder": no dashboard, log, notes or extra tracker.

1. **Find the binder.** search_files with `title = 'R&E Binder' and mimeType =
   'application/vnd.google-apps.folder'`, excludeContentSnippets true, pageSize 100. Follow
   nextPageToken to the end. Check each title yourself: only exactly `R&E Binder` counts.
   - **One:** that's his binder.
   - **None:** make it at the top of his My Drive (no parentId). It's empty, so skip step 2.
   - **Two or more:** ask "I found [N] folders called “R&E Binder”, made [dates]. Which one is yours?"
     Make nothing until he answers.
   - **A look-alike, like `R&E Binder (lab Sep 24)`, is not his binder.** Never use, rename or move it.
     Never search with `contains` to find the binder.
2. **See what's there.** List the binder (`parentId = '<binder id>'`), then Archived if it's there,
   the same way, every page to the end. Something counts only if its name is exact and its kind is
   right: a folder for each folder, a Google Doc for Read Me First, a Google Sheet for the Job Tracker.
3. **Make the missing folders** (the files come in steps 4 and 5), named exactly as in the map, in the map's order, parents first, one
   at a time: the binder's own folders, then the ones inside Archived. Use the id each create gives
   back as the next parent. Don't search again for what you just made.
4. **Read Me First, only if it's missing:** create_file in the binder, title `Read Me First`,
   contentMimeType `text/plain`, and all of [read-me-first.md](references/read-me-first.md), word for
   word, as textContent. It becomes a Google Doc.
5. **Job Tracker, only if it's missing:** as in [tracker.md](references/tracker.md), steps 1 to 3, with
   [the job checklist](references/job-checklist.md) for Needs. If you just made all three of Jobs, Finished
   Jobs and Truck & Shop, skip the listing, and the textContent is exactly this. Otherwise follow
   tracker.md in full, so jobs already there get their rows:
   ```
   Job,Status,Started,Estimate,Deposit,Invoice,Paid,Permit,Insurance,Lien waivers,Warranty,Papers,Last paper,Needs
   Truck & Shop,,,,,,,,,,,0,,
   ```
6. **Tell him** (below).

**Something odd** (the right name but the wrong kind, like a file called “Jobs”, or the same thing
twice): leave it alone, and tell him in one line. A wrong-kind item doesn't count, so still make the
right one. Anything else in the binder is his: leave it, and don't mention it.

## Tell him

**The explanation** is four parts of read-me-first.md, word for word, in order: "What it's for", "How
to put papers in", "How filing works" and "What to say to Claude". **The next step** is: "Put papers in
“Inbox - Drop Here”, then say “file my inbox”."

| What happened | Reply |
|---|---|
| You made Read Me First just now (a first setup) | "Your binder is ready: “R&E Binder”, in your Google Drive. At the top are your Job Tracker and “Read Me First”. Here's how it works:" Then the explanation, then the next step |
| You made some things, but Read Me First was already there | "I added what was missing: [what you made]. Nothing else changed." Then the next step |
| You made nothing | "Your binder was already set up. Nothing changed." Then the next step |
| He asked how it works | "Here's how your binder works:" Then the explanation, then the next step. If step 1 found no binder, end with "Say “set up my binder” to make it." instead |

## In the Code tab only

The Code tab's lock runs on Python. Look at the binder lock's line at the start of the session:
- **It says Python or the iPhone-photo reader is missing:** say "Your PC still needs Python and the
  iPhone-photo reader. Ask whoever set up your Claude to install them." Then go on with the setup.
- **It says the binder folder isn't set:** after setup, say where the binder is on this PC, and that
  the plugin's "binder folder" setting should point to it.

## Common mistakes

| Mistake | Instead |
|---|---|
| Making things that aren't in the map: a dashboard, a project tracker, a log | Only the items in "The whole binder" |
| Using, renaming or moving a look-alike like "R&E Binder (lab Sep 24)" | Only the exact title counts. None found: make a new binder |
| Reading only the first page of a listing | Every page, to the end. Otherwise you make doubles |
| Promising "I'll update it every time" | The connector can't change what's inside a file. The tracker is made fresh after each change ([tracker.md](references/tracker.md)) |
| Leaving out what it's for, the phrases, the iPhone tip or Read Me First | Steps 4 and 6, every part |
| Ending with an open question, like "What do you want to work on first?" | End with the one next step |
| Building things when he only asked how it works | Explain only. Make nothing |
