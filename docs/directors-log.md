# How this was built: the director's log

I directed each building block, Claude Code built it, and we checked it together. There is one entry
per block, oldest first. The quotes are my own words from the build sessions, with only the spelling fixed and
the client's name replaced.

The owner in these notes is a real roofing contractor I assessed. Every paper the system touches is
fake, from a made-up company called Sample Roofing Co.

**Each entry has the same five parts:** what I asked for · what Claude built · how we checked it ·
what I decided · the commit.

> **Note:** until Sep 24, 2026 the binder had its own MCP server. The last entry explains why it was
> retired for Google's Drive connector. Older entries are kept exactly as they were.

---

## Sep 14–15, 2026 · The idea, the plan and the repo (step 3)

**What I asked for**
> "Can we turn this into a complete organizer as well? Say he starts a job. The job will automate and
> build out components and folders that he may need, such as receipts, insurance statements, cost...
> and all he will have to do is speak to Claude."

> "Let's do Project R&E Binder."

**What Claude built**
- A 26-step plan in five parts, each step with a reason and a plain-English deliverable.
- This private repo:
  - the ignore rules, written first so personal notes and real papers can never be committed
  - the brief Claude reads at the start of every session (`CLAUDE.md`)
  - a README skeleton
  - the license and the plugin manifest

**How we checked it**
- The repo is private on GitHub.
- The ignore rules were in the first commit, before any other file.

**What I decided**
- It runs in Claude Code on my PC, and the binder lives in Google Drive.
- It uses fake paperwork only, and I play the owner.
- No MCP server yet: "for right now let's exclude the MCP server, we will make it a bit more simpler."

**Commits:** `9bf0e89`, `8a4b602`

---

## Sep 22, 2026 · The binder gets its own MCP server (plan change)

**What I asked for**
> "I want to be able to create a local MCP server and demonstrate that we can do that."

> "Do we really even need an MCP server? Honestly, be honest: is problem 1's resolution enough for the
> resume?"

**What Claude built**
- An honest comparison of the options.
- A revised design:
  - The binder gets its own small MCP server, the only thing allowed to move files.
  - The owner's yes comes from a box the server shows him, so Claude can never say yes on his behalf.
- The brief, the tracker and the plan were updated, and the overlapping trackers were retired.

**How we checked it**
- The design was checked against the Claude Code docs: plugin-bundled servers, and servers asking
  the user directly (MCP elicitation).
- The one open question, whether that box shows up in the desktop app, became the first test of
  step 4.

**What I decided**
- Build only the Binder, with its own server.
- The yes comes from the server asking the owner directly.
- The assessment's other two problems stay a researched roadmap.

**Commits:** `643aee5`, `b10a08c`, `b5ac3bc`

---

## Sep 23, 2026 · Google Drive set up (step 1), and who does what

**What I asked for**
> "You are supposed to build out the entire folder structure, not me do it manually. I'm supposed to be
> guiding and directing you."

> "I want to be able to show how I got Claude to build the building blocks, and then I will demo."

**What Claude built**
- Checked my Google Drive setup and found both accounts in Stream mode, where the files live only
  online.
- Walked me through switching one account to Mirror mode. That puts real files on the PC, which the
  server needs so it can copy a file, check it arrived, then remove the original.
- Lined up every document with how this project runs:
  - I direct one building block at a time, Claude builds it, and each block gets an entry here.

**How we checked it**
- Claude confirmed the Drive files are now real files on the PC.
- I checked the same Drive shows on my phone.

**What I decided**
- Mirror mode, on one account.
- The server builds every binder folder (step 4). It keeps the two I had already made by hand.
- In the demo I play the owner. My only jobs are dropping papers into the Inbox and clicking Yes or
  Stop.

**Commit:** "Line the records up: roles, the director's log, steps 1 and 2"

---

## Sep 23, 2026 · A practice set of fake papers

**What I asked for**
> "I want you to output those files and make fake receipts and documents so I can just download.
> Please make me a folder of it."

**What Claude built**
- A script that makes 10 fake papers for one made-up job:
  - receipts as phone-style photos
  - estimates, invoices, a permit, an insurance certificate, a lien waiver and a warranty as
    scanned-looking PDFs
  - each one marked "sample, not real"
- A key that says where each paper belongs (`evals/paperwork/practice/`).

**How we checked it**
- Claude opened every paper and checked it read correctly.
- It fixed two layout slips and rebuilt the set.

**What I decided**
- These are practice papers for building and trying things out.
- The scored test in Part 4 uses a new set that Claude never sees while building, with its answer key
  written first, so the score is honest.

**Commit:** "Add a practice set of fake papers for the Henderson job"

---

## Sep 23, 2026 · Block 4a: the plugin package and the yes box test (step 4)

**What I asked for**
> "Please go slowly and let's start to work this test box out and everything. Let's go just step one
> through five, but if you need me to do anything manual, please [tell me]. But please explain just
> like you did now, in plain English, while you are doing things so I can understand."

**What Claude built**
1. **The box label and store shelf** (`.claude-plugin/plugin.json`, `marketplace.json`): the project
   installs as a Claude Code plugin straight from its own folder. The label asks one question, which
   folder is the binder, and the answer lives in my own settings, never in the repo.
2. **The start-up note** (`.mcp.json`): when the plugin turns on, it starts the binder's own server.
3. **The starter script** (`server/launch.py`): the first time, it builds the server's own private
   Python toolbox (`mcp` 2.2.0, pinned), then starts the server. Its messages never go down the line
   the server uses to talk to Claude Code.
4. **The test gatekeeper** (`server/binder_server.py`): one tool, `test_yes_box`, which shows the yes
   box (Yes, file them / Change something / Stop) and reports what was clicked. It can't move, change
   or delete anything.
5. **A crash-test checker** (`server/tests/test_yes_box.py`): a stand-in app answers the box every
   possible way.
6. **Installed it** in my Claude settings (after I approved), pointed at an empty practice folder on
   my Lab Drive, not my real Drive.

**How we checked it**
- The toolbox built in 28 seconds.
- The crash-test checker passed 6 of 6: only the one tool is offered, the box says "TEST ONLY" and
  shows the three choices, and Yes, Stop, "no thanks" and closing the box are each reported correctly.
- The server starts through the starter script and answers.
- After `/reload-plugins`, Claude Code said plugin servers only start in a new session, so the click
  test, where I answer the box myself, happened in a fresh chat. It is the next entry.

**What I decided**
- Build the whole chain before any clicking, and test it without Claude first.
- Use a practice folder on the Lab Drive until "set up my binder" is built and proven.

**Commit:** "Block 4a: package the plugin and build the yes box test server"

---

## Sep 23, 2026 · Block 4a, the click test: the yes moves to Claude Code's "Allow?"

**What I asked for**
> "Run the yes box test."

> "Honestly, let's just do Claude ask the question, because using the terminal may be too technical
> and scary for the end user. Let's clean up our files and stick to option B."

> "If we're just doing Claude, do we even need an MCP server anymore? Can we do anything else to build
> an MCP server to help improve the workflow and just the entire performance of this binder?"

> "I still want to discuss. Can you make a chart of what the server can do vs what Claude can do?
> Benefits of each, because I feel like even without the server it can do more. Also how do agents
> and skills come into play as well."

> "With the MCP server, can we actually drop images and/or files within our Claude Code chat right
> here, and the MCP actually take that and file it instead of using the Inbox?"

Then, in a fresh chat:

> "Run the allow test."

> "I clicked Deny, but no rejection response came back. Also, if we want to use a server, can we set
> up a custom connection, one with a URL and everything, or does that not work?"

**What Claude built**
- **Ran the click test.** The server asked for its box, and the desktop app answered "decline" by
  itself. I never saw a box. Claude checked that no setting was answering it: this app just doesn't
  show a server's own box.
- **Laid out three ways forward:** the terminal version of Claude Code, Claude Code's own "Allow?"
  prompt (the plan's backup), or a pop-up window of the server's own.
- **Rewrote the test tool** so the server never shows a box of its own. If the tool runs at all, the
  owner allowed it. Its checks were rewritten to match.
- **Added an "always ask" rule** to my Claude settings for the five tools that change the binder:
  the test tool, `file_papers`, `archive_paper`, `undo_last` and `close_job`. A plugin can't carry
  this rule itself, so it lives in my own settings. The Claude Code docs say it asks even in auto
  mode and beats any "always allow".
- **A chart of Claude alone against Claude plus the server**, job by job, and a picture of how the
  skills, helper agents, guard hooks, the "Allow?" prompt and the server fit together.

**How we checked it**
- The click test in the desktop app: the server's box came back "declined" with nothing shown to me.
- The rewritten server passed 3 of 3 checks: only the test tool is offered, it moves nothing, and it
  never shows a box of its own.
- The first "Allow?" try, in the same chat, ran without asking me. The rule and the new server code
  were both added partway through that chat, and both load when a chat starts, so the test is
  repeated in a fresh chat.
- **Two drop tests.** I dragged two fake papers into the chat with "file this"; nothing was filed.
  - The receipt photo reached Claude as a re-saved copy in the chat's own temporary folder, renamed
    and smaller (204 KB against the original's 265 KB).
  - The insurance certificate PDF reached Claude as the untouched original, with its real name and
    its place in Downloads.
  - Claude read both and placed them where the practice key says: the receipt in Henderson ›
    4 Bills & Receipts, and the certificate in Henderson › 5 Insurance, marked protected.
- **The allow test, in a fresh chat, in auto mode.** Auto mode normally runs tools without asking,
  so it's the hardest case. First Claude checked that the test tool had loaded and that the "always
  ask" rule was in my settings.
  - Call 1: the "Allow?" question showed and waited. I clicked Allow, and the test ran ("The owner
    clicked Allow, so the test ran. Nothing moved.").
  - Call 2: it showed again. I clicked Deny, and the test never ran.
  - What surprised me: after Deny, nothing came back. Claude Code ends Claude's turn on a Deny, so
    Claude can't reply until I type. For the owner, that means Claude has to say what Deny does
    *before* each "Allow?": "Click Deny if it's wrong. Nothing moves, and tell me what to change."

**What I decided**
- The yes comes from Claude Code's "Allow?" prompt. The terminal version is too technical for the
  owner.
- Keep the MCP server. It holds the only key to the files, has no delete, keeps the "Allow?" line in
  plain English, and runs the same rules every time. Claude alone is more flexible, but the server
  wins on everything that could lose a paper.
- Add four server improvements, about 6 hours in all: a plain-English "Allow?" line, find a paper, a
  double-drop catcher, and a money snapshot on the Job Sheet.
- Add the chat as a second way in, about 2 hours. At the PC the owner can drag papers into the chat,
  and the server copies them from the chat's drop folder or from Downloads, Desktop or Documents,
  never moving or deleting the original. The Inbox stays for the phone.
- Keep the server connected the way it is: it starts by itself with the plugin. Claude laid out the
  two kinds of URL connection. A URL server on my PC works, but it adds nothing and someone has to
  start it first. An online custom connector could reach the Claude phone app, but it can't see the
  binder folder on my PC. It would need Google Drive's online access and a public address, which
  makes it a separate, much bigger build.

**Commits:** "Block 4a: the desktop app won't show the server's box; the yes moves to Claude Code's
Allow prompt", then "Record the chat-drop tests and add the chat as a second way in", then "Block 4a:
the Allow prompt asks in a fresh chat; Deny stops the tool"

---

## Sep 23, 2026 · Block 4b: "set up my binder" (step 4)

**What I asked for**
> "Please fix that now, and after, build set up my binder."

When Claude showed its plan:

> "The folder structure doesn't align with what we originally had. Please look at that and make sure
> that's right."

> "I want to work completely out of the Drive folder, please. No practice needed off of E. Let's just
> remove that folder."

**What Claude built**
- **Checked its plan against the original binder** (section 7 of the Binder doc) and found what it
  had left out: the Read Me First and All Jobs pages, and the move log and job facts in the Logbook.
  It explained that the Henderson folder in the original picture is an example of one job, made when
  that job starts.
- **Moved the work to my Drive.** The empty E: practice folder went to the Recycle Bin, and the
  plugin's binder setting now points at the Drive `R&E Binder` (the path lives only in my settings).
- **The fence** (`server/binder/safety.py`): every path the server touches is checked first. It finds
  where a path really leads, so a "..\" or a shortcut folder can't lead out of the binder, and it
  refuses a binder folder with any other name.
- **The builder** (`server/binder/setup.py`) and the `setup_binder` tool: they make the Inbox's Read me,
  Jobs, Finished Jobs, Truck & Shop, Archived (with Truck & Shop), and the Logbook (Job Facts, Move Log,
  Settings), plus Read Me First (Word) and All Jobs (Excel) as placeholders. They only create:
  anything already there is left exactly as it is, and nothing is moved, changed or deleted.
- **The skill** (`skills/binder-setup/SKILL.md`): what Claude does when I say "set up my binder": say
  what's about to happen, run the tool, show me the binder in plain words, and tell me my next step.
- **Test checks** (`server/tests/test_setup.py`), run in throwaway folders, never my Drive.

**How we checked it**
- 15 of 15 checks pass, without Claude. The builder makes the whole binder in an empty folder, and a
  second run changes nothing (every file's fingerprint and time stamp is the same). It keeps a
  hand-made Inbox and the paper inside it, never overwrites a page, and leaves a file in the way alone
  while building the rest. The pages open and say the right things. The real server, started the way
  Claude Code starts it, offers only its two tools, builds the binder twice with the right reports,
  shows no box of its own, and refuses a wrongly named folder without touching it.
- **The fence was tested by attacking it.** A shortcut folder planted inside the binder and pointing
  outside was refused, and nothing was written outside. With the fence switched off on purpose, those
  checks failed, which proves they really test it.
- The live run on my Drive happens in a fresh chat, because the server only picks up new tools when a
  chat starts.

**What I decided**
- Read Me First and All Jobs appear now, as placeholders: Word and Excel, so they open in the Drive app
  on a phone and All Jobs can be sorted.
- Each job's own folders (Job Overview, Job Sheet, folders 1 to 8) come at step 7, when I start a job.
- Work only in the Drive binder. No practice folder.

**Commit:** "Block 4b: setup_binder, its fence and the binder-setup skill"

### The live run on my Drive (fresh chat, Sep 23)

**What I asked for**
> "Set up my binder."

Then, playing the owner:

> "I just filed something in the inbox in Google Drive. Please file it for me."

> "I just put a random HEIC photo in. Obviously, it's not like a receipt or anything. Let me know if
> you can move it and do anything with it whenever I put it in the drop box."

**What happened**
- **Setup worked on the real Drive binder.** The server made 12 things (Jobs, Finished Jobs, Truck &
  Shop, Archived with Truck & Shop, the Logbook with Job Facts, Move Log and Settings, Read Me First,
  All Jobs, and a Read me in my Inbox). It kept the Inbox I had made by hand, exactly as it was.
- **The second run changed nothing:** "Your binder was already set up, so nothing changed."
- **A read-only look matched the picture.** Claude only searched for files; it never ran a command
  inside the binder.
- **A PDF sent through Drive was read right.** I dropped the practice certificate of insurance into the
  Inbox. Claude read it (Sample Mutual, C-26-8841, holder Dana Henderson, 412 Oak St) and said it goes
  in Henderson › 5 Insurance, a protected folder. That matches the answer sheet.
- **It wasn't filed, and that's correct.** Filing isn't built yet and the Henderson job has no folders
  until step 7. Claude isn't allowed to move papers itself, so the paper stayed in the Inbox.
- **An iPhone photo couldn't be read.** My phone saves photos as HEIC, and Claude's reader can't open
  that format. That was the finding the plan said to write down, and it became the next block.
- **Nothing happens by itself when a paper lands.** Nothing runs in the background (rule 7): I ask,
  Claude reads and suggests, and I click Allow.

**Commit:** "Block 4b live run: the binder built on Drive, a PDF read right, iPhone photos can't be read"

---

## Sep 23, 2026 · The photo converter: iPhone photos become JPGs (step 2)

**What I asked for**
> "When photos are uploaded and it is in HEIC format, I want a converter to make that .jpg and archive
> the HEIC version."

**What Claude built**
- **The converter** (`server/binder/photos.py`) and the `convert_photos` tool. For each iPhone photo in
  the Inbox it makes a JPG next to it, turned the right way up. It opens the JPG back to check it came
  out right, and it never writes over a file: if the name is taken, it uses "IMG_2572 (2).jpg".
- **It only creates.** The original stays in the Inbox exactly as it was, so it doesn't need an Allow.
- **The pair goes in the Move Log:** the photo's name, its fingerprint and its JPG. Filing will use
  that to know which original goes with which JPG, and a second run uses it to know a photo is done.
- **A new folder, Archived › Phone Originals,** added to setup. Running setup again makes only that
  folder.
- **The server's own Python** now includes a HEIC reader (`pillow-heif`), installed by the launcher the
  next time the server starts.

**How we checked it**
- 26 of 26 checks pass, without Claude: the 15 from before plus 11 new ones, all with fake iPhone photos
  made from a practice receipt, in throwaway folders. They show:
  - the JPG opens, the original's fingerprint and time stamp don't change, and the Move Log gets the
    pair
  - a sideways photo comes out upright
  - a second run changes nothing
  - a JPG already there is never written over
  - a PDF, a JPG and a fake "HEIC" that isn't a photo are all left alone
  - a missing Move Log means hands off
  - an Inbox that secretly leads outside the binder is refused
  - the real server converts through `convert_photos` and shows no box of its own
- **One check caught a real bug** before anything shipped. Two copies of the same photo got only one
  JPG, because the converter matched on the fingerprint alone. Now it matches on name and fingerprint,
  so each copy gets its own JPG, and catching the double drop is left to filing.
- **The guards were switched off on purpose** (the fence, and "never write over"), and their checks
  failed, which proves they really test them.
- A full-size JPG made from a fake 12-megapixel iPhone photo opened in Claude's reader, and the receipt
  was readable ($784.74, as on the answer sheet).
- The live run on my Drive happens in a fresh chat, because the server only picks up a new tool when a
  chat starts.

**What I decided**
- **No extra click for a photo.** Making the JPG doesn't ask, because it only creates. The original
  moves to Archived › Phone Originals under the same Allow that files its JPG, so the owner never clicks
  twice for one paper. Until filing is built, the original and its JPG both sit in the Inbox.
- **Originals go to Archived › Phone Originals**, one place for every original photo, whatever the job.
- It runs when I ask Claude to read or file the Inbox, not the moment a photo lands, because nothing
  runs by itself (rule 7).

**Commit:** "Photo converter: iPhone photos (HEIC) get a JPG Claude can read"

### The live run on my Drive, and step 2 finished (fresh chat, Sep 24)

**What I asked for**
> "Read my inbox."

Then, playing the owner, after photographing a fake receipt on my PC screen with my iPhone and
uploading it to the Inbox from the Drive app:

> "I just uploaded a photo."

**What happened**
- **Setup, run again, made only the new folder:** Archived › Phone Originals. The other 13 things were
  left exactly as they were.
- **My personal test photo got its JPG:** `IMG_2572.HEIC → IMG_2572.jpg`. Claude opened the JPG, which
  it couldn't do with the HEIC the day before. It's my own photo, so Claude didn't describe it, and
  nothing from it went in the repo.
- **A second run made nothing new:** "Already done, left as they were."
- **Step 2, the real test:** my phone photo arrived in the Inbox as `IMG_5684.HEIC`, full size
  (4284 × 5712). The converter made its JPG, and Claude read the receipt through a photo of a screen:

  | | Answer key | What Claude read |
  |---|---|---|
  | What it is | Supply-house receipt: shingles and materials | Riverbend Building Supply sale: shingles, underlayment, nails, drip edge |
  | Total | $784.74 | $784.74 (subtotal $715.49 + tax $69.25, and the math checks) |
  | Paid how | Charged to account | Charged to account, Sample Roofing Co. |
  | Job | Henderson, 412 Oak St | Job/PO: Henderson - 412 Oak |
  | Where it goes | Henderson › 4 Bills & Receipts | Henderson › 4 Bills & Receipts |

- **Nothing was filed,** and that's correct: filing isn't built. Both photos and their JPGs sit in the
  Inbox with the certificate of insurance until then.
- **The phone-to-Inbox route works end to end:** snap it, upload it from the Drive app, ask Claude to
  read the Inbox. Nothing ran until I asked (rule 7). That passes step 2's "done when": Claude reads
  a real receipt photo out of the Inbox and correctly says what it is.

**Commit:** "Step 2 done: an iPhone photo sent through Drive is converted and read right"

---

## Sep 23, 2026 · Tidying the repo, how it's packaged, and the road map

**What I asked for**
> "For our GitHub repo, let's organize it a bit. … Let's just make one skills folder, and then within
> that skills folder, we'll have all the skills that our agent could possibly use, and then we'll have
> an agents folder, and then we'll have our folders with hooks and rules. … The docs will have
> documentation, evals for the fake pieces of paper or documents, and then we'll keep the server there.
> I just want to clean our repository up a bit more so it doesn't overcomplicate things for someone to
> read."

> "I will write or you will write a doc that basically states how this is set up for the owner and how we
> packaged it for him. … We want to make this as direct and not tech jargon as much as possible."

> "Can we also make a change to the lifecycle HTML/artifact? Instead of steps, let's make it into a
> flowing diagram that is intuitive and in sync with our progress, so I will know what to do next time
> I load this session. Also please prepare a handoff just like we did before, with a diagram to show
> progress and what tasks are left."

**What Claude built**
- **Checked the plugin rules first**, so the tidy-up wouldn't break the package:
  - each skill must sit in its own folder, so `skills/binder-setup/` was already right
  - `.claude-plugin/` and `.mcp.json` must stay at the top
  - any `.md` file in `agents/` loads as a helper
  - a plugin can't carry the Allow list
- **The new layout.** `skills/` and `server/` stayed. `agents/` shows now, with only a hidden
  placeholder. New `guardrails/` folder. `eval/` became `evals/`. The log became
  `docs/directors-log.md`. Every move kept its history.
- **`guardrails/rules.md`:** the 8 rules in plain words, each with how it's kept and whether it's been
  tested. Claude's brief now pulls them in from there, so they live in one place.
  **`guardrails/always-ask.json`:** the Allow list the owner's settings need.
- **`docs/how-it-works.md`:** how the binder is set up and packaged for the owner, in plain words. It has:
  - a picture
  - what's in the package and the job each piece does in the binder
  - what happens when he says "set up my binder" or "read my inbox"
  - how it's installed on his PC, step by step, with who does each step
  - honest limits
- **The README** got a folder map and links, and its Guardrails section now points at the rules.
- **The lifecycle page became a road.**
  - The 26 steps sit on one winding path from the assessment to the finish line: rows on a computer,
    straight down on a phone.
  - Done dots are filled, a pin marks where we are, and clicking a dot opens it to tick or add a note.
  - A "Next time, type this" card at the top reads a note that Claude updates at the end of every
    session, so the page always says what to do next.
  - The ticks carried over.

**How we checked it**
- 26 of 26 server checks still pass after the moves.
- No old folder names are left in the repo, and every link in the README and the new docs leads to a
  file that exists.
- The page was published to the same link (version 5), and its store still holds the four ticks. It was
  looked at on a local copy with tonight's real progress, at phone width and computer width, in dark
  mode.

**What I decided**
- One `guardrails/` folder for the hooks and the rules.
- The folders that aren't built yet show now, empty.
- `eval/` becomes `evals/`.
- Docs get plain names and there are fewer of them: `how-it-works.md` replaced the planned "01 how it
  works", and the other planned docs are decided when their part comes.
- Instead of a list of steps, the lifecycle page is a flowing map that stays in step with our progress
  and says what to type next time.

**Commit:** "Tidy the repo: guardrails, evals, plain doc names, and how it's packaged for the owner"

---

## Sep 24, 2026 · The phone route: filing from the Claude app on the phone (step 5)

**What I asked for**
> "Try the phone route."

Then, as the owner, from the Claude app on my phone, with a photo of a fake deposit receipt attached:
> "Where does this go?"

**What Claude built**
- **Nothing new. This step was a test and a decision.** Step 5's goal: a clear yes or no, written
  down, on whether photos sent from the phone can be filed.
- **Research first.** Claude read the Claude Code docs on the mobile app and Remote Control. A helper
  agent's summary said "Allow?" questions don't reach the phone, so Claude checked the docs itself and
  found the opposite: they are sent to the phone and stay open until answered. The docs also said a
  phone photo is saved on the PC, but not what kind of file it is.
- **A test plan with four questions:** does the photo land on the PC as a file, can Claude read it, does
  "Allow?" show on the phone, and what would filing from there need. Remote Control was already on for
  this chat, so there was nothing to set up.

**How we checked it**
- Claude opened the fake handwritten deposit receipt on my PC screen. I photographed it in the Claude
  app on my iPhone and sent it to this chat.
- **It arrived as a file:** a JPG, 1932 × 2576, 1.8 MB, with no location data, in the uploads folder,
  in a folder named for this chat. The name was changed to a code plus `image.jpg`. So the Claude app
  sends a smaller, re-saved copy, not the iPhone's HEIC original, and no converting was needed.
- **Claude read it right:** receipt No. 0212, $4,000.00 from Dana Henderson, check #1042, deposit for
  412 Oak St → Henderson › 2 Payments. That matches the practice answer key.
- **"Allow?" showed on my phone** all three times. I tapped Allow twice and the test tool ran; I tapped
  Deny once and it was stopped ("Denied by user").
- **One difference from the PC:** on Sep 23, a Deny at the PC ended Claude's turn. From the phone,
  Claude could keep talking after the Deny. Explaining Deny before every "Allow?" still works either
  way.
- No "always allow" rule was saved; the always-ask rule is still in my settings. Nothing was filed or
  copied into the binder, and the photo stays out of the repo.

**What I decided**
- **The test as planned:** the deposit receipt, then Allow and Deny from the phone.
- **Both phone routes can file (option C).** The owner can upload to the Inbox with the Drive app, or send
  a photo in the Claude app. For the second, the server may copy from the folder where phone photos
  land, like a paper dropped in the chat at the PC. Rule 5 now says so. It's built into the filing
  tool at step 9, about 1 hour more.
- **The honest limit:** filing from the phone still runs on my PC, so the PC has to be on with the
  Claude app open.

**Commit:** "Step 5 done: phone photos reach the PC and Allow works from the phone; Part 1 finished"

---

## Sep 24, 2026 · The switch: our server retired, and everything made simpler (step 6)

**What I asked for**
> "So instead of this limitation, can we also include the ability to use this from Claude chats?"

> "I don't really think it's that impressive that we have an MCP server that does Google Drive stuff
> when there is already a connector built out for that. Don't you think it will be better if we just
> develop specific skills, agents, guardrails, our test evals and docs? We can use guardrails as hooks and
> rules."

> "The goal is to make this as user friendly as possible for him, and we want it to be so easy he will
> use this all the time to help with organization."

> "I want all of it to be easy enough a 13-year-old would understand, but we do the developing regarding
> the skills, agents, guardrails, etc." … "It would mostly be chat though."

> "Go through our project files, trackers, everything, even the GitHub repo, and simplify everything and
> change things accordingly."

> "Turn the lifecycle HTML into a dashboard with tasks that are specific and easy enough for me to
> understand. You will update it every time we finish a task, and it will be yellow for what task we are
> working on."

> "Also remember we need the skill: when we say we are starting a new job, it will create a folder
> structure inside Jobs under that job, with the structure we wanted."

**What we found first**
- **A regular Claude chat on my phone, with Google's Drive connector, read a receipt straight from the
  Inbox with the PC out of the picture:** the Riverbend receipt, $784.74, every line right. It couldn't
  read the iPhone's HEIC copy.
- **A photo attached in a regular chat can't be saved into Drive.** The connector needs the file typed
  out as text, and a 2.3 MB photo is about 3 million characters. Nothing was saved.
- **From the docs:**
  - the connector can make folders, move, rename, copy, share and trash
  - it asks before moving, sharing or trashing
  - it can't edit what's inside a file
  - hooks can stop any tool or force an "Allow?", including the connector's tools, and they ship inside
    the plugin
  - hooks and helper agents only run in the Code tab
- **A check of every file:**
  - the old server was described in about 55 places in the tracker, the page and the README
  - `CLAUDE.md` was 426 lines
  - the folder map was copied in 6 places

**What Claude changed**
- **Repo:**
  - Removed the server, its tests and the Allow list.
  - Made one folder map (`skills/binder-setup/references/folder-map.md`), and rewrote the setup skill for
    the connector.
  - Rewrote the rules, how-it-works and the README so a 13-year-old can follow them.
  - Cut `CLAUDE.md` from 426 to 154 lines.
  - Plugin version 0.4.0.
- **The Binder doc:**
  - Cut to 21 steps (Part 1 kept as history).
  - New rules, words, maps and "done when".
  - The Showcase section folded into "Done when".
  - A journal row.
- **The dashboard:** it replaced the winding-road page, at the same link.
  - All 61 tasks: green when done, yellow for the one we're on.
  - Progress by part, what's waiting on me, the big decisions, and test results.
  - Claude updates it after every task, without republishing.
- **Around the project:**
  - Removed the old Allow-list entries from my Claude settings.
  - Marked the four old plans "superseded".
  - Updated `D:\CLAUDE.md` and Claude's memory.
  - Rewrote my resume's Binder bullet and rebuilt that resume. It's still one page.

**How we checked it**
- No repo page describes the server as current. Only this log's history and the "retired" notes mention
  it.
- 0 broken links in the README, `CLAUDE.md`, the docs, the rules and the skill.
- The package files are valid, and the server and `.mcp.json` are gone.
- The Binder doc opens with 21 steps and 11 sections.
- The dashboard's data has 21 steps and 61 tasks, with exactly one task yellow at a time.
- **Cleanup:** the old server was still running in the session, so Claude stopped it and sent its Python
  folder (132 MB) to the Recycle Bin. At my request, my personal photo also went from the Inbox to the
  Recycle Bin.
- **Each part on the dashboard** now says, in plain words, what we're doing and why.

**What I decided**
- **Retire our own server.** Google's Drive connector does the moving; we build the skills, three
  read-only helper agents, guardrails (rules and hooks), the scored test and the docs.
- **Where the owner works:** mostly a regular Claude chat. The Code tab too, keeping chat drop, where a
  dropped paper is copied into the Inbox after Allow.
- **Keep the evals.** Cut the plan to 21 steps. Keep `How His Jobs Run.html`. Simplify first, then test.
- **Put a photo straight into a chat, then filed, in the product** if step 7 proves it works.
- **Starting a job** makes the job's full folder set inside Jobs, from the one folder map.
- **A dashboard,** updated after every task, with the current task in yellow.

**Commit:** "Step 6: retire our server for Google's Drive connector, simplify everything, add the dashboard"

---

## Sep 25, 2026 · Proving the connector route (step 7)

**What I asked for**
> "Prove the connector route."

### Check 1: how does a regular chat ask before a move?

**What Claude set up**
- A throwaway `Connector Test` folder in my Drive, with one fake paper (`Invoice 5521 - Haul-Away.pdf`)
  and an empty `Move Here` folder inside it. Claude checked through the connector that all three had
  reached Google Drive online before I started.

**How we checked it**
- As the owner, in a regular Claude chat on my phone, I asked Claude to move the invoice into `Move Here`,
  then back, with a Deny in between.
- **It moved both ways, but nothing asked me.** No Allow and no Deny showed at any point.
- **Why:** my Google Drive connector is set to "always allow". So Google's "ask before moving" is only
  a setting. The owner could switch it off the same way, and nothing would ask.
- Claude checked Drive afterwards: the invoice is back in `Connector Test`, where it started.
- **Not done yet:** looking at the connector's settings on claude.ai, to see which actions can be set
  to "ask" or "blocked". Chrome was open, but the Claude extension wasn't connected, so this waits.

**What I said**
> "So it worked, but it did not ask me the Allows for any of the steps. It just did it automatically. I
> have everything set up for the MCP connector for Google Drive to 'always allow'. Our gates should
> always prompt these with the AskUserQuestion tool. That needs to be a rule."

**What Claude changed**
- **Rule 1 rewritten** (`guardrails/rules.md`): before Claude moves, renames or copies anything, it asks
  a question the owner taps (what the paper is, where it's going, then Allow or Deny). Only Allow lets it
  happen. It asks every time, even when Google Drive is set to "always allow".
  - In a chat, it asks with the chat's tap-to-answer buttons. That's Claude following a rule, not a lock.
  - In the Code tab, it asks with the AskUserQuestion box, and a hook is the lock.
  - Deleting and sharing never happen at all (rules 3 and 5), so rule 1 covers moves, renames and copies.
- **Stopped counting on Google's ask** everywhere it was mentioned: `CLAUDE.md`, the README,
  `docs/how-it-works.md`, the Binder doc's rule and word list, and the dashboard's "How the Binder
  works".
- "Still open" question 1 is now: which extra locks does a chat get, on top of our question? (step 12)

**What I decided**
- **The Allow question covers moves and changes only.** Making an empty folder doesn't ask.
- **Google Drive's own setting as a second lock:** decided at step 12, "the guard". For now it stays on
  "always allow", so our question is the only gate. That's the honest test of the rule.
- **Claude can look at my connector settings in Chrome,** look only, when the extension is connected.

**Commit:** "Step 7, check 1: Google's ask can be off, so Claude's own Allow question is now rule 1"

### Check 2 turned into a skill: "start a job" (pulled forward from step 9)

**What I asked for**
> "Why don't we make this into a skill? This needs to be a skill that we can use to create these
> folders, instead of saying all this stuff."

Claude had given me a long message to paste, naming all 8 folders. I chose to build the skill now, and
to make the first job the practice job, Henderson, in the binder itself.

**What Claude built**
- **`skills/job-organizer/SKILL.md`**, its first part: "start a job". I say "start a job for Henderson,
  412 Oak St" and Claude makes:
  - `Jobs/2026 Henderson - 412 Oak St/`, with a Job Overview page (customer, address, phone, notes) and
    the 8 numbered folders
  - a matching empty folder in Archived
- The names come from the one folder map, so nobody types them.
- No Allow is needed, because it only makes folders (rule 1).
- If the address is missing, it asks for just that. If the customer or street is already in Jobs or
  Finished Jobs, it stops and asks if it's the same job.
- Filing, finding, "how's the job?", undo and closing come later, in the same skill.
- The plugin went to version 0.5.0. The copy installed in my Code tab was still 0.2.0, from before the
  switch, so Claude updated it.

**How we checked it**
- **Without the skill first,** to see what goes wrong. Asked to start the Henderson job, Claude:
  - left the year out of the name
  - made none of the 8 folders and no Archived folder
  - made up a "Job Tracker" sheet and promised to keep it updated, which the connector can't do
  - told me to put papers straight into the job's folder, not the Inbox
- **With the skill, three dry runs** (plans only, nothing made): a normal new job, a missing address,
  and a customer whose 2025 job is in Finished Jobs. All three came out right: the full set, one short
  question, and "is this the same house?" with nothing made. One gap showed up: details I mention, like
  "hail damage", weren't kept. The skill now puts them in the Job Overview's Notes.
- **Two live runs on my Drive,** by a fresh copy of Claude using only the skill and Google's connector:
  - **First run:** 15 steps, 11 things made in about 26 seconds, every name spelled right. Claude checked
    the Drive itself afterwards.
  - **Second run:** it found the job, made nothing, and said "Henderson's job was already set up.
    Nothing changed."
- **Added to my Claude account:** once the Claude extension in Chrome was connected, Claude packed the
  skill into a zip with the folder map inside (a regular chat can't see files outside a skill), and
  uploaded it at Customize → Skills. It showed as "job-organizer v1", switched on. Skills work on every
  Claude plan, even Free, as long as "Code execution and file creation" is on (it was).
- **The regular chat test:** in a new regular chat I typed "start a job for Martinez, 27 Maple Ave",
  then "start a job for Henderson, 412 Oak St". It worked just as described. Claude checked the Drive:
  Martinez got all 11 things in about 22 seconds, and nothing new was made for Henderson.
- **My connector settings, looked at only:** each of the connector's 11 actions can be set to Always
  allow, Needs approval or Blocked, and all 11 are on Always allow. There's no separate "move": moving
  and renaming go through "Update file". "Needs approval" is skipped in chats set to "Automatically
  approve". An idea for step 12: set Share and Trash to Blocked, a real lock for rules 3 and 5 even in
  a chat.

**What I decided**
- Starting a job is a skill, built now instead of at step 9.
- The first job is Henderson, in the binder. It stays, for filing at step 10.

**Commit:** "job-organizer skill: "start a job" makes a job's full folder set (pulled forward from step 9)"

### Checks 3 and 4, and step 7 closed

**What I said**
> "I think we're doing a lot too much testing. ... All the stuff we can just test within our PC. We
> don't really need our phone for anything else. We just need to do the setup, and then he'll be able
> to use it on his phone no matter what, because it'll be synced."

**What Claude checked**
- **Check 3 (a paper scanned with the Drive app):** no test needed. Google's connector says in its own
  description that it reads PDFs, and the Drive app's Scan makes PDFs.
- **Check 4 (a photo sent in a regular chat):** Claude ran it in my Chrome on the PC.
  1. The chat made a PDF from a fake gas receipt photo, named from what was on it.
  2. The PDF's menu has "Open in Google Drive". One click put it at the top of My Drive, with no
     permission prompt.
  3. The chat then moved it into a folder.

  Claude confirmed each step in Drive.
- **My connector settings, looked at only:** each of the 11 actions can be Always allow, Needs approval
  or Blocked, and all are on Always allow. Moving is done by "Update file".
- **The Code-tab lock (check 5)** moved into the finish plan's workstream W6. Claude removed the
  throwaway test lock.

**Step 7's answer:** the connector route works.
- Claude asks before moving (rule 1).
- Starting a job works in a chat.
- Scans can be read.
- A photo sent in a chat can be filed with one click.

---

## Sep 25, 2026 · The finish plan, and my guardrails

**What I asked for**
> "Let's just make a plan first. I want to get this done as fast as possible, and then you will teach
> me how to use it and how it works, and then I'll teach the owner. ... We want to break it into tasks, and
> we can break it into sub agents that create other skills. But I will be the director and commander
> for everything, and you will stop and ask me what I would want in each situation."

> "Please also still talk to me about the guardrails, such as we shouldn't ever touch insurance files.
> Please interview me and make sure we get those rules down and set."

**What Claude did**
- **Research by two helper agents**, from the official docs:
  - claude.ai plugins can be added from a public GitHub repo or a zip, on Pro or Max.
  - "Install this repo" typed in a chat can't install anything, so Claude does it through Chrome or
    the Code tab.
  - A plugin can leave out the test files by living in its own folder.
  - Scheduled tasks exist, but I chose on-demand.
  - Plus the HEIC options.
- **A plan** built with a planning agent: 5 skills, 10 workstreams, 6 waves, and about 14 hours of
  wall-clock. It's saved in the plan file named in `CLAUDE.md`.
- **Three rounds of questions, then a guardrails interview.** My answers are the new rules
  ([`guardrails/rules.md`](../guardrails/rules.md)).
- **Wave 1, started the same day:**
  - The repo now holds the owner's package in `plugin/`, the one copy of the shared pieces in `shared/`,
    and `tools/` to copy, check and pack.
  - The dashboard was re-planned: steps 8 to 20 are the new plan.
- **Cleanup**, when I said "just clean it all up and start anew":
  - The test lock was removed.
  - The old binder was renamed "R&E Binder (lab Sep 24)" and kept. Nothing was deleted.
  - The test folder was archived inside it.

**What I decided**
| Topic | My call |
|---|---|
| Install | A public GitHub repo, added as a Claude plugin. Needs Pro or Max |
| Public repo | Anonymized: no real client or business names. A clean new repo |
| Skills | 5 separate skills |
| Filing a pile | "It should first present to the owner where the files are going to go. The owner can say or make changes, but after that, one tap moves them directly to where it says." |
| Job tracker | A fresh copy after each change; the old ones archived |
| Secretary | Only when asked: missing papers, money reminders, dates and stuck jobs |
| Code tab | An optional extra: the hard lock and helper agents |
| Evals | About 30 papers, in the repo only |
| iPhone photos | Claude converts them only to read them; the original is filed, renamed |
| Chat lock | Rules only; Google's connector settings stay on Always allow |
| New job on a paper | Offer to start it on the list |
| Duplicates | Archived, as a line on the list |
| Finished jobs | Filed, marked on the list |
| Unsure papers | Stay in the Inbox with one question; never a guess |
| File names | A standard name on filing |

**My guardrails (the interview):**
- **Insurance and the other legal papers** (estimates, permits, invoices and lien waivers,
  warranties): "You can move them around and file them, but never change the contents. It will only be
  read-only within the file."
- **Never delete. Never share. Never contact anyone.**
- **Sensitive details:**
  - last 4 digits only
  - no numbers in file names or the tracker
  - personal papers left alone and not described
  - nothing copied out of the binder
- **Legal papers can be moved later** with a tap, to fix mistakes.

**The first early test (U1): can a regular chat read an iPhone (HEIC) photo from Drive?** No.
- The connector sent the 5 MB photo back as text, and it was cut off.
- Nothing arrived in Claude's workspace, and nothing in Drive changed.

My call: "send it here" plus prevention. Setup turns on the iPhone's "Most Compatible". If a HEIC still
shows up, Claude asks me to send that photo in the chat, reads it, and files the original. At the PC,
it's automatic.

**Commit:** "Finish plan, wave 1: plugin/ + shared/ + tools/, guardrails v2, dashboard re-planned"

---

## Sep 25, 2026 · Wave 2: five skills, the lock and the test pile, built in parallel

**How it was built** (the part I'm directing):
- **"Before" tests first.** Five plain copies of Claude, with no skill, tried each job on the same fake
  binders. Their failures became each builder's to-do list.
- **Seven builder agents ran in parallel:** one per skill, one for the Code-tab lock and helpers, and
  one for the test pile. Each could only edit its own files.
- **The lead** (Claude in my session) fixed the shared rules they reported, ran the checks, and
  committed.
- **"After" tests:** four fresh copies of Claude used only the finished skills, with no hints.

**What the "before" and "after" tests showed:**

| Skill | Without the skill | With the skill |
|---|---|---|
| Setup | Built no binder folders; invented project files; renamed my old binder without asking | All 11 items built; the old binder never touched; saying it twice changed nothing |
| Close a job | Missed the unpaid $9,950 invoice and the missing Haul-Away lien waiver; moved a job without asking | Named exactly those 2 gaps, then asked one Allow |
| Filing | Names drifted; no legal marks; a big table | Clean names; legal marks; a phone-friendly list; one tap; my change handled |
| Undo | Offered to delete a folder | Never deletes; one list, one tap; a fresh tracker |
| "What am I missing?" | 5 of 8 gaps; 1 false alarm; searched outside the binder; offered to text a customer | **8 of 8 gaps**, no false alarm, stays in the binder |
| Code-tab lock | — | 25 of 25 tests; it fails closed |

**Other things built:**
- **The Code-tab lock:** one tap lets exactly N moves through for 15 minutes. Delete, share, copy, and
  writing into the binder's files are always blocked. It blocks if anything goes wrong.
- **3 read-only helper agents:** a paper reader, a filing checker and a job checker.
- **2 scripts:** the iPhone-photo reader, and dropping a paper into the Inbox.
- **The answer key** (32 papers, 8 tricky), written before any paper existed.
- **The paper maker and the scorer.** The scorer caught both planted mistakes in its test.

**What I decided (the decision round):**
- **Approved as written:** the Read Me First and key phrases, the filing list, the close-a-job
  message, and the "what am I missing?" reply.
- **The answer key:** approved, with Okafor as the third job and Brooks as the new customer. The 32
  fake papers are made.
- **Mixed clues on a paper:** ask. **Lien waivers:** only from suppliers he owes. **Amounts that don't
  add up:** not flagged.
- **I asked:** "Wait, so I will use the evals as a test, but everything else will be built. Is that
  right?" Yes: the evals are only for testing and the numbers, never in the owner's package.
- **On the lock:** "Writing is okay, but what could you even write or organize? What about notes for
  him if he ever asks?" So I added notes: "add a note to Henderson: ..." makes a dated note in the
  job, a new file each time, never an edit.
- **Python:** "We'd include that as a dependency, so he installs it as well." Python and the
  iPhone-photo reader are installed before the plugin in the Code tab. pillow-heif is now on my PC.

**Commits:** "Wave 2: five skills, the Code-tab lock, helpers, scripts, answer key and scorer", "After-tests:
tighten the checklist, secretary, setup, filing and lookup wording", "Bryant's decision round: texts
approved, answer key approved, scored papers made, notes, Python"

## Sep 25 and 26, 2026 · Waves 3 to 5: live checks, breaking the lock, and the scored runs

**How it ran** (the part I'm directing):
- **I played the owner** in a regular Claude chat for the live checks, while Claude checked every result
  in my Google Drive. Halfway through I said "you do all the testing": from then on Claude drove my
  regular chat through Chrome, typed the lines, tapped Allow where the plan said to, and checked
  itself in Drive and in the chats.
- **Every change to my Claude account** (replacing the plugin) was asked for first. I said yes once
  for the rest of the day, and Claude told me each time it happened.

**Live checks: all passed**

| Check | Result |
|---|---|
| Install, setup, start a job | The plugin on my account and in the Code tab; setup made all 11 items; Henderson started |
| File a pile | 9 of 9 papers right, with the gas receipt left in the Inbox as I asked |
| Deny, find, job status, "what am I missing?" | Deny moved nothing; the lien waiver found with a link; a 5-line status; the one real gap named |
| Undo, close a job | All 9 papers back with their old names; Henderson closed into Finished Jobs, with the 7 missing papers named |
| iPhone photo | Asked me to send it; spotted it as a duplicate of a filed receipt; archived the original with its .HEIC name |
| Photo sent in a chat | An exact copy (same bytes), saved with "Open in Google Drive", filed in Truck & Shop |

**Trying to break the Code-tab lock:** trash, writing into the binder on my PC (Bash, PowerShell and a
sneakier way) and a helper's move were all blocked. Reading the lock's code, Claude found 2 gaps a
tester could use: a paper renamed like an old tracker could move with no tap, and any new file got
through, even a PDF. **I said fix both now:** 0.7.1, with tests written first and watched failing.

**What the checks found, and what got fixed**

| Found | Fixed in |
|---|---|
| A regular chat now has its own tap buttons, and once asked "Move this 1?" before showing where the receipt would go. I asked: "fix whatever we need to fix to make sure it doesn't skip a step again" | 0.7.2: the list always comes first, typed in the chat, in every skill that asks |
| Google Drive renames a file saved from a chat (spaces become underscores) | 0.7.3: match it by date and name parts |
| The chat looked for the skill's rule files in the wrong folder, then read only the first page of the Inbox (5 of 32 papers). It stopped before moving anything | 0.7.3: every skill says where its files are and to read every page |
| In the Code tab, the Claude app synced a newer plugin mid-session, the old folder vanished, and the lock quietly stopped running. The skill still asked first, so nothing moved without my tap | 0.7.4, my pick "add a safety stop": no lock note after my Allow means nothing moves |

**The scored runs** (32 fake papers, 8 tricky, answer key written first; one line and one tap each):

| | Regular chat | Code tab |
|---|---|---|
| Right folder | 29 of 32 | **32 of 32** |
| Tricky papers | 8 of 8 | 8 of 8 |
| Papers changed or missing | 0 | 0 |
| Moves before my Allow | 0 | 0 |
| Time | 6 min 55 s | about 26 min |

The chat's 3 misses were roof photos that Drive's reader returns no text for: it asked which job
instead of guessing. The Code tab opened the photos on the PC. Details:
[the scored runs](../evals/results/2026-09-26-scored-runs.md).

**What I decided:**
- **Speed-ups:** Claude does all the setup, and my teaching is a 15-minute walkthrough.
- **Run 2 in the Code tab:** yes. Claude can't operate its own app, so I did 3 clicks.
- **Timing myself by hand:** skipped. So there's no "minutes saved" claim, only measured times.

**Commits:** "Lock 0.7.1: close the tracker-name and new-file gaps", "Plugin 0.7.2: the list always
comes before the question", "Plugin 0.7.3: every skill says where its files are and to read every
page", "Plugin 0.7.4: a safety stop when the Code-tab lock isn't running; scored runs"

## Sep 27, 2026 · Wave 6: the guide, the README, the teaching script and the public repo

**What I decided:**
- **the owner's guide:** one guide, not two. The Read Me First that setup puts in his binder is the guide,
  with 2 lines learned in testing (after Allow, photos sent in a chat need "Open in Google Drive"; answer
  Claude's questions in a word). `tools/print_guide.py` prints the same text on one page.
- **The README:** my first draft was too thin. I asked for "a diagram, very simple and more easy to read,
  like I wrote it", then "be more descriptive... exclude all fluff... explain more into what this is".
  It now opens with what the system is and what it's made of, with one diagram colored by who acts.
- **The public repo:** named `re-binder`. "R&E" stays, but the fake papers get a made-up city so the
  initials, the trade and the city can't point to the real company. A cleaned copy of my brief to
  Claude (`CLAUDE.md`) goes in, because it shows how I directed the work.
- **Publishing:** I approved it after the final scan came back clean.

**What Claude built:**
- `tools/export_public.py`: makes the public copy from the private repo (the name and city replaced, the
  fake papers re-made, private files left out) and stops if anything private is left. It also
  refreshes the public repo after a change. It never goes public itself.
- The teaching script for setting it up with an owner: 20 minutes, 6 parts, and what to do if
  something goes wrong.

**How we checked it:**
- The public copy passed every check on its own: 29 of 29 lock tests, 14 script tests, the papers'
  self-test and the scorer. The scan found 0 client names, cities, area codes, emails or private paths.
- **Installed from GitHub** on my account (Add marketplace → Add from a repository → Sync → Add). "Set
  up my binder" found my binder and made nothing. The README's install steps were corrected to the
  real clicks.

**Commits:** "Guide: 2 lines from testing, and a printable one-page copy", "README ...", "Teaching
script", "Public export: a script and a cleaned brief", "Install steps checked from GitHub". Public
repo: github.com/bryant5040/re-binder.
