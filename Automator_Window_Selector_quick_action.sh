#!/bin/sh
osascript <<'APPLESCRIPT'
tell application "Terminal"
    activate
    do script "python3 ~/private/Projects/windowtab_selector/window_selector_cowork.py"
    set theWindow to first window whose tabs contains theTab
    repeat while busy of theTab
        delay 0.3
    end repeat
    close theWindow
end tell
APPLESCRIPT
