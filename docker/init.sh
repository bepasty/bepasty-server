#!/bin/bash

if [ ! -f "$BEPASTY_CONFIG" ]; then
    echo "Please please mount a configuration file to '$BEPASTY_CONFIG'."
    exit 1
fi

if ! python "$BEPASTY_CONFIG"; then
    exit 1
fi

exec /app/env/bin/gunicorn -b "$LISTEN" --workers="$WORKERS" bepasty.wsgi:application
