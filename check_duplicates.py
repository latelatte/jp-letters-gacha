#!/usr/bin/env python3
# 数字と常用漢字の重複チェック

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logics.char_loader import load_char_sets

hiragana_chars, katakana_chars, jouyou_chars, numbers_chars, rarity_map = load_char_sets()

print("数字と常用漢字の重複チェック")
print("="*40)

# 数字文字セット
number_char_set = set(numbers_chars)
jouyou_char_set = set(jouyou_chars)

# 重複している文字を見つける
duplicates = number_char_set.intersection(jouyou_char_set)

print(f"数字文字数: {len(numbers_chars)}")
print(f"常用漢字数: {len(jouyou_chars)}")
print(f"重複文字数: {len(duplicates)}")
print()

if duplicates:
    print("重複している文字:")
    print("-" * 20)
    for char in sorted(duplicates):
        number_rarity = None
        jouyou_rarity = rarity_map.get(char, "Unknown")
        
        # numbers.jsonから該当文字のレアリティを取得
        import json
        from pathlib import Path
        base = Path(__file__).parent / "assets"
        with open(base / "numbers.json", encoding="utf-8") as f:
            numbers_data = json.load(f)
        
        for entry in numbers_data:
            if entry["character"] == char:
                number_rarity = entry["rarity"]
                break
        
        print(f"  {char}: 数字={number_rarity}, 常用漢字=N-kanji, 実際のrarity_map={jouyou_rarity}")

print("\nrarity_mapでの最終的な値:")
print("-" * 30)
for char in sorted(duplicates):
    print(f"  {char}: {rarity_map[char]}")

print("\n分析:")
print("-" * 10)
print("現在の実装では、rarity_mapに後から設定された値が優先されます。")
print("char_loader.pyの処理順序:")
print("1. numbers.jsonのレアリティが設定される")
print("2. gacha_utils.pyで常用漢字にN-kanjiが設定される（setdefault使用）")
print("3. setdefaultは既に値がある場合は上書きしないため、")
print("   重複文字は数字のレアリティが保持される")
