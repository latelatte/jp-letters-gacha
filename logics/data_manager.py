from pathlib import Path

ASSETS_DIR = Path("./assets")
ASSETS_DIR.mkdir(exist_ok=True)

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Gist管理用のインポート
gist_manager = None  # グローバル変数として宣言

try:
    from .gist_manager import GistDataManager
    USE_GIST = True
except ImportError:
    USE_GIST = False
    GistDataManager = None  # 型チェック用

DATA_FILE = ASSETS_DIR / "data.json"

def init_data_manager():
    """データマネージャーを初期化（Bot起動時に呼び出す）"""
    global gist_manager
    
    if USE_GIST and GistDataManager:
        try:
            gist_manager = GistDataManager()
            # 起動時にGistからデータを同期
            data = gist_manager.sync_with_gist()
            # ローカルファイルにも保存（フォールバック用）
            _save_to_local_file(data)
            print("✅ Gistデータマネージャーを初期化しました")
        except Exception as e:
            print(f"⚠️ Gist初期化に失敗、ローカルファイルを使用: {e}")
            gist_manager = None
    else:
        print("⚠️ Gistモジュールが利用できません、ローカルファイルを使用")

def _save_to_local_file(data: Dict[str, Any]):
    """ローカルファイルにデータを保存（フォールバック用）"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _load_from_local_file() -> Dict[str, Any]:
    """ローカルファイルからデータを読み込み（フォールバック用）"""
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data():
    """データを読み込む（Gist優先、フォールバックでローカル）"""
    if gist_manager:
        try:
            return gist_manager.download_from_gist()
        except Exception as e:
            print(f"⚠️ Gistからの読み込みに失敗、ローカルファイルを使用: {e}")
    
    return _load_from_local_file()


def save_data(data):
    """データを保存（Gist優先、フォールバックでローカル）"""
    # ローカルファイルには必ず保存（フォールバック用）
    _save_to_local_file(data)
    
    # Gistにもアップロード試行
    if gist_manager:
        gist_manager.upload_to_gist(data)


def get_user_data(user_id):
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "points": 0,
            "last_claim_date": None,
            "letters": []
        }
        save_data(data)

    return data[user_id]


def update_user_data(user_id, user_data):
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)


# チャンネル設定管理
CHANNEL_CONFIG_FILE = ASSETS_DIR / "channel_config.json"

def load_channel_config():
    if not os.path.exists(CHANNEL_CONFIG_FILE):
        return {}
    with open(CHANNEL_CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_channel_id(kind):
    config = load_channel_config()
    key = "mission_channel_id" if kind == "mission" else "restricted_channel_id"
    return config.get(key)

# ミッション正解管理
def get_current_answer():
    """現在のミッション正解を取得"""
    config = load_channel_config()
    return config.get("current_answer", "あかさたな")  # デフォルト値

def set_current_answer(answer):
    """ミッション正解を設定"""
    config = load_channel_config()
    config["current_answer"] = answer
    
    if not os.path.exists(CHANNEL_CONFIG_FILE):
        CHANNEL_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CHANNEL_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)