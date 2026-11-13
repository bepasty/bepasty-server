import os
import sys


def error_exit(message):
    print("\n\n%s" % message)
    sys.exit(1)


SITENAME = os.environ.get("BEPASTY_SITENAME")
if SITENAME is None:
    error_exit("Environment variable BEPASTY_SITENAME must be set.")

SECRET_KEY = os.environ.get("BEPASTY_SECRET_KEY")
if SECRET_KEY is None:
    error_exit("Environment variable BEPASTY_SECRET_KEY must be set.")

APP_BASE_PATH = os.environ.get("BEPASTY_APP_BASE_PATH")

# Keep defaults in sync with bepasty by only setting values that are
# explicitly provided via environment variables.
storage_filesystem_directory = os.environ.get("BEPASTY_STORAGE_FILESYSTEM_DIRECTORY")
if storage_filesystem_directory is not None:
    STORAGE_FILESYSTEM_DIRECTORY = storage_filesystem_directory

default_permissions = os.environ.get("BEPASTY_DEFAULT_PERMISSIONS")
if default_permissions is not None:
    DEFAULT_PERMISSIONS = default_permissions

max_allowed_file_size = os.environ.get("BEPASTY_MAX_ALLOWED_FILE_SIZE")
if max_allowed_file_size is not None:
    try:
        MAX_ALLOWED_FILE_SIZE = int(max_allowed_file_size)
    except ValueError as err:
        error_exit("Invalid BEPASTY_MAX_ALLOWED_FILE_SIZE: %s" % str(err))

max_body_size = os.environ.get("BEPASTY_MAX_BODY_SIZE")
if max_body_size is not None:
    try:
        MAX_BODY_SIZE = int(max_body_size)
    except ValueError as err:
        error_exit("Invalid BEPASTY_MAX_BODY_SIZE: %s" % str(err))
