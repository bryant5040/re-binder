"""Makes the practice set: 10 FAKE papers for one made-up job (Sample Roofing Co., Henderson, 412 Oak St).

Receipts come out as phone-style photos (JPG); office papers come out as scanned-looking PDFs.
Every paper carries a small "sample / not real" line. Where each one belongs is in practice_key.csv.

This set is for building and trying things out. The scored test uses a separate set (paperwork/scored/)
that is never used while building, so the score stays honest.

Needs Pillow and the Windows fonts Arial, Consolas, Georgia and Ink Free.
Run from the repo root: python evals/make_practice_papers.py
It never touches the binder; it only writes into evals/paperwork/practice/.
"""
import os
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

random.seed(7)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paperwork", "practice")
FONTS = r"C:\Windows\Fonts"
os.makedirs(OUT, exist_ok=True)

_cache = {}


def F(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(os.path.join(FONTS, name + ".ttf"), size)
    return _cache[key]


def money(v):
    return f"${v:,.2f}"


# ---------- page helpers (PDF papers) ----------
W, H, M = 1275, 1650, 90  # letter size at 150 dpi
GRAY = (95, 95, 95)
INK = (30, 30, 30)
PEN = (25, 45, 140)
FAKE_LINE = "SAMPLE DOCUMENT  -  FAKE DATA MADE FOR A DEMO  -  NOT A REAL RECORD"


def new_page():
    im = Image.new("RGB", (W, H), "white")
    return im, ImageDraw.Draw(im)


def wrap(d, text, f, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=f) <= maxw:
                line = t
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


def para(d, x, y, text, f, maxw, fill=INK, lh=1.4):
    for ln in wrap(d, text, f, maxw):
        d.text((x, y), ln, font=f, fill=fill)
        y += int(f.size * lh)
    return y


def letterhead(d, name, addr, color, title, meta):
    d.rectangle([0, 0, W, 16], fill=color)
    tw = d.textlength(title, font=F("arialbd", 34))
    ns = 40
    while ns > 24 and d.textlength(name, font=F("arialbd", ns)) + tw + 40 > W - 2 * M:
        ns -= 2
    d.text((M, 60), name, font=F("arialbd", ns), fill=color)
    y = 116
    for ln in addr:
        d.text((M, y), ln, font=F("arial", 20), fill=GRAY)
        y += 27
    d.text((W - M, 60), title, font=F("arialbd", 34), fill=(45, 45, 45), anchor="ra")
    ry = 116
    for lab, val in meta:
        d.text((W - M - 380, ry), lab, font=F("arial", 20), fill=GRAY)
        d.text((W - M, ry), val, font=F("arialbd", 20), fill=INK, anchor="ra")
        ry += 27
    y = max(y, ry) + 24
    d.line([M, y, W - M, y], fill=color, width=3)
    return y + 30


def block(d, x, y, label, lines, width=520):
    d.text((x, y), label.upper(), font=F("arialbd", 17), fill=GRAY)
    y += 28
    for ln in lines:
        y = para(d, x, y, ln, F("arial", 22), width, lh=1.3)
    return y


def table(d, x, y, widths, header, rows, aligns, head_fill, fb=None):
    fh = F("arialbd", 19)
    fb = fb or F("arial", 20)
    total_w = sum(widths)
    hh = 44
    d.rectangle([x, y, x + total_w, y + hh], fill=head_fill)
    cx = x
    for w, h, a in zip(widths, header, aligns):
        tx = cx + 12 if a == "l" else cx + w - 12
        d.text((tx, y + hh / 2), h, font=fh, fill="white", anchor="lm" if a == "l" else "rm")
        cx += w
    y += hh
    lh = int(fb.size * 1.32)
    for i, r in enumerate(rows):
        cells = [wrap(d, str(c), fb, w - 24) for c, w in zip(r, widths)]
        rh = max(len(c) for c in cells) * lh + 18
        if i % 2 == 1:
            d.rectangle([x, y, x + total_w, y + rh], fill=(244, 245, 247))
        cx = x
        for lines, w, a in zip(cells, widths, aligns):
            ty = y + 10
            for ln in lines:
                if a == "l":
                    d.text((cx + 12, ty), ln, font=fb, fill=INK)
                else:
                    d.text((cx + w - 12, ty), ln, font=fb, fill=INK, anchor="ra")
                ty += lh
            cx += w
        y += rh
        d.line([x, y, x + total_w, y], fill=(205, 205, 205), width=1)
    return y


def totals(d, y, pairs, bold_last=True):
    for i, (lab, val) in enumerate(pairs):
        last = bold_last and i == len(pairs) - 1
        f = F("arialbd" if last else "arial", 24 if last else 21)
        d.text((W - M - 300, y), lab, font=f, fill=INK, anchor="ra")
        d.text((W - M - 12, y), val, font=f, fill=INK, anchor="ra")
        y += 36
    return y


def signature(d, x, y, name_written, printed, date=None):
    d.text((x + 10, y), name_written, font=F("Inkfree", 44), fill=PEN)
    y += 58
    d.line([x, y, x + 420, y], fill=INK, width=2)
    d.text((x, y + 8), printed, font=F("arial", 18), fill=GRAY)
    if date:
        d.text((x + 470, y - 50), date, font=F("Inkfree", 34), fill=PEN)
        d.line([x + 460, y, x + 680, y], fill=INK, width=2)
        d.text((x + 460, y + 8), "Date", font=F("arial", 18), fill=GRAY)
    return y + 40


def save_pdf(im, name):
    d = ImageDraw.Draw(im)
    d.text((W // 2, H - 45), FAKE_LINE, font=F("arial", 15), fill=(150, 150, 150), anchor="mm")
    # a touch of scanner softness
    im = im.filter(ImageFilter.GaussianBlur(0.35))
    im.save(os.path.join(OUT, name), "PDF", resolution=150)


SRC = "Sample Roofing Co."
SRC_ADDR = ["100 Example Ave, Sample City, MO 00001", "(555) 555-0142  -  office@sampleroofing.example"]
NAVY = (22, 52, 104)
OWNER = "Dana Henderson"
SITE = "412 Oak St, Sample City, MO 00009"

# ---------- 1. Estimate ----------
im, d = new_page()
y = letterhead(d, SRC, SRC_ADDR, NAVY, "ESTIMATE",
               [("Estimate #", "E-2026-031"), ("Date", "September 8, 2026"), ("Good for", "30 days")])
block(d, M, y, "Prepared for", [OWNER, SITE, "(555) 555-0163"])
block(d, 660, y, "Roof measurements", [
    "Roof area: 2,400 sq ft (24 squares)", "Pitch: 6/12  -  Layers to remove: 1",
    "Ridge 42 ft  -  Eaves 120 ft  -  Rakes 96 ft", "Waste factor: 10%"], width=520)
y += 190
rows = [
    ("Tear off existing shingles, 1 layer", "24", "sq", "85.00", "2,040.00"),
    ("Architectural shingles, Charcoal, installed", "26.4", "sq", "310.00", "8,184.00"),
    ("Synthetic underlayment", "24", "sq", "35.00", "840.00"),
    ("Ice and water shield, eaves and valleys", "6", "sq", "95.00", "570.00"),
    ("Drip edge", "216", "ft", "3.25", "702.00"),
    ("Ridge vent", "42", "ft", "12.00", "504.00"),
    ("Pipe boots", "3", "ea", "45.00", "135.00"),
    ("Dumpster and haul-away", "1", "ea", "525.00", "525.00"),
    ("Building permit", "1", "ea", "150.00", "150.00"),
]
y = table(d, M, y, [540, 110, 90, 150, 205], ["Description", "Qty", "Unit", "Price", "Amount"],
          rows, ["l", "r", "l", "r", "r"], NAVY)
y = totals(d, y + 24, [("Total", money(13650)), ("Deposit due at signing", money(4000)),
                       ("Balance due on completion", money(9650))])
y = para(d, M, y + 20, "Notes: Includes our 10-year workmanship warranty. Rotten decking, if found, is "
         "replaced at $75.00 per sheet, only after the owner says OK.", F("arial", 20), W - 2 * M, fill=GRAY)
d.text((M, y + 40), "Accepted by owner:", font=F("arialbd", 20), fill=INK)
signature(d, M, y + 80, "Dana Henderson", "Owner signature", "9/10/26")
save_pdf(im, "Estimate E-2026-031 - Henderson.pdf")

# ---------- 2. Building permit ----------
GREEN = (28, 94, 60)
im, d = new_page()
y = letterhead(d, "Sample City Building Division", ["1 Example Plaza, Room 400", "Inspections: (555) 555-0100"],
               GREEN, "BUILDING PERMIT",
               [("Permit No.", "BP-2026-00417"), ("Issued", "September 11, 2026"), ("Expires", "March 11, 2027")])
y = block(d, M, y, "Site address", [SITE])
y = block(d, M, y + 18, "Property owner", [OWNER])
y = block(d, M, y + 18, "Contractor", [SRC + "  -  Contractor license RC-0000-SAMPLE"], width=W - 2 * M)
y = block(d, M, y + 18, "Work allowed", [
    "Residential re-roof. Tear off and replace asphalt shingles, about 24 squares. "
    "Replace damaged decking as needed. No structural changes."], width=W - 2 * M)
y = table(d, M, y + 30, [700, 395], ["Fees", "Amount"],
          [("Residential re-roof permit", "$150.00"), ("Paid by contractor, receipt 88213", "PAID")],
          ["l", "r"], GREEN)
y = block(d, M, y + 30, "Inspections required", [
    "Final inspection when the job is done. Call (555) 555-0100 at least one day ahead."], width=W - 2 * M)
d.rectangle([M, y + 30, W - M, y + 100], outline=GREEN, width=3)
d.text((W // 2, y + 65), "POST THIS PERMIT WHERE IT CAN BE SEEN FROM THE STREET", font=F("arialbd", 24),
       fill=GREEN, anchor="mm")
signature(d, M, y + 150, "R. Example", "Building official", "9/11/26")
save_pdf(im, "Permit BP-2026-00417.pdf")

# ---------- 3. Certificate of insurance ----------
MAROON = (120, 30, 45)
im, d = new_page()
y = letterhead(d, "Sample Mutual Insurance Co.", ["Agent: Pat Example, Sample Insurance Agency",
                                                  "(555) 555-0175  -  certs@samplemutual.example"],
               MAROON, "CERTIFICATE OF INSURANCE", [("Date issued", "09/09/2026"), ("Certificate #", "C-26-8841")])
y = para(d, M, y, "This certificate is for information only. It gives the certificate holder no rights and does "
         "not change the policies listed below.", F("arial", 19), W - 2 * M, fill=GRAY)
top = y + 20
block(d, M, top, "Insured", [SRC, "100 Example Ave", "Sample City, MO 00001"])
block(d, 660, top, "Certificate holder", [OWNER, "412 Oak St", "Sample City, MO 00009"])
y = top + 170
rows = [
    ("General liability", "GL-0000-4417", "01/01/2026", "01/01/2027",
     "$1,000,000 each occurrence\n$2,000,000 aggregate"),
    ("Commercial auto", "CA-0000-2290", "01/01/2026", "01/01/2027", "$1,000,000 combined single limit"),
    ("Workers' compensation", "WC-0000-7712", "01/01/2026", "01/01/2027", "Statutory\n$500,000 each accident"),
]
y = table(d, M, y, [230, 190, 150, 150, 375], ["Coverage", "Policy #", "Starts", "Ends", "Limits"],
          rows, ["l", "l", "l", "l", "l"], MAROON)
y = block(d, M, y + 30, "Description of operations", [
    "Roofing contractor. Re: roof replacement at 412 Oak St, Sample City, MO 00009."], width=W - 2 * M)
y = block(d, M, y + 24, "Cancellation", [
    "If any policy above is cancelled before it ends, notice will be sent as the policy requires."],
    width=W - 2 * M)
signature(d, M, y + 60, "Pat Example", "Authorized representative")
save_pdf(im, "Certificate of Insurance - Sample Roofing.pdf")

# ---------- 4. Dumpster invoice (a bill to Sample Roofing) ----------
ORANGE = (196, 94, 20)
im, d = new_page()
y = letterhead(d, "Sample Haul-Away Dumpsters", ["88 Example Rd, Sample City, MO 00011", "(555) 555-0121"],
               ORANGE, "INVOICE", [("Invoice #", "5521"), ("Date", "09/22/2026"), ("Terms", "Net 15"),
                                   ("Due", "10/07/2026")])
block(d, M, y, "Bill to", [SRC, "100 Example Ave", "Sample City, MO 00001"])
block(d, 660, y, "Job site", ["Henderson  -  412 Oak St", "Dropped 09/15/2026", "Picked up 09/22/2026"])
y += 170
rows = [
    ("20-yard dumpster, 7-day rental", "1", "395.00", "395.00"),
    ("Disposal, up to 3 tons", "1", "included", "0.00"),
    ("Extra weight over 3 tons", "0.6 ton", "65.00", "39.00"),
]
y = table(d, M, y, [600, 150, 170, 175], ["Description", "Qty", "Rate", "Amount"], rows,
          ["l", "r", "r", "r"], ORANGE)
y = totals(d, y + 24, [("Subtotal", money(434)), ("Balance due", money(434))])
para(d, M, y + 30, "Please write invoice 5521 on your check. Thank you for your business!",
     F("arial", 20), W - 2 * M, fill=GRAY)
save_pdf(im, "Invoice 5521 - Haul-Away.pdf")

# ---------- 5. Final invoice to the owner ----------
im, d = new_page()
y = letterhead(d, SRC, SRC_ADDR, NAVY, "INVOICE",
               [("Invoice #", "1047"), ("Date", "September 21, 2026"), ("Terms", "Due on receipt")])
block(d, M, y, "Bill to", [OWNER, SITE])
block(d, 660, y, "Job", ["Roof replacement", "Work finished September 19, 2026", "Per estimate E-2026-031"])
y += 170
rows = [
    ("Roof replacement per estimate E-2026-031", "13,650.00"),
    ("Change order #1: replace 4 sheets of rotten decking at $75.00 (owner OK'd 9/17)", "300.00"),
]
y = table(d, M, y, [895, 200], ["Description", "Amount"], rows, ["l", "r"], NAVY)
y = totals(d, y + 24, [("Total", money(13950)), ("Less deposit received 9/10 (check #1042)", "-" + money(4000)),
                       ("Balance due", money(9950))])
para(d, M, y + 30, "Thank you for choosing Sample Roofing Co. Your warranty certificate is attached. "
     "Make checks payable to Sample Roofing Co.", F("arial", 20), W - 2 * M, fill=GRAY)
save_pdf(im, "Invoice 1047 - Henderson.pdf")

# ---------- 6. Lien waiver from the supplier ----------
TEAL = (20, 90, 100)
im, d = new_page()
y = letterhead(d, "Riverbend Building Supply", ["2200 Example Industrial Dr, Sample City, MO 00010",
                                                "(555) 555-0187"],
               TEAL, "LIEN WAIVER", [("Date", "09/22/2026"), ("Type", "Conditional, final")])
d.text((W // 2, y + 10), "CONDITIONAL WAIVER AND RELEASE UPON FINAL PAYMENT", font=F("arialbd", 26),
       fill=INK, anchor="ma")
y += 70
rows = [("Property", SITE), ("Owner", OWNER), ("Customer", SRC + " (account 4471)"),
        ("Materials supplied through", "September 16, 2026"), ("Payment amount", "$784.74")]
y = table(d, M, y, [380, 715], ["Item", "Details"], rows, ["l", "l"], TEAL)
y = para(d, M, y + 30,
         "When Riverbend Building Supply has received and cashed the payment amount above from the customer, "
         "Riverbend Building Supply waives and releases any lien rights it has on the property above for "
         "materials it supplied to this job through the date above.", F("arial", 22), W - 2 * M)
y = para(d, M, y + 14,
         "This release is conditional. It does not take effect until that payment has been received and has "
         "cleared the bank.", F("arial", 22), W - 2 * M)
signature(d, M, y + 60, "Chris Example", "Chris Example, Credit Manager, Riverbend Building Supply", "9/22/26")
save_pdf(im, "Lien Waiver - Riverbend Supply - 412 Oak St.pdf")

# ---------- 7. Workmanship warranty ----------
im, d = new_page()
d.rectangle([40, 40, W - 40, H - 80], outline=NAVY, width=6)
d.rectangle([56, 56, W - 56, H - 96], outline=NAVY, width=2)
d.text((W // 2, 130), SRC, font=F("arialbd", 44), fill=NAVY, anchor="ma")
d.text((W // 2, 200), "Workmanship Warranty", font=F("georgia", 60), fill=INK, anchor="ma")
d.text((W // 2, 290), "Certificate W-2026-031", font=F("arial", 24), fill=GRAY, anchor="ma")
y = 360
rows = [("Property", SITE), ("Owner", OWNER), ("Work", "Full roof replacement, architectural shingles"),
        ("Work finished", "September 19, 2026"), ("Warranty period", "10 years, through September 19, 2036")]
y = table(d, 150, y, [330, 645], ["Warranty details", ""], rows, ["l", "l"], NAVY)
y = block(d, 150, y + 30, "What this covers", [
    "Leaks or failures caused by how we installed the roof. We fix them at no charge for labor or "
    "materials."], width=975)
y = block(d, 150, y + 20, "What this does not cover", [
    "Storm, hail or wind damage; damage from falling trees or foot traffic; work done by others; "
    "problems with the shingles themselves (those fall under the maker's own warranty, registered "
    "separately)."], width=975)
y = block(d, 150, y + 20, "To make a claim", ["Call (555) 555-0142 and give the certificate number above."],
          width=975)
signature(d, 150, y + 50, "S. Sample", "Owner, Sample Roofing Co.", "9/22/26")
save_pdf(im, "Workmanship Warranty W-2026-031.pdf")


# ---------- phone-photo helpers (receipts) ----------
def phone_photo(paper, name, angle, bg, portrait=True, fill_w=0.72, fill_h=0.80):
    size = (1512, 2016) if portrait else (2016, 1512)
    canvas = Image.new("RGB", size, bg)
    dc = ImageDraw.Draw(canvas)
    for i in range(0, size[1], 4):  # grain in the table or seat
        s = random.randint(-10, 10)
        c = tuple(max(0, min(255, v + s)) for v in bg)
        dc.line([(0, i), (size[0], i + random.randint(-25, 25))], fill=c, width=4)
    scale = min(size[0] * fill_w / paper.width, size[1] * fill_h / paper.height)
    p = paper.resize((int(paper.width * scale), int(paper.height * scale)), Image.LANCZOS).convert("RGBA")
    p = p.rotate(angle, expand=True, resample=Image.BICUBIC)
    shadow = Image.new("RGBA", p.size, (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", p.size, (0, 0, 0, 120)), mask=p.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    x = max(0, (size[0] - p.width) // 2 + random.randint(-25, 25))
    y = max(0, (size[1] - p.height) // 2 + random.randint(-20, 20))
    canvas = canvas.convert("RGBA")
    canvas.alpha_composite(shadow, (x + 14, y + 18))
    canvas.alpha_composite(p, (x, y))
    canvas = canvas.convert("RGB")
    vign = Image.radial_gradient("L").resize(size).point(lambda v: int(v * 0.75))
    canvas = Image.composite(ImageEnhance.Brightness(canvas).enhance(0.7), canvas, vign)
    canvas = Image.blend(canvas, Image.effect_noise(size, 40).convert("RGB"), 0.03)
    canvas = canvas.filter(ImageFilter.GaussianBlur(0.8))
    canvas.save(os.path.join(OUT, name), "JPEG", quality=84)


def thermal_receipt(lines, width_chars=32):
    f = F("consola", 26)
    cw = f.getlength("M")
    lh = 34
    pad = 34
    w = int(cw * width_chars + pad * 2)
    h = lh * len(lines) + pad * 2 + 30
    im = Image.new("RGB", (w, h), (250, 250, 245))
    d = ImageDraw.Draw(im)
    y = pad
    for ln in lines:
        bold = ln.startswith("!")
        ln = ln.lstrip("!")
        if ln.startswith("^"):
            ln = ln[1:].center(width_chars)
        col = (45, 45, 55)
        d.text((pad, y), ln, font=f, fill=col)
        if bold:
            d.text((pad + 1, y), ln, font=f, fill=col)
        y += lh
    # torn bottom edge
    teeth = [(0, h - 14)]
    for x in range(0, w + 12, 12):
        teeth.append((x, h - (4 if (x // 12) % 2 else 16)))
    teeth += [(w, h), (0, h)]
    d.polygon(teeth, fill=(0, 0, 0))
    mask = Image.new("L", im.size, 255)
    ImageDraw.Draw(mask).polygon(teeth, fill=0)
    im.putalpha(mask)
    return im


def row(left, right, width=32):
    return left + right.rjust(width - len(left))


# ---------- 8. Supply-house receipt (photo) ----------
supply = thermal_receipt([
    "^RIVERBEND BUILDING SUPPLY", "^2200 Example Industrial Dr", "^Sample City, MO 00010", "^(555) 555-0187",
    "-" * 32, row("SALE", "09/16/2026 07:14"), row("Ticket: 4471-0916", "Clerk: MJ"),
    "Acct: SAMPLE ROOFING CO.", "Job/PO: HENDERSON - 412 OAK", "-" * 32,
    "ARCH SHINGLE CHARCOAL BDL", row("  10 @ 38.50", "385.00"),
    "SYNTH UNDERLAYMENT 10SQ RL", row("   2 @ 89.00", "178.00"),
    "COIL ROOF NAIL 1-1/4 BOX", row("   1 @ 54.99", "54.99"),
    "DRIP EDGE 10FT WHITE", row("  10 @ 9.75", "97.50"),
    "-" * 32, row("SUBTOTAL", "715.49"), row("TAX 9.679%", "69.25"), "!" + row("TOTAL", "784.74"),
    "-" * 32, row("CHARGED TO ACCOUNT", "784.74"), "", "^THANK YOU", "",
    "^** SAMPLE - NOT A REAL RECEIPT **",
])
phone_photo(supply, "IMG_20260916_071522.jpg", angle=-3.5, bg=(112, 86, 62))

# ---------- 9. Gas station receipt (photo, belongs to no job) ----------
gas = thermal_receipt([
    "^SAMPLE FUEL STOP #12", "^1800 Example Hwy", "^Sample City, MO 00016", "-" * 32,
    row("09/23/2026", "06:38 AM"), row("PUMP 7", "UNLEADED"), row("GALLONS", "18.402"),
    row("PRICE/GAL", "$3.199"), "!" + row("FUEL TOTAL", "$58.87"), "-" * 32,
    row("VISA", "****0000"), "AUTH 000000", "", "^THANK YOU - DRIVE SAFE", "",
    "^** SAMPLE - NOT A REAL RECEIPT **",
])
phone_photo(gas, "IMG_20260923_063811.jpg", angle=4.0, bg=(58, 60, 64))

# ---------- 10. Handwritten deposit receipt from a receipt book (photo) ----------
slip = Image.new("RGB", (1150, 640), (251, 238, 165))
d = ImageDraw.Draw(slip)
d.text((40, 30), "RECEIPT", font=F("arialbd", 40), fill=(60, 60, 60))
d.text((1110, 36), "No. 0212", font=F("arialbd", 32), fill=(190, 40, 40), anchor="ra")
labels = [(130, "Date"), (210, "Received from"), (290, "Amount"), (370, "For"), (450, "Paid by")]
for yy, lab in labels:
    d.text((40, yy), lab, font=F("arial", 26), fill=(70, 70, 70))
    d.line([(230, yy + 32), (1110, yy + 32)], fill=(120, 150, 200), width=2)
for x, lab in [(250, "Cash"), (420, "Check #"), (820, "Money order")]:
    d.text((x, 450), lab, font=F("arial", 24), fill=(70, 70, 70))
d.text((40, 530), "Received by", font=F("arial", 26), fill=(70, 70, 70))
d.line([(230, 562), (700, 562)], fill=(120, 150, 200), width=2)
d.text((1110, 600), "SAMPLE - NOT A REAL RECEIPT", font=F("arial", 18), fill=(150, 140, 100), anchor="ra")
hand = F("Inkfree", 42)
for (x, yy, t) in [(250, 118, "9/10/26"), (250, 198, "Dana Henderson"),
                   (250, 278, "Four thousand and 00/100 -- $4,000.00"),
                   (250, 358, "Deposit - new roof, 412 Oak St"),
                   (560, 432, "1042"), (250, 518, "S. Sample")]:
    d.text((x, yy + random.randint(-4, 4)), t, font=hand, fill=PEN)
d.ellipse([(405, 438), (530, 490)], outline=PEN, width=3)  # circled "Check #"
phone_photo(slip.convert("RGBA"), "IMG_20260910_184407.jpg", angle=2.0, bg=(70, 72, 76), fill_w=0.88)

print("\n".join(sorted(os.listdir(OUT))))
