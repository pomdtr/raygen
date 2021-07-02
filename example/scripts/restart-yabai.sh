#!/usr/bin/env bash
# @raycast.schemaVersion 1
# @raycast.needsConfirmation false
# @raycast.mode silent
# @raycast.packageName Yabai
# @raycast.icon yabai.png
# @raycast.title Restart Yabai

launchctl kickstart -k "gui/${UID}/homebrew.mxcl.yabai"
