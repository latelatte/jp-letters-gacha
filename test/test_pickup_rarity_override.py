#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ピックアップガチャのレアリティオーバーライド機能をテストするスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Discord関連のモジュールをモックしてインポートエラーを回避
sys.modules['discord'] = type(sys)('discord')
sys.modules['discord.ui'] = type(sys)('discord.ui')

from logics.pickup_gacha import draw_pickup_char, load_pickup_config
from collections import defaultdict

def test_pickup_rarity_override(num_draws: int = 1000):
    """
    ピックアップガチャでレアリティオーバーライドが正しく動作するかテスト
    """
    print(f"ピックアップガチャ レアリティオーバーライドテスト: {num_draws:,} 回")
    print("=" * 60)
    
    # 設定情報を表示
    config = load_pickup_config()
    if not config:
        print("❌ イベント設定が読み込めませんでした")
        return
    
    print("📋 現在のイベント設定:")
    print(f"  タイトル: {config.get('title', 'N/A')}")
    print(f"  ピックアップ率: {config.get('pickup_rate_percentage', 'N/A')}%")
    
    rarity_overrides = config.get("rarity_overrides", {})
    if rarity_overrides:
        print(f"\n🎯 レアリティオーバーライド:")
        for char, rarity in sorted(rarity_overrides.items()):
            print(f"    {char} → {rarity}")
    else:
        print("\n⚠️  レアリティオーバーライドが設定されていません")
    
    print(f"\n🎲 {num_draws:,} 回ピックアップガチャテスト中...")
    
    # ガチャを引く
    results = defaultdict(int)
    char_results = defaultdict(int)
    
    for i in range(num_draws):
        if i % 100 == 0 and i > 0:
            print(f"  進捗: {i:,} / {num_draws:,} 回完了")
        
        try:
            char, rarity = draw_pickup_char()
            if char and rarity:
                results[rarity] += 1
                char_results[char] += 1
        except Exception as e:
            print(f"エラー発生: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("📊 ピックアップガチャテスト結果")
    print("=" * 60)
    
    total_draws = sum(results.values())
    print(f"実際に引けた回数: {total_draws:,} / {num_draws:,}")
    
    if total_draws == 0:
        print("❌ ガチャが引けませんでした。設定を確認してください。")
        return
    
    print(f"\n【レアリティ別排出結果】")
    for rarity in ["SSR", "SR", "R", "N"]:
        count = results.get(rarity, 0)
        percentage = (count / total_draws * 100) if total_draws > 0 else 0
        print(f"  {rarity:3}: {count:6,} 回 ({percentage:5.2f}%)")
    
    # ピックアップ文字の出現状況
    pickup_chars = set(config.get("characters", []))
    pickup_results = {char: char_results[char] for char in pickup_chars if char in char_results}
    
    print(f"\n【ピックアップ文字の出現状況】")
    total_pickup = sum(pickup_results.values())
    pickup_rate_actual = (total_pickup / total_draws * 100) if total_draws > 0 else 0
    print(f"  総ピックアップ出現: {total_pickup:,} 回 ({pickup_rate_actual:.2f}%)")
    print(f"  設定ピックアップ率: {config.get('pickup_rate_percentage', 'N/A')}%")
    
    print(f"\n【ピックアップ文字別詳細】")
    for char in sorted(pickup_chars):
        count = char_results.get(char, 0)
        percentage = (count / total_draws * 100) if total_draws > 0 else 0
        
        # オーバーライドされたレアリティを表示
        expected_rarity = rarity_overrides.get(char, "元の設定")
        print(f"  {char} ({expected_rarity}): {count:4} 回 ({percentage:.3f}%)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        test_pickup_rarity_override(int(sys.argv[1]))
    else:
        test_pickup_rarity_override(1000)
