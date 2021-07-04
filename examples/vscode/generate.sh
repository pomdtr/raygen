#!/usr/bin/env sh

jq -c '.openedPathsList.entries[] | select(has("folderUri")) | select(.folderUri | startswith("file://")) | .folderUri | sub("file://"; "") | {title: "Open \(. | split("/") | .[-1]) Folder",command: "open vscode://file/\(.)"}' "/Users/$USER/Library/Application Support/Code/storage.json" | raygen --input-format ndjson --clean --shebang sh --package-name VSCode --icon vscode.png -
