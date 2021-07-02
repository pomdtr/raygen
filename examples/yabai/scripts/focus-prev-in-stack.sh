#!/usr/bin/env bash
# @raycast.schemaVersion 1
# @raycast.needsConfirmation false
# @raycast.mode silent
# @raycast.packageName Yabai
# @raycast.icon yabai.png
# @raycast.title Focus Prev in Stack
# @raycast.description None

yabai -m window --focus stack.prev 2>/dev/null || yabai -m window --focus stack.last
