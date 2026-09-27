# Using Google Drive (for Claude)

The binder lives in his Google Drive. You reach it only through the Google Drive connector.

**Find the binder.**
- Search `title = 'R&E Binder' and mimeType = 'application/vnd.google-apps.folder'`, with the exact
  title only. Check each result's title yourself. A folder like "R&E Binder (lab Sep 24)" is not his
  binder: never use it, rename it or move it.
- None found: say "Your binder isn't set up yet. Say “set up my binder” first."
- Two found: ask him which one.

**List a folder.**
- Use `parentId = 'ID'`. For many folders at once: `parentId = 'A' or parentId = 'B'`. Each result
  says its parentId.
- Results come in pages: always follow `nextPageToken` to the end. Use pageSize 100.
- Leave out content snippets when you only need names.
- In a query, write an apostrophe as `\'`.

**Make things.**
- A folder: create_file with mimeType `application/vnd.google-apps.folder` and a parentId. This worked
  in live tests on Sep 25, 2026, even though the connector marks that field as old. Make one at a
  time, parents first. Use the id each create returns as the next parent; don't search again.
- A Google Doc: create_file with textContent and contentMimeType `text/plain`.
- A Google Sheet: the same, with contentMimeType `text/csv`.

**Move and rename in one call:** update_file with the fileId, the new parentId, and the new title.

**Dates:** the day a file arrived in Drive is its createdTime.

**Links:** a file's link is the viewUrl that search or get_file_metadata returns. Never build one
yourself.

**Read.**
- read_file_content works for PDF, JPG, PNG and Google or Office files.
- It can't read iPhone photos (HEIC, mimeType `image/heif` or `image/heic`) or plain text files.
- For iPhone photos, see the filing skill.

**Never:**
- use trash_file, share_file or copy_file
- promise to edit a file (the connector can't change what's inside one)
- make or move anything outside the "R&E Binder" folder. The one exception: a file he just saved from
  the chat with "Open in Google Drive" lands at the top of My Drive, and you move it into the binder.
