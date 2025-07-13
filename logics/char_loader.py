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
    with open(base / "numbers.json", encoding="utf-8") as f:
        numbers = json.load(f)
    with open(base / "rarity_map.json", encoding="utf-8") as f:
        rarity_map = json.load(f)
    
    hiragana_list = [e["kana"] for e in hiragana]
    katakana_list = list(katakana.keys())
    kanji_list = list(kanji.keys())
    numbers_list = [e["character"] for e in numbers]
    
    # ひらがなのレアリティを追加
    for entry in hiragana:
        rarity_map[entry["kana"]] = entry["rarity"]
    
    for ch, rarity in katakana.items():
        rarity_map[ch] = rarity

    for ch, rarity in symbols.items():
        rarity_map[ch] = rarity
        
    for entry in numbers:
        rarity_map[entry["character"]] = entry["rarity"]
        
    # ひらがなのNレアリティをN-hiraに変更
    for ch in hiragana_list:
        if rarity_map.get(ch) == "N":
            rarity_map[ch] = "N-hira"
    
    # 常用漢字のNレアリティをN-kanjiに変更
    for ch in kanji_list:
        if rarity_map.get(ch) == "N":
            rarity_map[ch] = "N-kanji"
        
    return hiragana_list, katakana_list, kanji_list, numbers_list, rarity_map