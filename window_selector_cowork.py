#!/usr/bin/env python3
"""
macOS Window Selector (ブラウザのタブ対応版)

~/window_history.txt から最近使ったウィンドウ / ブラウザタブを
新しい順に重複なしで並べ、番号で選ぶと そこへ切り替える。

使い方:
    python3 window_selector_cowork.py        対話型
    python3 window_selector_cowork.py 3      一覧を出して 3 番へ切り替え
    python3 window_selector_cowork.py -l     一覧だけ表示して終了
"""

import os
import subprocess
import sys

from wt_config import LOG_FILE

LIMIT = 10

CHROMIUM_APPS = {
    "Google Chrome",
    "Google Chrome Canary",
    "Chromium",
    "Brave Browser",
    "Microsoft Edge",
    "Arc",
}

# Chrome 系: URL が一致するタブを探してアクティブにする
CHROMIUM_SCRIPT = r'''
on run argv
    set appName to item 1 of argv
    set targetURL to item 2 of argv
    tell application appName
        activate
        repeat with w in windows
            set i to 1
            repeat with t in tabs of w
                if (URL of t) is targetURL then
                    set active tab index of w to i
                    set index of w to 1
                    return "ok"
                end if
                set i to i + 1
            end repeat
        end repeat
    end tell
    return "notfound"
end run
'''

SAFARI_SCRIPT = r'''
on run argv
    set targetURL to item 1 of argv
    tell application "Safari"
        activate
        repeat with w in windows
            repeat with t in tabs of w
                if (URL of t) is targetURL then
                    set current tab of w to t
                    set index of w to 1
                    return "ok"
                end if
            end repeat
        end repeat
    end tell
    return "notfound"
end run
'''


def parse_line(line):
    """1行を (日時, アプリ, タイトル, URL) に分解。

    新形式(タブ区切り)と旧形式("|"区切り)の両方を受け付ける。
    """
    line = line.rstrip("\n")
    if not line.strip():
        return None

    if "\t" in line:
        parts = line.split("\t")
    elif "|" in line:
        # 旧形式: 日時 | アプリ | タイトル  (タイトル内の | は残る)
        parts = [p.strip() for p in line.split("|", 2)]
    else:
        return None

    while len(parts) < 4:
        parts.append("")

    ts, app, title, url = (p.strip() for p in parts[:4])
    if not app or app.startswith("==="):
        return None
    return ts, app, title, url


def read_history(limit=LIMIT):
    """新しい順・重複なしで最大 limit 件返す。"""
    if not os.path.exists(LOG_FILE):
        print(f"ログが見つかりません: {LOG_FILE}")
        print("window_monitor.py を起動してください")
        return []

    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    seen = set()
    entries = []
    for line in reversed(lines):          # 新しい行から見る
        rec = parse_line(line)
        if not rec:
            continue
        ts, app, title, url = rec
        key = (app, title, url)
        if key in seen:
            continue
        seen.add(key)
        entries.append(rec)
        if len(entries) >= limit:
            break
    return entries


def shorten(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


def show(entries):
    if not entries:
        print("履歴がまだありません")
        return
    print()
    print("=" * 78)
    print("【最近のウィンドウ / タブ】")
    print("=" * 78)
    for i, (ts, app, title, url) in enumerate(entries, 1):
        mark = "🌐" if url else "  "
        print(f"{i:2d}. {mark} {shorten(app, 14):14s} {shorten(title, 44)}")
        if url:
            print(f"        {shorten(url, 66)}")
    print("=" * 78)
    print()


def run_osascript(script, args):
    try:
        r = subprocess.run(
            ["osascript", "-e", script] + args,
            capture_output=True, text=True, timeout=15,
        )
        return r.returncode == 0 and "ok" in r.stdout
    except Exception as e:
        print(f"切り替えに失敗しました: {e}")
        return False


def activate_app(app):
    script = f'tell application "{app}" to activate'
    try:
        subprocess.run(["osascript", "-e", script], timeout=10, check=True)
        return True
    except Exception as e:
        print(f"{app} を前面にできませんでした: {e}")
        return False


def switch_to(entry):
    ts, app, title, url = entry

    if url and app in CHROMIUM_APPS:
        if run_osascript(CHROMIUM_SCRIPT, [app, url]):
            print(f"→ {app}: {title}")
            return True
        print("そのタブは見つかりませんでした（閉じた可能性があります）")
        return activate_app(app)

    if url and app == "Safari":
        if run_osascript(SAFARI_SCRIPT, [url]):
            print(f"→ Safari: {title}")
            return True
        print("そのタブは見つかりませんでした（閉じた可能性があります）")
        return activate_app(app)

    if activate_app(app):
        print(f"→ {app}")
        return True
    return False


def main():
    args = sys.argv[1:]

    entries = read_history()
    if not entries:
        sys.exit(1)

    show(entries)

    if args and args[0] in ("-l", "--list"):
        return

    if args:
        try:
            n = int(args[0])
        except ValueError:
            print("番号を指定してください")
            sys.exit(1)
        if not (1 <= n <= len(entries)):
            print(f"1 から {len(entries)} の間で指定してください")
            sys.exit(1)
        switch_to(entries[n - 1])
        return

    while True:
        try:
            s = input(f"番号を入力 (1-{len(entries)}, q で終了): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if s.lower() in ("q", "quit", "exit", ""):
            return
        try:
            n = int(s)
        except ValueError:
            print("数字を入れてください")
            continue
        if not (1 <= n <= len(entries)):
            print(f"1 から {len(entries)} の間で指定してください")
            continue
        switch_to(entries[n - 1])
        return


if __name__ == "__main__":
    main()
