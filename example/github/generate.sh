#!/usr/bin/env sh

gh repo list dailymotion --json name --json description --json url --limit 500 --jq '.[] | "Open \(.name) Repository|open \(.url)|\(.description)"' | raygen --input-format csv --delimiter '|' --package Github --clean -
