#!/bin/bash

# downloads ディレクトリの権限を修正
if [ -d "/app/downloads" ]; then
    sudo chown -R nablazy:nablazy /app/downloads
fi

# 元のコマンドを実行
exec "$@"

