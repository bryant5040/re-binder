<!-- Made from shared/start-a-job.md. Edit shared/start-a-job.md, then run: python tools/sync_shared.py -->

# Start a job

The one recipe for making a job's folders. The job organizer uses it when he says "start a job for
Smith, 12 Elm St". The filing skill uses it when a paper needs a new job. Read the
[folder map](folder-map.md) and [the rules](rules.md) first.

**What he gets, every time.** The names come from "One job's folders" in the folder map.

```
R&E Binder/Jobs/<year> <customer> - <street>/
    Job Overview                                 a Google Doc
    1 Estimate & Measurements/ ... 8 Warranty/   all 8 numbered folders
R&E Binder/Archived/<year> <customer> - <street>/   empty, made at the same time
```

Nothing else: no extra folders, no notes files.

1. **Get the two things you need:** the customer's name and the street address, from his words or from
   the paper. If one is missing, ask for just that, in one short question.
2. **Build the job's name:** `<year> <customer> - <street>`, for example `2026 Henderson - 412 Oak St`.
   - Year: this year, unless he says another.
   - Customer: as he says it, usually a last name.
   - Street: the number and street only, no city or zip.
   - Leave out `\ / : * ? " < > |`. They break on his PC.
3. **Find the binder** with the Google Drive connector ([Drive basics](drive-basics.md)): `R&E Binder`
   and its `Jobs`, `Finished Jobs` and `Archived` folders. If any is missing, stop and say: "Your
   binder isn't set up yet. Say “set up my binder” first."
4. **Check the job isn't there already.** Look in Jobs and Finished Jobs, following every page to the
   end.
   - **The exact same name in Jobs:** make only the parts that are missing.
   - **The same customer or the same street, in Jobs under another name or anywhere in Finished
     Jobs:** stop and ask him if it's the same job. Make nothing until he answers. If it's a new job,
     make it. If it's the same job, make nothing, and go back to the skill that sent you here.
   - **He already said it's a new job:** don't ask again. Make it.
5. **Make what's missing,** parents first, one at a time, with the connector's create step:
   - the job's folder in Jobs
   - `Job Overview`: a Google Doc with four lines: Customer, Address (with the city if you have it),
     Phone (if he gave one), Notes (anything else he said about the job, like "hail damage")
   - the 8 numbered folders inside the job's folder, named exactly as in the map
   - the job's folder in Archived

   Making folders needs no Allow (rule 1). While making them, never move, rename, copy, share or
   trash anything.

**Then go back to the skill that sent you here.** It says what to tell him.
- **He asked ("start a job for …"):** the job organizer makes a fresh Job Tracker right away.
- **A paper on the filing list needs a new job:** do steps 1 to 4 while making the list. Do step 5
  only after his Allow, when that line comes up. The round ends with one Filing Record and one fresh
  Job Tracker ([the list](allow-list.md)).

## Common mistakes

| Mistake | Instead |
|---|---|
| The name has no year, or has the city | `<year> <customer> - <street>`, nothing more |
| Some of the 8 folders missing, or named differently | All 8, spelled exactly as in the map |
| No folder in Archived | Make it at the same time as the job |
