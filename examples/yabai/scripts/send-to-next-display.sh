#!/usr/bin/env bash
# @raycast.schemaVersion 1
# @raycast.needsConfirmation false
# @raycast.mode silent
# @raycast.packageName Yabai
# @raycast.icon yabai.png
# @raycast.title Send to Next Display
# @raycast.description None

yabai -m window --space next 2>/dev/null || yabai -m window --space first
