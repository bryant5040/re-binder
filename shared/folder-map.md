# The binder's folders

This is the only copy of the folder map. It lives in `shared/` and is copied into every skill. To
change a folder name, change it here, then run `python tools/sync_shared.py`.

## The whole binder

```
R&E Binder/
├── Read Me First                 what the binder is for, and the key phrases (a Google Doc)
├── Job Tracker                   one row per job, made fresh after every change (a Google Sheet)
├── Inbox - Drop Here/            the only folder he puts papers in
├── Jobs/                         one folder per job, made when he starts the job
├── Finished Jobs/                closed jobs, moved here whole
├── Truck & Shop/                 papers that belong to no job: gas, tools, the truck
└── Archived/                     anything taken out. Nothing is ever deleted
    ├── Truck & Shop/
    ├── Old Trackers/             each replaced Job Tracker, with its date in the name
    └── Filing Records/           one sheet per filing round, so "undo that" works
```

**"Set up my binder" makes everything above that's missing.** It never moves, renames or deletes
anything that's already there.

## One job's folders

"Start a job for Henderson, 412 Oak St" makes this, the same every time:

```
Jobs/
└── 2026 Henderson - 412 Oak St/
    ├── Job Overview                customer, address, phone, notes (a Google Doc)
    ├── 1 Estimate & Measurements/  legal
    ├── 2 Payments/
    ├── 3 Permit/                   legal
    ├── 4 Bills & Receipts/
    ├── 5 Insurance/                legal
    ├── 6 Photos/
    ├── 7 Invoice & Lien Waiver/    legal
    └── 8 Warranty/                 legal

Archived/
└── 2026 Henderson - 412 Oak St/    made at the same time
```

- **Notes he asks for** sit next to Job Overview, each its own dated Google Doc, like
  `2026-09-25 Note - customer wants gutters`. Starting a job never makes one.
- **Job folder name:** `<year> <customer> - <street>`, for example `2026 Henderson - 412 Oak St`.
- **Legal folders (1, 3, 5, 7 and 8)** hold legal papers. Like every paper, what's inside them is
  never changed. They can be filed and moved after his Allow, and the list marks them "(legal)".
- **Making folders never needs an Allow.** Moving or renaming a paper always does.

## Which paper goes where

| Paper | Folder |
|---|---|
| Estimate, measurements, signed contract | 1 Estimate & Measurements |
| Deposit or payment from the customer: check, receipt, card slip | 2 Payments |
| Building permit, inspection papers | 3 Permit |
| Bills and receipts for this job: materials, dumpster, labor | 4 Bills & Receipts |
| Insurance certificate, other insurance papers | 5 Insurance |
| Photos of the roof or the job site | 6 Photos |
| His final invoice to the customer; any lien waiver | 7 Invoice & Lien Waiver |
| The warranty he gives the customer | 8 Warranty |
| Gas, tools, the truck, shop supplies: anything for no job | Truck & Shop |
