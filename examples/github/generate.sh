#!/usr/bin/env sh
gh api -X GET /users/pomdtr/starred --paginate --jq '.[] | select(.owner.login == "dailymotion") | {title: "Open or Search \(.name) Repository", command: "./open_or_search.sh \(.html_url) $1", description: .description}' \
| raygen --icon logo.png --input-format ndjson --package-name Github --clean --argument query --optional-arg --encode-arg --embed open_or_search.sh -
