#!/usr/bin/env bash
# @raycast.schemaVersion 1
# @raycast.needsConfirmation false
# @raycast.mode silent
# @raycast.packageName Yabai
# @raycast.icon yabai.png
# @raycast.title Focus Prev

yabai -m window --focus prev 2>/dev/null || yabai -m window --focus last
