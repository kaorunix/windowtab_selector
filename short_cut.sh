#!/bin/sh
osascript <<'APPLESCRIPT'
tell application "Terminal"
    activate
    do script "python3 ~/private/Projects/page_pick/window_selector_cowork.py"
end tell
APPLESCRIPT
