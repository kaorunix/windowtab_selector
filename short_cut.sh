#!/bin/sh
osascript <<'APPLESCRIPT'
tell application "Terminal"
    activate
    do script "python3 ~/private/Projects/windowtab_selector/window_selector_cowork.py"
end tell
APPLESCRIPT
