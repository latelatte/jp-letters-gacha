#!/usr/bin/env python3
# 記号データの状況確認

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logics.char_loader import load_char_sets
import json
from pathlib import Path

hiragana_chars, katakana_chars, jouyou_chars, numbers_chars, rarity_map = load_char_sets()

print("記号データの状況確認")
print("=" * 40)

# symbols.jsonを直接読み込み
base = Path(__file__).parent / "assets"
with open(base / "symbols.json", encoding="utf-8") as f:
    symbols_data = json.load(f)

print(f"symbols.jsonの文字数: {len(symbols_data)}")
print(f"記号の一覧:")
symbol_chars = list(symbols_data.keys())
for i, char in enumerate(symbol_chars):
    rarity = symbols_data[char]
    print(f"  {i+1:2d}. {char} ({rarity})")

print(f"\nレアリティ分布:")
rarity_count = {}
for char, rarity in symbols_data.items():
    rarity_count[rarity] = rarity_count.get(rarity, 0) + 1

for rarity, count in sorted(rarity_count.items()):
    print(f"  {rarity}: {count}個")

print(f"\nrarity_mapでの記号:")
print("-" * 20)
symbol_in_map = 0
for char in symbol_chars:
    if char in rarity_map:
        print(f"  {char}: {rarity_map[char]}")
        symbol_in_map += 1

print(f"\nrarity_mapに含まれている記号: {symbol_in_map}/{len(symbol_chars)}")

# 記号がガチャで引けるかテスト
print(f"\n記号ガチャテスト:")
print("-" * 15)
from logics.gacha_utils import draw_weighted_char

symbol_drawn = 0
for i in range(20):
    char = draw_weighted_char()
    if char in symbol_chars:
        rarity = rarity_map.get(char, "Unknown")
        print(f"  {char} ({rarity}) が出現！")
        symbol_drawn += 1

print(f"\n20回中 {symbol_drawn} 回記号が出現")
