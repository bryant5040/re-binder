# Dry-run scenario B: a binder after some filing, with gaps

A text copy of what Google Drive would show. Everything here is fake. Today is **Fri Sep 25, 2026**. The
binder is `R&E Binder` (id `BINDER`). The planted gaps are listed at the bottom, **for the lead only**.
A dry-run agent must not be shown that section.

```
R&E Binder/
├── Read Me First, Job Tracker (created 2026-09-24 17:05, id TRK2)
├── Inbox - Drop Here/                  id INBOX
│   ├── IMG_20260920_101500.jpg         added 2026-09-20
│   └── Scan 2026-09-20.pdf             added 2026-09-20
├── Jobs/
│   ├── 2026 Henderson - 412 Oak St/    id J1   created 2026-09-05
│   │   ├── 1 Estimate & Measurements/  2026-09-04 Estimate - Henderson - E-2026-031 - $13,650.00.pdf
│   │   ├── 2 Payments/                 2026-09-10 Deposit - Henderson - $4,000.00.jpg
│   │   ├── 3 Permit/                   2026-09-11 Permit - Sample City - BP-2026-00417.pdf  (the permit says: issued Sep 11, 2026, expires Oct 15, 2026)
│   │   ├── 4 Bills & Receipts/         2026-09-16 Receipt - Riverbend Supply - $784.74.jpg
│   │   │                               2026-09-19 Bill - Haul-Away - 5521 - $434.00.pdf
│   │   ├── 5 Insurance/                2026-09-01 Insurance - Sample Insurance Co - Certificate.pdf
│   │   ├── 6 Photos/                   (empty)
│   │   ├── 7 Invoice & Lien Waiver/    2026-09-21 Invoice - Henderson - 1047 - $9,950.00.pdf
│   │   │                               2026-09-21 Lien Waiver - Riverbend Supply - $784.74.pdf
│   │   └── 8 Warranty/                 2026-09-21 Warranty - Henderson - W-2026-031.pdf
│   ├── 2026 Martinez - 27 Maple Ave/   id J2   created 2026-09-02
│   │   ├── 1 Estimate & Measurements/  2026-09-02 Estimate - Martinez - E-2026-040 - $8,200.00.pdf
│   │   ├── 2 Payments/                 2026-09-08 Deposit - Martinez - $2,000.00.jpg
│   │   └── 3 to 8                      (all empty)
│   └── 2026 Okafor - 1580 Cedar Ct/    id J4   created 2026-09-20
│       ├── 1 Estimate & Measurements/  2026-09-24 Estimate - Okafor - E-2026-044 - $11,400.00.pdf
│       └── 2 to 8                      (all empty)
├── Finished Jobs/
│   └── 2025 Patel - 88 Birch Ln/       id J3   created 2025-10-01
│       ├── 1 Estimate & Measurements/  2025-10-01 Estimate - Patel - E-2025-090 - $6,300.00.pdf
│       ├── 2 Payments/                 2025-10-03 Deposit - Patel - $1,500.00.jpg
│       ├── 3 Permit/                   2025-10-04 Permit - Sample City - BP-2025-00888.pdf
│       ├── 4 Bills & Receipts/         2025-10-10 Receipt - Riverbend Supply - $2,210.00.jpg
│       ├── 5 Insurance/                2025-10-01 Insurance - Sample Insurance Co - Certificate.pdf
│       ├── 7 Invoice & Lien Waiver/    2025-11-01 Invoice - Patel - 0981 - $4,800.00.pdf
│       │                               2025-11-01 Lien Waiver - Riverbend Supply - $2,210.00.pdf
│       └── 8 Warranty/                 2025-11-02 Warranty - Patel - W-2025-114.pdf
├── Truck & Shop/                       2026-09-02 Receipt - Sample Fuel Stop - $61.20.jpg
│                                       2026-09-23 Receipt - Sample Fuel Stop - $58.87.jpg
└── Archived/
    └── Filing Records/                 Filing Record 2026-09-24 1702 (a Google Sheet; rows below)
```

**`Filing Record 2026-09-24 1702`** (columns: n, file id, name before, name after, from folder id, to folder id, kind):

| n | file id | name before | name after | from | to | kind |
|---|---|---|---|---|---|---|
| 1 | x21 | IMG_20260916_071522.jpg | 2026-09-16 Receipt - Riverbend Supply - $784.74.jpg | INBOX | J1F4 | move |
| 2 | x22 | Invoice 5521 - Haul-Away.pdf | 2026-09-19 Bill - Haul-Away - 5521 - $434.00.pdf | INBOX | J1F4 | move |
| 3 | x23 | Lien Waiver - Riverbend Supply - 412 Oak St.pdf | 2026-09-21 Lien Waiver - Riverbend Supply - $784.74.pdf | INBOX | J1F7 | move |
| 4 | x24 | Estimate E-2026-044 - Okafor.pdf | 2026-09-24 Estimate - Okafor - E-2026-044 - $11,400.00.pdf | INBOX | J4F1 | new job |

---

## For the lead only: the planted gaps (don't show dry-run agents)

1. Henderson: a bill from Haul-Away but no lien waiver from Haul-Away.
2. Henderson: the permit expires Oct 15, 2026, within 30 days.
3. Martinez: no permit, and work should have started.
4. Martinez: no insurance certificate.
5. Martinez: no new paper since Sep 8, which is 17 days (more than 14).
6. Okafor: an estimate but no deposit.
7. Patel (finished): invoice 0981 for $4,800.00 but no final payment in 2 Payments.
8. The Inbox: 2 papers waiting since Sep 20, which is 5 days (more than 3).

**Not a gap:** Henderson's final invoice was sent Sep 21, only 4 days ago, so no payment reminder yet.
