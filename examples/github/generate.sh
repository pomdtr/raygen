#!/usr/bin/env sh
LIMIT=${1:-1000}
gh repo list dailymotion --no-archived --json name --json description --json url --json pushedAt --limit "$LIMIT" --jq '.[] | select(.pushedAt > "2021") | {title: "Open \(.name) Repository", command: "open \(.url)", description: .description}' | raygen --icon logo.png --input-format ndjson --package Github --clean -
