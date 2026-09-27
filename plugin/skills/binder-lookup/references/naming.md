<!-- Made from shared/naming.md. Edit shared/naming.md, then run: python tools/sync_shared.py -->

# How filed papers are named

Every paper gets a clear name when it's filed, in the same step as the move. The name changes; what's
inside never does.

**Pattern:** `YYYY-MM-DD Kind - Who - Detail.ext`

## Date

- The paper's own Date or Issued line.
- Not a due date, an expiry date, or the dates the work was done.
- If there's no such line, use the date by the signature.
- If there's no date at all, use the day the paper came into Drive.

## Kind, one of

- Estimate, Contract, Measurements
- Deposit, Payment
- Permit, Inspection
- Receipt, Bill
- Insurance
- Invoice, Lien Waiver
- Warranty
- Photo
- Other

Watch for these:
- **Bill or Invoice:**
  - A company's invoice *to him* is a **Bill**.
  - **Invoice** is only *his own* invoice to a customer.
- **Deposit or Payment:** his receipt for a customer's deposit is a **Deposit**. Later money from the
  customer is a **Payment**.
- **Insurance:** a certificate of insurance is **Insurance**.

## Who

Never the job, and never the job's street. The only exception is a job-site photo, which uses the
street.

| Kind | Who |
|---|---|
| Receipt, Bill | the store or supplier |
| Estimate, Contract, Measurements, Deposit, Payment, Invoice, Warranty | the customer |
| Permit, Inspection | the city |
| Insurance | the insurer |
| Lien Waiver | the supplier who signs it |
| Photo | the street |

**Use the short name he'd say:** "Riverbend Building Supply" becomes `Riverbend Supply`, "Sample City
Building Division" becomes `Sample City`. If the binder already has that business in a name, copy its
Who exactly.

## Detail

| Kind | Detail |
|---|---|
| Estimate | its number and total |
| Invoice (his) | its number and the balance due |
| Bill | its number and the amount due |
| Receipt, Deposit, Payment | the amount |
| Lien Waiver | the amount it covers |
| Permit, Insurance, Warranty | its number |
| Photo | 2 to 4 words, like `Roof before` |

**Never** a policy, account, card, check, ID or license number.

## .ext

Keep the original extension exactly: `.pdf`, `.jpg`, `.heic`.

## Examples

- `2026-09-16 Receipt - Riverbend Supply - $784.74.jpg`
- `2026-09-10 Deposit - Henderson - $4,000.00.jpg`
- `2026-09-11 Permit - Sample City - BP-2026-00417.pdf`
- `2026-09-22 Bill - Sample Haul-Away - 5521 - $434.00.pdf`
- `2026-09-21 Invoice - Henderson - 1047 - $9,950.00.pdf`
- `2026-09-23 Receipt - Sample Fuel Stop - $58.87.jpg` (goes to Truck & Shop)
- `2026-09-18 Photo - 412 Oak St - Roof before.jpg`

## Also

- **Short:** about 60 characters. Never more than 100.
- **Never** the characters `\ / : * ? " < > |`, which break on his PC. Use `-` instead.
- **One paper in several files** (a 2-page estimate sent as 2 photos): add ` - page 1`, ` - page 2`.
- **Two papers would get the same name:** add ` (2)` before the extension.
