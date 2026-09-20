#!/usr/bin/env python3
"""
macOS Window Selector for Cowork
ウィンドウ履歴から最新N件を表示し、ユーザーが選択したウィンドウを開く
Cowork で使用することを想定
"""

import subprocess
import os
import sys
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "window_history.txt")

def read_window_history(limit=10):
    """
    ウィンドウ履歴ファイルから最新N件を読み込む
    """
    if not os.path.exists(LOG_FILE):
        print(f"エラー: {LOG_FILE} が見つかりません")
        print("window_monitor.py を先に実行してください")
        return []
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # ヘッダーと空行をスキップしながら逆順で読む
        entries = []
        for line in reversed(lines):
            line = line.strip()
            if line and "|" in line and not line.startswith("===") and not line.startswith("開始"):
                entries.append(line)
                if len(entries) >= limit:
                    break
        
        return list(reversed(entries))
    
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
        return []

def parse_entry(entry):
    """
    ログエントリをパース
    フォーマット: "YYYY-MM-DD HH:MM:SS | AppName | WindowTitle"
    """
    try:
        parts = entry.split("|")
        if len(parts) >= 3:
            timestamp = parts[0].strip()
            app_name = parts[1].strip()
            window_title = parts[2].strip()
            return timestamp, app_name, window_title
    except:
        pass
    return None, None, None

def display_history(entries):
    """
    ウィンドウ履歴を表示
    """
    print("\n" + "="*80)
    print("【ウィンドウ履歴 - 最新10件】")
    print("="*80)
    
    if not entries:
        print("ウィンドウ履歴が記録されていません")
        print("window_monitor.py を先に実行してください")
        print("="*80 + "\n")
        return False
    
    for i, entry in enumerate(entries, 1):
        timestamp, app_name, window_title = parse_entry(entry)
        if timestamp and app_name:
            # ウィンドウタイトルが長い場合は省略
            if len(window_title) > 40:
                window_title = window_title[:37] + "..."
            print(f"{i:2d}. [{timestamp}] {app_name:15s} | {window_title}")
    
    print("="*80 + "\n")
    return True

def activate_app(app_name):
    """
    macOS でアプリケーションをアクティブにする
    """
    try:
        script = f'''
        tell application "{app_name}"
            activate
        end tell
        '''
        subprocess.run(['osascript', '-e', script], timeout=5, check=True)
        return True
    except Exception as e:
        print(f"エラー: {app_name} を開けませんでした - {e}")
        return False

def main():
    """
    メイン処理
    使用方法:
      python3 window_selector_cowork.py           # 対話型
      python3 window_selector_cowork.py 3         # 自動実行モード（3番を開く）
    """
    
    # ウィンドウ履歴を読み込み
    entries = read_window_history(limit=10)
    
    # 履歴を表示
    if not display_history(entries):
        sys.exit(1)
    
    # コマンドライン引数がある場合は自動実行
    if len(sys.argv) > 1:
        try:
            num = int(sys.argv[1])
            if 1 <= num <= len(entries):
                timestamp, app_name, window_title = parse_entry(entries[num - 1])
                if app_name:
                    print(f"開いています: {app_name} - {window_title}")
                    if activate_app(app_name):
                        print(f"✓ {app_name} をアクティブにしました")
                        sys.exit(0)
                    else:
                        print(f"✗ {app_name} をアクティブにできませんでした")
            else:
                print(f"エラー: 1 から {len(entries)} の番号を入力してください")
                sys.exit(1)
        except ValueError:
            print(f"エラー: 有効な番号を入力してください")
            sys.exit(1)
    else:
        # 対話型モード
        while True:
            try:
                user_input = input("開くウィンドウの番号を入力してください（1-10）、または 'quit' で終了: ").strip()
                
                if user_input.lower() == 'quit':
                    print("終了します")
                    break
                
                try:
                    num = int(user_input)
                    if 1 <= num <= len(entries):
                        timestamp, app_name, window_title = parse_entry(entries[num - 1])
                        if app_name:
                            print(f"\n開いています: {app_name} - {window_title}")
                            if activate_app(app_name):
                                print(f"✓ {app_name} をアクティブにしました\n")
                                sys.exit(0)
                            else:
                                print(f"✗ {app_name} をアクティブにできませんでした\n")
                    else:
                        print(f"1 から {len(entries)} の番号を入力してください\n")
                except ValueError:
                    print("有効な番号を入力してください\n")
            
            except KeyboardInterrupt:
                print("\n\n終了します")
                break

if __name__ == "__main__":
    main()
