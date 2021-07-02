#!/usr/bin/env bash
# @raycast.schemaVersion 1
# @raycast.needsConfirmation false
# @raycast.mode silent
# @raycast.packageName Yabai
# @raycast.icon yabai.png
# @raycast.title Focus Next in Stack

yabai -m window --focus stack.next 2>/dev/null || yabai -m window --focus stack.first
