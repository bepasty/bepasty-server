========================
Using bepasty's REST-API
========================

The Rest-API enables you to upload and download files, as well as retrieve informations
about the file on the server.

Currently (Version 0.3) the REST API provides four API Endpoints::

    GET  /apis/rest
    POST /apis/rest/items
    GET  /apis/rest/items/<itemname>
    GET  /apis/rest/items/<itemname>/download



Retrieving information for uploading
====================================
API Interface::

    GET /apis/rest

Example Response::

    {
        MAX_ALLOWED_FILE_SIZE: 5000000000,
        MAX_BODY_SIZE: 1048576
    }

This interface will give you important infos for uploading and downloading files to your bepasty server.
By now only the MAX_BODY_SIZE will be delivered to you, as no more info is available.

MAX_BODY_SIZE
    The maximum size of a post request's body. This is limited by the webserver and other middleware. See the
    documentation for more information. This also gives you the maximum size for the chunked upload.

MAX_ALLOWED_FILE_SIZE
    The maximum allowed filesize that can be stored on the server. Files uploads bigger than this limit will be aborted
    and the file on the server will be deleted.

Uploading a file
================
API Interface::

    POST /apis/rest/items

When uploading a file, chunked upload is mandatory. Check the MAX_BODY_SIZE for the maximum chunk size that can
be sent to the server. The body of the post request contains the base64 encoded binary of the file to be uploaded.

POST Request by the client
--------------------------
Post Request Body
    Contains the base64 encoded binary of the file to be uploaded.

The following headers *can (cursive)* or **must (bold)** be delivered by every post request to the server:

**Content-Range**
    The content-range header follows the specification by the w3c (http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.16).
    It has to be provided consistently and can resume a aborted file upload, together with the transaction-ID.

**Transaction-ID**
    The transaction-ID will be provided by the server after the first upload chunk. After that first chunk, the transaction-id
    has to be provided by the client, to continue uploading the file.

*Content-Type*
    The content-type of the file uploaded to the server. If the content-type is not given, the server will guess the
    content-type by the filename. If this fails the content-type will be 'application/octet-stream'

*Content-Length*
    The content-length is mostly ignored by the server. It can be used to indicate the final file size. If your final
    file size is bigger than the maximum allowed size on the server, the upload will be aborted. The real filesize will
    be calculated by the server while uploading.

*Content-Filename*
    The content-filename header can be used to name the file on the server. If no content-filename is passed, the server
    will generate a name from scratch. Maximum filename size is 50 characters.

Maxlife-Unit

Maxlife-Value

Post Response by the server
---------------------------

Retrieving information about a file
===================================
API Interface::

    GET /apis/rest/items/<itemname>

Downloading a file
==================
API Interface::

    GET /apis/rest