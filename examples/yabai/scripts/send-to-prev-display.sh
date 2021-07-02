#!/usr/bin/env bash
# @raycast.schemaVersion 1
# @raycast.needsConfirmation false
# @raycast.mode silent
# @raycast.packageName Yabai
# @raycast.icon yabai.png
# @raycast.title Send to Prev Display
# @raycast.description None

yabai -m window --space prev 2>/dev/null || yabai -m window --space last
