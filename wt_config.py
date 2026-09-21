#!/usr/bin/env python3
"""window_monitor.py / window_selector_cowork.py で共有する設定。"""

import os

_DEFAULT_LOG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "window_history.txt"
)

# WINDOW_HISTORY_LOG 環境変数で上書き可能
LOG_FILE = os.environ.get("WINDOW_HISTORY_LOG", _DEFAULT_LOG_FILE)
