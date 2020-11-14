========================
Using bepasty's REST-API
========================

The Rest-API enables you to upload and download files, as well as
retrieve informations about the file on the server.

Currently the REST API provides the following API Endpoints::

    GET  /apis/rest
    GET  /apis/rest/items
    POST /apis/rest/items
    GET  /apis/rest/items/<itemname>
    GET  /apis/rest/items/<itemname>/download
    POST /apis/rest/items/<itemname>/modify
    POST /apis/rest/items/<itemname>/delete
    POST /apis/rest/items/<itemname>/lock
    POST /apis/rest/items/<itemname>/unlock



Errors
======
The error response from REST-API will set ``Content-Type:
application/json``, and body as JSON format like the following
example. (it was previously ``Content-Type: text/html; charset=utf-8``
and partial HTML page or plain string)

Example::

    {
      "error": {
        "code": <HTTP status code>,
        "message": "<error detail>"
      }
    }


Retrieving information for uploading
====================================
API Interface:

    ::

        GET /apis/rest

GET Response by the server:

    Example Response::

        {
          MAX_ALLOWED_FILE_SIZE: 5000000000,
          MAX_BODY_SIZE: 1048576
        }

    This interface will give you important infos for uploading and
    downloading files to your bepasty server.  By now only the
    MAX_BODY_SIZE will be delivered to you, as no more info is
    available.

    MAX_BODY_SIZE
        The maximum size of a post request's body. This is limited by
        the webserver and other middleware. See the documentation for
        more information. This also gives you the maximum size for the
        chunked upload.

    MAX_ALLOWED_FILE_SIZE
        The maximum allowed filesize that can be stored on the
        server. Files uploads bigger than this limit will be aborted
        and the file on the server will be deleted.

Uploading a file
================
API Interface:

    ::

        POST /apis/rest/items

    When uploading a file, chunked upload is mandatory. Check the
    MAX_BODY_SIZE for the maximum chunk size that can be sent to the
    server. The body of the post request contains the base64 encoded
    binary of the file to be uploaded. (required permission:
    :ref:`create <permissions>`)

POST Request by the client:

    Post Request Body
        Contains the base64 encoded binary of the file to be uploaded.

    The following headers *can (cursive)* or **must (bold)** be
    delivered by every post request to the server:

    **Content-Range**
        The content-range header follows the specification by the w3c
        (http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.16).
        It has to be provided consistently and can resume a aborted
        file upload, together with the transaction-ID.

    **Transaction-ID**
        The transaction-ID will be provided by the server after the
        first upload chunk. After that first chunk, the transaction-id
        has to be provided by the client, to continue uploading the
        file.

    *Content-Type*
        The content-type of the file uploaded to the server. If the
        content-type is not given, the server will guess the
        content-type by the filename. If this fails the content-type
        will be 'application/octet-stream'

    *Content-Length*
        The content-length is mostly ignored by the server. It can be
        used to indicate the final file size. If your final file size
        is bigger than the maximum allowed size on the server, the
        upload will be aborted. The real filesize will be calculated
        by the server while uploading.

    *Content-Filename*
        The content-filename header can be used to name the file on
        the server. If no content-filename is passed, the server will
        generate a name from scratch. Maximum filename size is 50
        characters.

    *Maxlife-Unit*
        The maxlife-unit can be used with the maxlife-value header to
        define a lifetime for the file that is uploaded.  The unit has
        to be one of these::

            ['MINUTES', 'HOURS', 'DAYS', 'WEEKS', 'MONTHS', 'YEARS', 'FOREVER']

        If this header is omitted the unit will be forever

    *Maxlife-Value*
        The maxlife-value header defines the value of the maxlife-unit.

POST Response by the server:

    *Transaction-ID*
        Transaction-ID provided for continued upload in a chunked upload
        process.
    *Content-Disposition*
        The URI of the newly uploaded file on the server. Will only be
        provided when upload is finished and successful.

Retrieving information about a file
===================================
API Interface:

    ::

        GET /apis/rest/items/<itemname>

    (required permission: :ref:`read <permissions>`)

GET Request by the client:

    **itemname**
        The itemname of the file requested.

GET Response by the server:

    Example Response::

        {
          file-meta: {
            complete: true,
            filename: "Wallpaper Work.7z",
            hash: "dded24ba6f1d953bedb9d2745635a6f7462817061763b0d70f68b7952722f275",
            locked: false,
            size: 150225567,
            timestamp-download: 1414483078,
            timestamp-max-life: -1,
            timestamp-upload: 1414443534,
            type: "application/x-7z-compressed"
          },
          uri: "/apis/rest/items/N24bFRZm"
        }

    *URI*
        The URI of the file on the server. Used to link to the download.
    *File-Meta*
        *Filename*
            The Filename of the uploaded file.
        *Size*
            The calculated size of the file on the server.
        *Timestamp-Upload*
            The timestamp of the moment the file was uploaded.
        *Timestamp-Download*
            The timestamp of the last download.
        *Timestamp-Max_life*
            The lifetime timestamp of the file in seconds. -1 means to
            keep the file forever.
        *Complete*
            True if the file upload is completed. False if it isn't
        *Locked*
            Whether the file is locked or not.
        *Hash*
            The sha256 hash of the file uploaded. Calculated by the server.
        *Type*
            Mimetype of the file uploaded. If no filetype is provided
            this will be set to 'application/octet-stream'.

Retrieving Item List
====================
API Interface:

    ::

        GET /apis/rest/items

    (required permission: :ref:`list <permissions>`)

GET Request by the client:

    No Parameters

GET Response by the server:

    Example Response::

        {
          "N24bFRZm": {
            file-meta: {
              complete: true,
              filename: "Wallpaper Work.7z",
              hash: "dded24ba6f1d953bedb9d2745635a6f7462817061763b0d70f68b7952722f275",
              locked: false,
              size: 150225567,
              timestamp-download: 1414483078,
              timestamp-max-life: -1,
              timestamp-upload: 1414443534,
              type: "application/x-7z-compressed"
            },
            uri: "/apis/rest/items/N24bFRZm"
          }, ...
        }

    Parameters are the same as in *Retrieving information about a file*.


Downloading a file
==================
API Interface:

    ::

        GET /apis/rest/items/<itemname>/download

    (required permission: :ref:`read <permissions>`)

GET Response by the server:

    Example Response::

        Content-Type: application/x-7z-compressed
        Content-Length: 150225568
        Content-Disposition: attachment; filename="Wallpaper Work.7z"
        Content-Range: bytes 0-150225567/150225567

    Opens up a stream and delivers the binary data directly. The above
    headers can be found in the HTTP Response.


Modifying metadata
==================
API Interface:

    ::

        POST /apis/rest/items/<itemname>/modify

    Modify metadata specified by ``<itemname>``. (required permission:
    :ref:`modify <permissions>`)

POST Request by the client:

    **itemname**
        The itemname of the target file.

    **Content-Type**
        The content-type header must be ``application/json``

    New metadata is specified by JSON in the request body.  Currently
    this API is supporting to modify ``filename`` and ``type``.  For
    example, if you want to modify the filename::

        {"filename": "new-filename.txt"}

    if you want to modify both filename and type::

        {"filename": "new-filename.txt", "type": "new-mimetype"}

POST Response by the server:

    On success, status code == 200. Otherwise status code != 200.


Deleting a file
===============
API Interface:

    ::

        POST /apis/rest/items/<itemname>/delete

    Delete a file specified by ``<itemname>``. (required permission:
    :ref:`delete <permissions>`)

POST Request by the client:

    **itemname**
        The itemname of the target file.

POST Response by the server:

    On success, status code == 200. Otherwise status code != 200.


Locking a file
==============
API Interface:

    ::

        POST /apis/rest/items/<itemname>/lock

    Lock a file specified by ``<itemname>``. (required permission:
    :ref:`admin <permissions>`)

POST Request by the client:

    **itemname**
        The itemname of the target file.

POST Response by the server:

    On success, status code == 200. Otherwise status code != 200.


Unlocking a file
================
API Interface:

    ::

        POST /apis/rest/items/<itemname>/unlock

    Lock a file specified by ``<itemname>``. (required permission:
    :ref:`admin <permissions>`)

POST Request by the client:

    **itemname**
        The itemname of the target file.

POST Response by the server:

    On success, status code == 200. Otherwise status code != 200.
