#!/usr/bin/env python3
# 数字ガチャのテスト用スクリプト

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logics.gacha_utils import draw_weighted_char, rarity_map

print("数字ガチャのテスト:")
print("================")

# 10回ガチャを引いてみる
for i in range(10):
    char = draw_weighted_char()
    rarity = rarity_map.get(char, "Unknown")
    char_type = ""
    
    # 文字の種類を判定
    if char.isdigit():
        char_type = "アラビア数字"
    elif char in "零一二三四五六七八九十百千万億兆京垓":
        char_type = "漢数字"
    elif char in "壱弐参肆伍陸漆捌玖拾":
        char_type = "大字"
    else:
        char_type = "その他"
    
    print(f"{i+1:2d}. {char} ({rarity}) - {char_type}")

print("\n数字文字のレアリティ分布:")
print("========================")

number_chars = [ch for ch, _ in rarity_map.items() if ch.isdigit() or ch in "零一二三四五六七八九十百千万億兆京垓壱弐参肆伍陸漆捌玖拾"]
rarity_count = {}
for char in number_chars:
    rarity = rarity_map[char]
    rarity_count[rarity] = rarity_count.get(rarity, 0) + 1

for rarity, count in sorted(rarity_count.items()):
    print(f"{rarity}: {count}文字")
