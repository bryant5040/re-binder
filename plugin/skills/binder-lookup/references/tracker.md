<!-- Made from shared/tracker.md. Edit shared/tracker.md, then run: python tools/sync_shared.py -->

# The Job Tracker

A Google Sheet at the top of the binder, named "Job Tracker". The connector can't edit a file, so after
every change you make a fresh one. That covers:
- setup
- starting, closing or reopening a job
- a filing round
- an undo

It's your own file, so it needs no Allow.

## Steps

1. **List everything** you need, following every page to the end:
   - Jobs and Finished Jobs
   - every job's 8 folders
   - Truck & Shop

   You can list many folders at once with `parentId = 'A' or parentId = 'B'`.
2. **Build the rows** from what's actually in the folders, so papers he filed by hand count too. Make
   one row per job, plus one for Truck & Shop.
3. **Make the new sheet:**
   - create_file, titled `Job Tracker`, in the binder
   - contentMimeType `text/csv`, with the CSV as textContent. It becomes a Google Sheet.
4. **Retire the old one, if there was one.** In one update_file call:
   - rename it `Job Tracker YYYY-MM-DD HHMM`, using its own created time
   - move it to `Archived › Old Trackers`
5. **Tell him:** "Your Job Tracker is up to date." Never say a tracker "will update" by itself.

## Columns

The first line of the CSV is exactly this, with no spaces after the commas:

```
Job,Status,Started,Estimate,Deposit,Invoice,Paid,Permit,Insurance,Lien waivers,Warranty,Papers,Last paper,Needs
```

- **Job:** the job folder's name.
- **Status:** Active (in Jobs) or Finished (in Finished Jobs).
- **Started:** the job folder's created date.
- **Estimate:** the amount in the estimate's file name, in 1.
- **Deposit:** the deposits in 2, added up.
- **Invoice:** the balance in his final invoice's file name, in 7.
- **Paid:** every deposit and payment in 2, added up.
- **Permit, Insurance, Warranty:** "yes" if the folder holds a paper, or blank.
- **Lien waivers:** how many lien waivers are in 7. Use `0` when there are none.
- **Papers:** how many papers are in the job's 8 folders. Use `0` when there are none.
- **Last paper:** the date of the newest paper.
- **Needs:** a few words from [the job checklist](job-checklist.md), like `permit; lien waiver`.
- **The Truck & Shop row:** Job = `Truck & Shop`, with only Papers and Last paper filled in.
- **Money:** leave a money column blank when there's no paper for it.
- **Formatting:**
  - Put any value with a comma, like `$9,950.00`, in double quotes.
  - Never put a card, account or ID number anywhere in it.
