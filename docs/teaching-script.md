# Teaching script: setting it up with the owner

About 20 minutes, sitting next to him with his phone. By the end, he has filed his first papers
himself.

**Bring:** the printed Read Me First, and 2 or 3 of his papers from this week. To print the guide, run
`python tools/print_guide.py`; it needs the packages in [`requirements.txt`](../requirements.txt).

## Before you meet (10 minutes, on your own)

| Check | Why |
|---|---|
| He has a Claude Pro or Max plan | Plugins need it |
| The Claude app and the Google Drive app are on his phone | He'll use both |
| You know which Google account holds his Drive | The binder goes in that Drive |

## 1. Install it (5 minutes): you drive, he signs in and taps OK

1. In Claude: **Customize → Plugins → + Add → Add marketplace → Add from a repository**. Enter
   `bryant5040/re-binder`, leave **Sync automatically** on so fixes reach him by themselves, and click
   **Sync**. Then find **Re binder** under **Discover** and click **Add**.
2. **Customize → Connectors → Google Drive.** He signs in to Google himself. Never type his password.
3. **Settings → Capabilities:** turn on **Code execution and file creation**.
4. On an iPhone: **Settings → Camera → Formats → Most Compatible**, so Claude can read his photos.

Tell him: "This lets Claude file your papers in your Google Drive. It can't delete anything, and it
never moves a paper until you tap Allow."

## 2. Set up the binder (3 minutes): he does it

He says **"set up my binder"**. Then open the Drive app together and show him the new **R&E Binder**
folder: the Inbox, Jobs, the Job Tracker and the Read Me First.

## 3. Start one real job (2 minutes)

He says **"start a job for [customer], [street]"**, using a job he's working on now. Show him the
job's folder and its 8 numbered folders.

## 4. File his first papers (5 minutes)

1. He scans 2 or 3 papers into **Inbox - Drop Here** with the Drive app (**+ → Scan**).
2. He says **"file my inbox"**.
3. Read the list together. Have him change one line, like "number 2 goes to Smith", so he sees
   he's in charge.
4. He taps **Allow**. Open the job's folders together: the papers are there, with clear names.

## 5. Ask it things (3 minutes)

- **"where's the [paper]?"**: Claude names the folder and gives a link.
- **"what am I missing?"**: Claude says what each job still needs.

## 6. Show him he's safe (2 minutes)

- He scans one more paper, says "file my inbox", and taps **Deny**. Nothing moves.
- He says **"undo that"** and taps Allow. His last filing goes back, with the old names.

## Leave him with one sentence

"Put papers in the Inbox, say 'file my inbox', check the list, tap Allow."

Leave the printed Read Me First in his truck. If he forgets a phrase, he can say "how does my binder
work?" and Claude shows it again.

## If something goes wrong

| He sees | What to do |
|---|---|
| "I can't open iPhone photos from Drive" | Send that photo in the chat, and check the camera is on Most Compatible |
| A paper stays in the Inbox with a question | Answer in a word, like "Henderson" |
| Claude asks which job a photo is for | Say the job. A photo of a roof has no text Claude can read |
| He tapped Allow on photos sent in the chat, but they aren't filed yet | Tap each file Claude made, then "Open in Google Drive", then say "done" |
| "Your binder isn't set up yet" | Say "set up my binder" |
| Claude ignores the binder completely | Check **Customize → Plugins** (Re binder is on) and **Customize → Connectors** (Google Drive is connected) |
| In the Code tab: "The binder's safety lock isn't running" | Start a new Code tab session and ask again |
