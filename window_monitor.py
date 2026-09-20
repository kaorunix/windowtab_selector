#!/usr/bin/env python3
"""
macOS Window Monitor
アクティブウィンドウが切り替わるたびに、アプリケーション名とウィンドウタイトルをテキストファイルに記録します
"""

import subprocess
import time
from datetime import datetime
import os
import sys

# ログファイルのパス（スクリプトと同じディレクトリに保存）
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "window_history.txt")

# 前のウィンドウを記録（同じウィンドウを複数回出力しないため）
last_window = ""

def get_active_window():
    """
    macOS のアクティブウィンドウ情報を取得
    アプリケーション名とウィンドウタイトルを返す
    """
    try:
        script = '''
        tell application "System Events"
            set frontApp to first application process whose frontmost is true
            set frontAppName to name of frontApp
            try
                set frontWindow to first window of frontApp whose value of attribute "AXMain" is true
                set windowTitle to name of frontWindow
            on error
                set windowTitle to "No Window"
            end try
        end tell
        return {frontAppName, windowTitle}
        '''
        
        # AppleScript を実行
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # 出力を解析（フォーマット: "AppName, WindowTitle"）
            output = result.stdout.strip()
            parts = output.split(", ", 1)  # 最初のカンマで分割（2つ）
            
            if len(parts) == 2:
                app_name = parts[0].strip()
                window_title = parts[1].strip()
                return app_name, window_title
        
        return None, None
    
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return None, None

def log_window_change(app_name, window_title):
    """
    ウィンドウ情報をテキストファイルに出力
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | {app_name} | {window_title}\n"
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # コンソールにも出力（デバッグ用）
        print(log_entry.strip())
    
    except Exception as e:
        print(f"ログ出力エラー: {e}", file=sys.stderr)

def main():
    """
    メインループ：ウィンドウを監視し続ける
    """
    global last_window
    
    print(f"ウィンドウモニタースクリプトを開始します")
    print(f"ログファイル: {LOG_FILE}")
    print(f"Ctrl+C で終了します\n")
    
    # ログファイルが存在しなければ作成し、ヘッダーを追加
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("=== macOS ウィンドウ履歴ログ ===\n")
            f.write(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    try:
        while True:
            app_name, window_title = get_active_window()
            
            if app_name and window_title:
                # 現在のウィンドウ情報
                current_window = f"{app_name}|{window_title}"
                
                # ウィンドウが変わった場合のみ記録
                if current_window != last_window:
                    log_window_change(app_name, window_title)
                    last_window = current_window
            
            # 0.5秒ごとに確認（CPU使用率を抑えるため）
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\nウィンドウモニタースクリプトを終了しました")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n予期しないエラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
