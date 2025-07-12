


import random

def build_weighted_char_list(rarity_map, rarity_weights):
    """
    Build a weighted list of characters for gacha drawing.

    Each character's weight is calculated as:
        rarity_weight / number of characters in that rarity group
    """
    chars_by_rarity = {
        rarity: [ch for ch, r in rarity_map.items() if r == rarity]
        for rarity in rarity_weights
    }

    all_chars = []
    all_weights = []
    for rarity, chars in chars_by_rarity.items():
        if not chars:
            continue
        weight_per_char = rarity_weights[rarity] / len(chars)
        for ch in chars:
            all_chars.append(ch)
            all_weights.append(weight_per_char)

    return all_chars, all_weights

def draw_char(rarity_map, rarity_weights):
    """
    Draw a character using adjusted rarity and character distribution weights.
    """
    all_chars, all_weights = build_weighted_char_list(rarity_map, rarity_weights)
    return random.choices(all_chars, weights=all_weights, k=1)[0]