#!/usr/bin/env sh

gh repo list dailymotion --json name --json description --json url --limit "$1" --jq '.[] | {title: "Open \(.name) Repository", command: "open \(.url)", description: .description}' | raygen --icon logo.png --input-format json --line-delimited --package Github --clean -
