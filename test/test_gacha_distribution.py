#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ガチャのレアリティ分布をテストするスクリプト
実際のガチャロジックを使って大量にガチャを引いて、レアリティ分布が期待通りか確認する
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logics.gacha_utils import draw_weighted_char, RARITY_WEIGHTS
from logics.char_loader import load_char_sets
from collections import defaultdict

def test_gacha_distribution(num_draws: int = 10000):
    """
    指定回数ガチャを引いて、レアリティ分布をテストする
    """
    print(f"ガチャテスト開始: {num_draws:,} 回抽選")
    print("=" * 50)
    
    # ガチャの設定情報を表示
    _, _, _, _, rarity_map = load_char_sets()
    
    print("現在の重み設定:")
    for rarity, weight in RARITY_WEIGHTS.items():
        print(f"  {rarity}: {weight}")
    
    print(f"\nレアリティマップ内の文字数:")
    rarity_counts_in_map = defaultdict(int)
    for char, rarity in rarity_map.items():
        rarity_counts_in_map[rarity] += 1
    
    for rarity, count in sorted(rarity_counts_in_map.items()):
        print(f"  {rarity}: {count} 文字")
    
    print(f"\n{num_draws:,} 回ガチャを実行中...")
    
    # ガチャを引く
    draw_counts = defaultdict(int)
    char_frequency = defaultdict(int)
    
    for i in range(num_draws):
        if i % 1000 == 0 and i > 0:
            print(f"  進捗: {i:,} / {num_draws:,} 回完了")
        
        try:
            char = draw_weighted_char()
            rarity = rarity_map.get(char, "Unknown")
            draw_counts[rarity] += 1
            char_frequency[char] += 1
        except Exception as e:
            print(f"エラー発生: {e}")
            continue
    
    print("\n" + "=" * 50)
    print("ガチャテスト結果")
    print("=" * 50)
    
    # 結果の分析
    total_draws = sum(draw_counts.values())
    print(f"実際に引けた回数: {total_draws:,} / {num_draws:,}")
    
    print(f"\n【レアリティ別排出結果】")
    for rarity in ["SSR", "SR", "R", "N", "N-hira", "N-kanji"]:
        count = draw_counts.get(rarity, 0)
        percentage = (count / total_draws * 100) if total_draws > 0 else 0
        print(f"  {rarity:8}: {count:6,} 回 ({percentage:5.2f}%)")
    
    # その他のレアリティがあれば表示
    other_rarities = set(draw_counts.keys()) - {"SSR", "SR", "R", "N", "N-hira", "N-kanji"}
    if other_rarities:
        print(f"\n【その他のレアリティ】")
        for rarity in sorted(other_rarities):
            count = draw_counts[rarity]
            percentage = (count / total_draws * 100) if total_draws > 0 else 0
            print(f"  {rarity:8}: {count:6,} 回 ({percentage:5.2f}%)")
    
    # 最も多く出た文字と最も少なく出た文字
    print(f"\n【文字別排出頻度 (上位10文字)】")
    sorted_chars = sorted(char_frequency.items(), key=lambda x: x[1], reverse=True)
    for i, (char, count) in enumerate(sorted_chars[:10]):
        rarity = rarity_map.get(char, "Unknown")
        percentage = (count / total_draws * 100) if total_draws > 0 else 0
        print(f"  {i+1:2}. {char} ({rarity}): {count} 回 ({percentage:.3f}%)")
    
    print(f"\n【最も出にくかった文字 (下位10文字)】")
    for i, (char, count) in enumerate(sorted_chars[-10:]):
        rarity = rarity_map.get(char, "Unknown")
        percentage = (count / total_draws * 100) if total_draws > 0 else 0
        print(f"  {char} ({rarity}): {count} 回 ({percentage:.3f}%)")
    
    # SSR文字が実際に出たかチェック
    ssr_chars_drawn = {char for char, count in char_frequency.items() 
                      if rarity_map.get(char) == "SSR" and count > 0}
    total_ssr_chars = len([char for char, rarity in rarity_map.items() if rarity == "SSR"])
    
    print(f"\n【SSR文字の出現状況】")
    print(f"  SSR総数: {total_ssr_chars} 文字")
    print(f"  実際に出たSSR: {len(ssr_chars_drawn)} 文字")
    print(f"  SSR出現率: {len(ssr_chars_drawn)/total_ssr_chars*100:.1f}%")
    
    if ssr_chars_drawn:
        print(f"  出たSSR文字: {', '.join(sorted(ssr_chars_drawn))}")

def quick_test():
    """簡易テスト: 100回だけ引いて動作確認"""
    print("簡易テスト: 100回ガチャ")
    test_gacha_distribution(100)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            quick_test()
        elif sys.argv[1].isdigit():
            test_gacha_distribution(int(sys.argv[1]))
        else:
            print("使用方法:")
            print("  python test_gacha_distribution.py        # 10,000回テスト")
            print("  python test_gacha_distribution.py quick  # 100回テスト")
            print("  python test_gacha_distribution.py 1000   # 1,000回テスト")
    else:
        # デフォルトは10,000回
        test_gacha_distribution(10000)
