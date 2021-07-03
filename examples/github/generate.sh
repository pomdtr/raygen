#!/usr/bin/env sh
ORG=$1
LIMIT=${2:-1000}
MIN_PUSH_TIME=${3:-2021}

gh repo list "$ORG" \
  --no-archived \
  --json name \
  --json description \
  --json url \
  --json pushedAt \
  --limit "$LIMIT" \
  --jq '.[] | select(.pushedAt > '"$MIN_PUSH_TIME"') | {title: "Open \(.name) Repository", command: "open \(.url)", description: .description}' \
| raygen --icon logo.png --input-format ndjson --package Github --clean -
