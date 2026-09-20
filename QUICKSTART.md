# クイックスタート - 5分で始める

## 今すぐやる 3ステップ

### ステップ1：ターミナルで実行権限を付与（30秒）

```bash
chmod +x ~/window_monitor.py ~/window_selector_cowork.py
```

### ステップ2：ウィンドウモニターを開始（1分）

ターミナルで実行：
```bash
python3 ~/window_monitor.py
```

このウィンドウはそのまま開いておく（バックグラウンドで動作）。

確認用に別のターミナルで：
```bash
tail -f ~/window_history.txt
```

ウィンドウを切り替えると、タイムスタンプ付きでログが記録されます。

### ステップ3：Cowork でテスト（3分）

Claude Desktop を開く：

1. **Cowork** タブをクリック
2. テキスト入力欄に以下を入力：
   ```
   python3 ~/window_selector_cowork.py
   ```
3. 実行

すると、最新10件のウィンドウが表示されます。

---

## 動作確認

### ウィンドウログが記録されているか確認

```bash
# ターミナルで実行
cat ~/window_history.txt

# 出力例:
# === macOS ウィンドウ履歴ログ ===
# 開始時刻: 2026-09-19 14:20:00
#
# 2026-09-19 14:20:15 | Chrome | Gmail - Inbox
# 2026-09-19 14:21:30 | Excel | 営業データ.xlsx
# 2026-09-19 14:22:45 | Word | 提案書.docx
```

---

## 次のステップ（オプション）

### A. 自動起動設定（PC 起動時に自動でログ記録）

```bash
cat > ~/Library/LaunchAgents/com.fideo.windowmonitor.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fideo.windowmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/$(whoami)/window_monitor.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/windowmonitor.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/windowmonitor.err</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.fideo.windowmonitor.plist
```

### B. 音声コマンドで試す（会議中の操作）

1. Cowork のテキスト入力欄をクリック
2. **Fn キーを2回押す**（Dictation 起動）
3. 「3番のウィンドウを開いてください」と話す
4. Claude（Cowork）が自動実行

---

## 実際の使い方

### パターン1：「2番を開いて」（Cowork から）

```
Cowork のテキスト入力欄に：
python3 ~/window_selector_cowork.py 2

↓

✓ Excel をアクティブにしました
```

### パターン2：対話型（Cowork から）

```
Cowork のテキスト入力欄に：
python3 ~/window_selector_cowork.py

↓

【ウィンドウ履歴 - 最新10件】
 1. Chrome | Gmail
 2. Excel | 営業データ.xlsx
 3. Word | 提案書.docx
...

開くウィンドウの番号を入力してください: 3

↓

✓ Word をアクティブにしました
```

### パターン3：音声で指示（会議中）

```
1. Fn + Fn で Dictation 起動
2. 「3番を開いてください」と話す
3. テキスト化される
4. Cowork が実行
5. Word が開く
```

---

## トラブルシューティング

**Q: window_monitor.py がエラーで止まった**

```bash
python3 ~/window_monitor.py
# エラーメッセージを確認
```

**Q: Cowork から実行できない**

```bash
# テスト用に対話型で実行
python3 ~/window_selector_cowork.py

# 「5」と入力して試す
```

**Q: ログファイルに何も書き込まれない**

```bash
# window_monitor.py が動作しているか確認
ps aux | grep window_monitor

# 動作していなければターミナルで開始
python3 ~/window_monitor.py
```

---

## ファイル配置

```
~/ (ホームディレクトリ)
├── window_monitor.py           ← 実行中
├── window_selector_cowork.py   ← Cowork で実行
├── window_history.txt          ← ログ（自動生成）
├── SETUP_GUIDE.md              ← 詳しいガイド
└── QUICKSTART.md               ← このファイル

~/Library/LaunchAgents/
└── com.fideo.windowmonitor.plist  ← 自動起動設定（オプション）
```

---

## 今の状態

✅ システムの準備完了
✅ ウィンドウログ記録開始
✅ Cowork から操作可能
✅ 音声コマンド対応

これですべての機能が使えます。試してみてください！
