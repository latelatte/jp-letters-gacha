import random
import math
from logics.char_loader import load_char_sets

hiragana_chars, katakana_chars, jouyou_chars, rarity_map = load_char_sets()

# レアリティごとの重み付け
RARITY_WEIGHTS = {
    "SSR": 1,
    "SR": 3,
    "R": 6,
    "N": 10
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

    all_chars = set(hiragana_chars + katakana_chars + jouyou_chars)
    rarity_groups = defaultdict(list)
    for ch in all_chars:
        rarity = rarity_map.get(ch, "N")
        rarity_groups[rarity].append(ch)

    chars = []
    weights = []

    for rarity, group in rarity_groups.items():
        base_weight = get_weight(rarity)
        group_size = len(group)
        if group_size == 0:
            continue
        weight_per_char = base_weight / math.sqrt(group_size)
        for ch in group:
            chars.append(ch)
            weights.append(weight_per_char)

    return random.choices(chars, weights=weights, k=1)[0]