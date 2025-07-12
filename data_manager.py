import json
import os
from datetime import datetime

DATA_FILE = "data.json"

# ファイルがなければ空データで作成
if not os.path.exists(DATA_FILE):
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