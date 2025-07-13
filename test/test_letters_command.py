#!/usr/bin/env python3
# lettersコマンドのテスト

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logics.char_loader import load_char_sets
import json
from pathlib import Path

print("lettersコマンドのテスト")
print("=" * 30)

# 文字セットの読み込み
hiragana_chars, katakana_chars, jouyou_chars, numbers_chars, rarity_map = load_char_sets()

# 記号の文字セットを作成
base = Path(__file__).parent / "assets"
with open(base / "symbols.json", encoding="utf-8") as f:
    symbols_data = json.load(f)
symbols_chars = list(symbols_data.keys())

print(f"ひらがな文字数: {len(hiragana_chars)}")
print(f"カタカナ文字数: {len(katakana_chars)}")
print(f"常用漢字数: {len(jouyou_chars)}")
print(f"数字文字数: {len(numbers_chars)}")
print(f"記号文字数: {len(symbols_chars)}")

# テスト用の文字コレクション
test_letters = ["あ", "ア", "漢", "5", "三", "。", "！", "京"]

print(f"\nテスト文字: {' '.join(test_letters)}")
print("-" * 20)

# 分類とソート（重複を避けるため優先順位で分類）
h = []
k = []
j = []
n = []
s = []

for c in test_letters:
    if c in numbers_chars:
        n.append(c)  # 数字が最優先
    elif c in symbols_chars:
        s.append(c)  # 次に記号
    elif c in hiragana_chars:
        h.append(c)  # ひらがな
    elif c in katakana_chars:
        k.append(c)  # カタカナ
    elif c in jouyou_chars:
        j.append(c)  # 漢字は最後

# ソート
h = sorted(h)
k = sorted(k)
j = sorted(j)
n = sorted(n)
s = sorted(s)

print("分類結果:")
if h: print(f"ひらがな：{' '.join(h)}")
if k: print(f"カタカナ：{' '.join(k)}")
if j: print(f"漢字：{' '.join(j)}")
if n: print(f"数字：{' '.join(n)}")
if s: print(f"記号：{' '.join(s)}")

print(f"\nレアリティチェック:")
for char in test_letters:
    rarity = rarity_map.get(char, "Unknown")
    char_type = ""
    if char in hiragana_chars:
        char_type = "ひらがな"
    elif char in katakana_chars:
        char_type = "カタカナ"
    elif char in jouyou_chars:
        char_type = "漢字"
    elif char in numbers_chars:
        char_type = "数字"
    elif char in symbols_chars:
        char_type = "記号"
    else:
        char_type = "不明"
    
    print(f"  {char}: {rarity} ({char_type})")
