#!/usr/bin/env bash
# @raycast.schemaVersion 1
# @raycast.needsConfirmation false
# @raycast.mode silent
# @raycast.packageName Yabai
# @raycast.icon yabai.png
# @raycast.title Focus Next
# @raycast.description None

yabai -m window --focus next 2>/dev/null || yabai -m window --focus first
