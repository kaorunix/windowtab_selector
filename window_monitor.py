#!/usr/bin/env python3
"""
macOS Window Monitor (ブラウザのタブ対応版)

アクティブなウィンドウ、またはブラウザのアクティブタブが変わるたびに
1行追記する。

ログ形式 (タブ区切り / TSV):
    日時 <TAB> アプリ名 <TAB> タイトル <TAB> URL

URL はブラウザ以外では空になる。
タイトルに "|" が含まれても壊れないよう、区切りはタブ文字を使う。
"""

import os
import signal
import subprocess
import sys
import time
from datetime import datetime

# ログファイルのパス（スクリプトと同じディレクトリに保存）
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "window_history.txt")
INTERVAL = 1.0  # 秒。短くすると反応は良くなるが osascript の呼び出しが増える

APPLESCRIPT = r'''
set delim to (ASCII character 9)
set theTitle to ""
set theURL to ""

tell application "System Events"
    set frontApp to name of first application process whose frontmost is true
end tell

if frontApp is in {"Google Chrome", "Google Chrome Canary", "Chromium", "Brave Browser", "Microsoft Edge", "Arc"} then
    try
        tell application frontApp
            if (count of windows) > 0 then
                set theTitle to title of active tab of front window
                set theURL to URL of active tab of front window
            end if
        end tell
    end try
else if frontApp is "Safari" then
    try
        tell application "Safari"
            if (count of windows) > 0 then
                set theTitle to name of current tab of front window
                set theURL to URL of current tab of front window
            end if
        end tell
    end try
end if

if theTitle is "" then
    try
        tell application "System Events"
            tell process frontApp
                set theTitle to name of front window
            end tell
        end tell
    end try
end if

return frontApp & delim & theTitle & delim & theURL
'''


def clean(s):
    """タブと改行を潰す。TSV を壊さないため。"""
    return " ".join(s.split())


def get_active():
    """(アプリ名, タイトル, URL) を返す。取れなければ None。"""
    try:
        r = subprocess.run(
            ["osascript", "-e", APPLESCRIPT],
            capture_output=True, text=True, timeout=5,
        )
    except Exception:
        return None

    if r.returncode != 0:
        return None

    parts = r.stdout.rstrip("\n").split("\t")
    while len(parts) < 3:
        parts.append("")

    app = clean(parts[0])
    title = clean(parts[1])
    url = clean(parts[2])

    if not app:
        return None
    return app, title, url


def append_log(app, title, url):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{app}\t{title}\t{url}\n")
    print(f"{ts}  {app}  {title}  {url}".rstrip())
    sys.stdout.flush()


def on_signal(sig, frame):
    print("\nウィンドウモニターを終了しました")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    print("ウィンドウモニターを開始します")
    print(f"ログファイル: {LOG_FILE}")
    print("Ctrl+C で終了します\n")

    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "a", encoding="utf-8").close()

    last_key = None

    while True:
        got = get_active()
        if got:
            app, title, url = got
            key = (app, title, url)
            if key != last_key:
                append_log(app, title, url)
                last_key = key
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
