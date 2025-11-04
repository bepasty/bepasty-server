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

# Keep defaults in sync with bepasty by only setting values that are
# explicitly provided via environment variables.
if "BEPASTY_STORAGE_FILESYSTEM_DIRECTORY" in os.environ:
    STORAGE_FILESYSTEM_DIRECTORY = os.environ["BEPASTY_STORAGE_FILESYSTEM_DIRECTORY"]

if "BEPASTY_DEFAULT_PERMISSIONS" in os.environ:
    DEFAULT_PERMISSIONS = os.environ["BEPASTY_DEFAULT_PERMISSIONS"]

if "BEPASTY_MAX_ALLOWED_FILE_SIZE" in os.environ:
    try:
        MAX_ALLOWED_FILE_SIZE = int(os.environ["BEPASTY_MAX_ALLOWED_FILE_SIZE"])
    except ValueError as err:
        print("\n\nInvalid BEPASTY_MAX_ALLOWED_FILE_SIZE: %s" % str(err))
        sys.exit(1)

if "BEPASTY_MAX_BODY_SIZE" in os.environ:
    try:
        MAX_BODY_SIZE = int(os.environ["BEPASTY_MAX_BODY_SIZE"])
    except ValueError as err:
        print("\n\nInvalid BEPASTY_MAX_BODY_SIZE: %s" % str(err))
        sys.exit(1)
