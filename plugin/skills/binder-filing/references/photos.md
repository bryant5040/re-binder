# Photos and dropped files

Three ways a paper can come in as a photo or a file: an iPhone photo in the Inbox, a photo sent in
the chat, and a file dropped into the chat in the Code tab. He never sees this page.

## iPhone photos (HEIC) in the Inbox

**How to tell:** mimeType `image/heif` or `image/heic`, or a name ending `.heic` or `.heif`, in any
case. Google Drive's reader can't open them, so never call read_file_content on one.

**In the Code tab** (you can run commands on his PC):
1. Run `python "<plugin root>/scripts/heic_to_jpg.py"`. The plugin root is two folders up from this
   skill's folder. It prints the paths of upright JPG copies in a temporary folder, outside the
   binder.
2. Read each JPG. Its name starts with its photo's name: `IMG_5684.HEIC - 3f2a9c1b.jpg` is the copy
   of `IMG_5684.HEIC`.
3. The Inbox original goes on the list like any paper, renamed, its extension kept exactly:
   `2026-09-16 Receipt - Riverbend Supply - $784.74.HEIC`. The JPG is only for reading: never file,
   move or upload it. There's nothing to ask him.
4. No JPG for a photo, the script fails, or it says an add-on is missing: don't install anything.
   Do what a regular chat does for that photo.

**In a regular chat:**
1. The photo stays in the Inbox: `IMG_5684.HEIC: I can't open iPhone photos from Drive. Please send me
   that photo here in the chat.`
2. When he sends it, the Claude app sends a JPG you can read. It's only for reading: never save, copy
   or upload it.
   - One iPhone photo waiting: the photo he sends is that one.
   - Several: ask him to send them in the order you listed them. The list says which is which:
     `IMG_5684.HEIC (the first photo you sent)`.
   - Not clear if it's the Inbox photo or a new paper: ask.
3. Then a new Inbox round for the whole Inbox. Don't read again the papers you already read in this
   chat. The photo's line is the Inbox original, renamed, extension kept (or a "Duplicates" line if
   that paper is already filed). Then the tap, the Inbox listed again, the move, the Filing Record,
   the tracker, and "Done".

## Photos sent in a regular chat

A paper that isn't in Drive yet. (In the Code tab, a photo sent in the chat is a dropped file: see the
last part.) Each paper needs one "Open in Google Drive" click from him. For more than 5 papers, suggest
the faster way first: "For a big pile, it's faster to scan them into your Inbox with the Drive app,
then say "file my inbox"."

1. **Read each photo once.** Several photos can be different pages of one paper ("page 1 of 2", "page
   2 of 2"): that's one paper and one line.
2. **Match, name and check for duplicates** as in the Inbox round, against the names already filed. A
   paper that's already filed gets no line: "The Riverbend receipt is already in your binder, so I
   left it out."
3. **Type the list in the chat, then ask** ([the list](allow-list.md)). The list comes first, as your
   own message, even for one photo; the question comes after it. Only Allow or a clear yes goes on.
4. **Make an exact copy of each paper** in your outputs folder, so it shows in the chat as a file he
   can tap, with its standard name:
   - one photo: the photo file itself, unchanged, with its own extension (the phone app sends `.jpg`)
   - several photos of one paper: one PDF, one photo per page, in order, unchanged (img2pdf keeps
     them exact)
   - never crop, straighten, turn, brighten, clean up or re-type it
   - if you can't find the photo's file: "I can't save this photo from here. Please scan it into your
     Inbox with the Drive app, then say "file my inbox"."
5. **Tell him:** "Tap each file, then "Open in Google Drive". Say "done" when you have."
6. **When he says done,** find each file at the top of My Drive (`parentId = 'root'`), made in the
   last hour. Google Drive changes the name as it saves: spaces and symbols can turn into
   underscores, like `2026-09-26_Receipt_-_Cardinal_Hardware_-_35_60.jpg`. So match it by the date
   and the Who in its name (`title contains '2026-09-26' and title contains 'Cardinal'`, writing an
   apostrophe as `\'`), and by its type.
   - Exactly one fits: move it with update_file (`fileId`, `title` = its standard name, `parentId`)
     into its folder. His Allow already covers this: no second tap. A "New job?" line: start the job
     first.
   - None fits, or two do: ask once: "I can't find "<name>" in your Drive yet. Did you tap "Open in
     Google Drive" for it?" (or "I see two copies of "<name>". Did you tap it twice?"). Never guess.
   - There's no Inbox to list again here. Finding exactly one file for each line is the check.
7. **Then** the Filing Record (from folder: My Drive), the fresh tracker, and "Done: 2 papers filed."
   with one next step.

A file he just saved from this chat is the only thing outside the binder you may touch, and only to
move it in.

## A file or photo dropped into the chat, in the Code tab

1. Read it once, and put it on the list like any paper.
2. After Allow, copy it into the Inbox with `python "<plugin root>/scripts/drop_to_inbox.py" "<file>"`.
   Never copy it with your own file tools. The script prints the new file's path; its name may end
   in ` (2)` if the name was taken.
3. List the Inbox until that name shows up (Google Drive for desktop takes a moment). It showing up
   isn't a change to the list. Then move it as listed: the same Allow covers it.
4. Not there after about 2 minutes: "Your paper is in your Inbox. Google Drive is still bringing it
   in. Say "file my inbox" in a minute."
