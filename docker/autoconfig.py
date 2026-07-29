#!/usr/bin/python

import os
import sys

SITENAME = os.environ.get("BEPASTY_SITENAME", None)
if SITENAME is None:
    print("\n\nEnvironment variable BEPASTY_SITENAME must be set.")
    sys.exit(1)

SECRET_KEY = os.environ.get("BEPASTY_SECRET_KEY", None)
if SECRET_KEY is None:
    print("\n\nEnvironment variable BEPASTY_SECRET_KEY must be set.")
    sys.exit(1)

APP_BASE_PATH = os.environ.get("BEPASTY_APP_BASE_PATH", None)

STORAGE_FILESYSTEM_DIRECTORY = os.environ.get(
    "BEPASTY_STORAGE_FILESYSTEM_DIRECTORY", "/app/data",
)

DEFAULT_PERMISSIONS = os.environ.get("BEPASTY_DEFAULT_PERMISSIONS", "create,read")

PERMISSIONS = {}
admin_secret = os.environ.get("BEPASTY_ADMIN_SECRET", None)
if admin_secret is not None:
    PERMISSIONS.update({admin_secret: "admin,list,create,modify,read,delete"})

try:
    max_allowed_file_size = os.environ.get("BEPASTY_MAX_ALLOWED_FILE_SIZE", 5000000000)
    MAX_ALLOWED_FILE_SIZE = int(max_allowed_file_size)
except ValueError as err:
    print("\n\nInvalid BEPASTY_MAX_ALLOWED_FILE_SIZE: %s", str(err))
    sys.exit(1)

try:
    max_body_size = os.environ.get("BEPASTY_MAX_BODY_SIZE", 1040384)
    MAX_BODY_SIZE = int(max_body_size)
except ValueError as err:
    print("\n\nInvalid BEPASTY_MAX_BODY_SIZE: %s", str(err))
    sys.exit(1)
