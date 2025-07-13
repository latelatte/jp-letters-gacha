import random
import math
from logics.char_loader import load_char_sets

hiragana_chars, katakana_chars, jouyou_chars, rarity_map = load_char_sets()

# hiragana には明示的な rarity がなければ N-hira を割り当てる
for ch in hiragana_chars:
    rarity_map.setdefault(ch, "N-hira")

# jouyou（常用漢字）も同様に
for ch in jouyou_chars:
    rarity_map.setdefault(ch, "N-kanji")

RARITY_WEIGHTS = {
    "SSR": 0.5,
    "SR": 1,
    "R": 10,
    "N-hira": 7,
    "N-kanji": 2
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

def draw_weighted_char():
    from collections import defaultdict

    # レアリティごとの文字グループを作成
    rarity_groups = defaultdict(list)
    all_chars = set(hiragana_chars + katakana_chars + jouyou_chars + list(rarity_map.keys()))
    for ch in all_chars:
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