import random
import math
from logics.char_loader import load_char_sets

hiragana_chars, katakana_chars, jouyou_chars, numbers_chars, rarity_map = load_char_sets()

# 数字も基本レアリティを設定
for ch in numbers_chars:
    rarity_map.setdefault(ch, "N")

RARITY_WEIGHTS = {
    "SSR": 1,
    "SR": 5,
    "R": 35,
    "N-hira": 40,
    "N-kanji": 19,
    "N": 30
}

def get_weight(rarity: str) -> int:
    return RARITY_WEIGHTS.get(rarity, 10)

def add_ssr_points(user: dict, rarity: str) -> str:
    if "ssr_points" not in user:
        user["ssr_points"] = 0
    points = {"SSR": 5, "SR": 3, "R": 2}.get(rarity, 1)
    user["ssr_points"] += points
    return f"+{points}"

def draw_ssr_char():
    ssr_chars = [ch for ch, rarity in rarity_map.items() if rarity == "SSR"]
    if not ssr_chars:
        return None
    return random.choice(ssr_chars)

def get_event_excluded_chars():
    """現在アクティブなイベントから通常ガチャで除外すべき文字を取得"""
    from pathlib import Path
    import json
    from datetime import date
    
    # 新形式の設定ファイルを優先
    events_config_path = Path(__file__).parent.parent / "assets" / "events_config.json"
    if events_config_path.exists():
        try:
            with open(events_config_path, encoding="utf-8") as f:
                events_data = json.load(f)
            
            current_event_id = events_data.get("current_event")
            if current_event_id and current_event_id in events_data.get("events", {}):
                config = events_data["events"][current_event_id]
                
                # イベントがアクティブかつイベント限定の場合のみ除外
                if not config.get("active", False) or not config.get("event_exclusive", False):
                    return set()
                
                # 期間チェック
                today = date.today()
                start = date.fromisoformat(config["start_date"])
                end = date.fromisoformat(config["end_date"])
                
                if not (start <= today <= end):
                    return set()
                
                return set(config.get("exclude_from_normal_gacha", []))
        except Exception:
            pass
    
    # 旧形式へのフォールバック
    config_path = Path(__file__).parent.parent / "assets" / "pickup_gacha.json"
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)
            
            # イベントがアクティブかつイベント限定の場合のみ除外
            if not config.get("active", False) or not config.get("event_exclusive", False):
                return set()
            
            # 期間チェック
            today = date.today()
            start = date.fromisoformat(config["start_date"])
            end = date.fromisoformat(config["end_date"])
            
            if not (start <= today <= end):
                return set()
            
            return set(config.get("exclude_from_normal_gacha", []))
        
        except Exception:
            pass
    
    return set()

def draw_weighted_char():
    from collections import defaultdict

    # イベント除外文字を動的に取得
    excluded_chars = get_event_excluded_chars()

    # レアリティごとの文字グループを作成（イベント除外文字を除く）
    rarity_groups = defaultdict(list)
    all_chars = set(hiragana_chars + katakana_chars + jouyou_chars + numbers_chars + list(rarity_map.keys()))
    for ch in all_chars:
        # イベント除外文字をスキップ
        if ch in excluded_chars:
            continue
        rarity = rarity_map.get(ch, "N-kanji")
        rarity_groups[rarity].append(ch)
        

    # レアリティと対応する重みをリスト化
    rarities = []
    rarity_weights = []
    for rarity, group in rarity_groups.items():
        if group:
            rarities.append(rarity)
            rarity_weights.append(get_weight(rarity))


    # レアリティを重み付きで1つ選ぶ
    selected_rarity = random.choices(rarities, weights=rarity_weights, k=1)[0]

    # そのレアリティに属する文字から1つ選ぶ
    return random.choice(rarity_groups[selected_rarity])