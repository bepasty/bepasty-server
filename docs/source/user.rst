=============
Using bepasty
=============

Logging in and Permissions
==========================

You may need to log in to get enough permissions required for the misc. functions of bepasty.

Your current permissions are shown on the web interface (in the navigation bar).

To log in, you need to know credentials - ask the admin who runs the site.

The site admin can assign permissions to login credentials (and also to the anonymous, not logged-in user):

* create: be able to create pastebins
* read: be able to read / download pastebins
* delete: be able to delete pastebins
* admin: be able to list all pastebins, to lock/unlock files

Pasting text
============

Just paste it into that big upper text input box.

Content-Type: Below the box you can optionally choose the type of your content (if you don't, it will become plain text).
Just start typing some letters of the type, e.g. if you pasted some python code, type pyt and see how it
offers you some choices based on that. Based on that type, we will highlight your text (using the Pygments
library, which supports a lot of text formats).

File name: You can optionally give a filename for your paste. If someone later downloads it, the browser will
use the filename you gave. If you don't give a filename, it will use "paste.txt".

When finished, click on "Submit". bepasty will save your text using a unique ID and redirect you to the URL
where you can view or download your pasted text.

Uploading files
===============

See that big box below the text input box - you can:

* click it to upload a single file (via the file selection dialogue of your browser). repeat if you have multiple files.
* drag files from your desktop and drop them there

Note: some features require a modern browser, like a current Firefox or Chrome/Chromium with Javascript enabled.

It will show you a progress indication while the files upload.

After the files are uploaded, bepasty will show you a list of links to the individual views of each uploaded file.
Make sure you keep all the links (open the links in new tabs / new windows) - they are the only way to access the files.

Additionally, bepasty prepared a file list for you (that has all the unique IDs of your uploaded files). If you
create a list item by hitting the respective button, bepasty will store that list in yet another pastebin item, so
you need to remember only that one URL. It's also a nice way to communicate a collection of files as you only need to
communicate that one URL (not each individual file's URL).

Viewing / Downloading files
===========================

Just visit the file's unique URL to view, download or delete it.

bepasty will show you metadata like:

* file name
* precise file size
* upload date/time (UTC)
* sha256 hash of the file contents

bepasty also supports directly displaying the data, for these content types:

* lists of files (if a list item was created at upload time)
* text files (highlighted depending on the content-type)
* PDFs (if you browser can render PDFs or has a plugin doing that)
* image files, like jpeg, png and svg
* audio/video files (using the html5 player widget, format support might depend on your browser and OS)
* for other file types, you need to download them and open them with the appropriate application

File hashes
===========

If you're unfamiliar with hashes like SHA256, you might wonder what they are good for and why we show them.

A hash is something like a checksum or fingerprint of the file contents. We compute the hash while or directly
after the file upload. If you have 2 files at different places and they have the same SHA256 hash, you can be
pretty sure that they have completely identical contents.

If you are looking at a file you just uploaded yourself, it might be interesting to compare the size and hash with
the values you see for your local file to make sure the upload worked correctly.

Same after you download a file: check whether the hash matches for the file on bepasty and your downloaded file.

If you transfer a file from location A via bepasty (B) to location C, you can also compare the file hashes at locations
A and C to make sure the file was not modified or corrupted while being transferred.

Important stuff to remember
===========================

* if you get credentials from an admin, do not make them available to other persons except if explicitly allowed
* files may go away at any time, always remember that a pastebin site is only for short-term temporary storage
  (how long this is depends on the site's / site admin's policy and available disk space)
