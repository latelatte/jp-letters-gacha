from pathlib import Path

ASSETS_DIR = Path("./assets")
ASSETS_DIR.mkdir(exist_ok=True)

import json
import os
from datetime import datetime

DATA_FILE = ASSETS_DIR / "data.json"

# ファイルがなければ空データで作成
if not DATA_FILE.exists():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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