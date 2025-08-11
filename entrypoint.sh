#!/bin/bash

# Fix downloads directory permissions
if [ -d "/app/downloads" ]; then
    sudo chown -R nablazy:nablazy /app/downloads
fi

# Execute original command
exec "$@"

