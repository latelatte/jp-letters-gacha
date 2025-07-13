import json
from pathlib import Path

# 文字データの読み込み
def load_char_sets():
    base = Path(__file__).parents[1] / "assets"
    with open(base / "hiragana.json", encoding="utf-8") as f:
        hiragana = json.load(f)
    with open(base / "katakana.json", encoding="utf-8") as f:
        katakana = json.load(f)
    with open(base / "jouyou_kanji.json", encoding="utf-8") as f:
        kanji = json.load(f)   
    with open(base / "symbols.json", encoding="utf-8") as f:
        symbols = json.load(f)
    with open(base / "rarity_map.json", encoding="utf-8") as f:
        rarity_map = json.load(f)
    hiragana_list = [e["kana"] for e in hiragana]
    katakana_list = list(katakana.keys())
    kanji_list = list(kanji.keys())
    
    for ch, rarity in katakana.items():
        rarity_map[ch] = rarity

    for ch, rarity in symbols.items():
        rarity_map[ch] = rarity
    return hiragana_list, katakana_list, kanji_list, rarity_map