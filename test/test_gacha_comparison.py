#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恒常ガチャとイベントガチャの排出率をシミュレートして比較するスクリプト
"""

import sys
import os
import json
from pathlib import Path
from collections import defaultdict

# Discordモジュールのモック
sys.modules['discord'] = type(sys)('discord')
sys.modules['discord.ui'] = type(sys)('discord.ui')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_normal_gacha(num_draws: int = 5000):
    """恒常ガチャのテスト"""
    from logics.gacha_utils import draw_weighted_char, RARITY_WEIGHTS
    from logics.char_loader import load_char_sets
    
    print(f"🎲 恒常ガチャシミュレーション ({num_draws:,} 回)")
    print("=" * 50)
    
    # ローマ数字が除外されているかチェック
    from logics.gacha_utils import get_event_excluded_chars
    excluded = get_event_excluded_chars()
    print(f"除外文字: {', '.join(sorted(excluded)) if excluded else 'なし'}")
    
    results = defaultdict(int)
    char_results = defaultdict(int)
    
    for i in range(num_draws):
        if i % 1000 == 0 and i > 0:
            print(f"  進捗: {i:,} / {num_draws:,}")
        
        try:
            char = draw_weighted_char()
            _, _, _, _, rarity_map = load_char_sets()
            rarity = rarity_map.get(char, "N-kanji")
            results[rarity] += 1
            char_results[char] += 1
        except Exception as e:
            print(f"エラー: {e}")
            continue
    
    total = sum(results.values())
    print(f"\n📊 恒常ガチャ結果 (総回数: {total:,})")
    
    # レアリティ別結果
    for rarity in ["SSR", "SR", "R", "N", "N-hira", "N-kanji"]:
        count = results.get(rarity, 0)
        percentage = (count / total * 100) if total > 0 else 0
        weight = RARITY_WEIGHTS.get(rarity, 0)
        print(f"  {rarity:8}: {count:6,} 回 ({percentage:5.2f}%) [重み: {weight}]")
    
    # ローマ数字が出ていないことを確認
    roman_chars = {"Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ", "Ⅺ", "Ⅻ"}
    roman_found = [char for char in roman_chars if char in char_results]
    print(f"\n🚫 ローマ数字排出確認: {len(roman_found)}文字出現 ({'除外成功' if len(roman_found) == 0 else '除外失敗'})")
    if roman_found:
        print(f"   出現したローマ数字: {', '.join(roman_found)}")
    
    return results, char_results

def test_pickup_gacha(num_draws: int = 5000):
    """ピックアップガチャのテスト"""
    print(f"\n🎯 ピックアップガチャシミュレーション ({num_draws:,} 回)")
    print("=" * 50)
    
    # イベント設定を読み込み
    events_config_path = Path("assets/events_config.json")
    with open(events_config_path, encoding="utf-8") as f:
        events_data = json.load(f)
    
    current_event = events_data["events"][events_data["current_event"]]
    pickup_chars = set(current_event["characters"])
    rarity_overrides = current_event.get("rarity_overrides", {})
    pickup_rate = current_event.get("pickup_rate_percentage", 70.0)
    
    print(f"ピックアップ文字: {', '.join(sorted(pickup_chars))}")
    print(f"ピックアップ率: {pickup_rate}%")
    print(f"レアリティオーバーライド: {len(rarity_overrides)}文字")
    
    # 手動でピックアップガチャの挙動をシミュレート
    from logics.gacha_utils import get_weight, RARITY_WEIGHTS
    from logics.char_loader import load_char_sets
    import random
    
    _, _, _, _, rarity_map = load_char_sets()
    
    results = defaultdict(int)
    char_results = defaultdict(int)
    pickup_draws = 0
    normal_draws = 0
    
    for i in range(num_draws):
        if i % 1000 == 0 and i > 0:
            print(f"  進捗: {i:,} / {num_draws:,}")
        
        # ピックアップ vs 恒常の判定
        if random.random() * 100 < pickup_rate:
            # ピックアップから抽選
            pickup_draws += 1
            
            # レアリティ別に分類
            pickup_by_rarity = defaultdict(list)
            for char in pickup_chars:
                rarity = rarity_overrides.get(char, rarity_map.get(char, "N"))
                pickup_by_rarity[rarity].append(char)
            
            # レアリティを重み付きで選択
            rarities = list(pickup_by_rarity.keys())
            weights = [get_weight(r) for r in rarities]
            selected_rarity = random.choices(rarities, weights=weights, k=1)[0]
            
            # そのレアリティから文字を選択
            char = random.choice(pickup_by_rarity[selected_rarity])
            final_rarity = rarity_overrides.get(char, rarity_map.get(char, "N"))
            
        else:
            # 恒常から抽選（ローマ数字除外）
            normal_draws += 1
            from logics.gacha_utils import draw_weighted_char
            char = draw_weighted_char()
            final_rarity = rarity_map.get(char, "N-kanji")
        
        results[final_rarity] += 1
        char_results[char] += 1
    
    total = sum(results.values())
    print(f"\n📊 ピックアップガチャ結果 (総回数: {total:,})")
    print(f"  ピックアップ抽選: {pickup_draws:,} 回 ({pickup_draws/total*100:.2f}%)")
    print(f"  恒常抽選: {normal_draws:,} 回 ({normal_draws/total*100:.2f}%)")
    
    # レアリティ別結果
    for rarity in ["SSR", "SR", "R", "N", "N-hira", "N-kanji"]:
        count = results.get(rarity, 0)
        percentage = (count / total * 100) if total > 0 else 0
        weight = RARITY_WEIGHTS.get(rarity, 0)
        print(f"  {rarity:8}: {count:6,} 回 ({percentage:5.2f}%) [重み: {weight}]")
    
    # ピックアップ文字の詳細
    print(f"\n🎯 ピックアップ文字詳細:")
    pickup_total = sum(char_results.get(char, 0) for char in pickup_chars)
    print(f"  総ピックアップ出現: {pickup_total:,} 回 ({pickup_total/total*100:.2f}%)")
    
    # レアリティオーバーライド別の出現状況
    by_override_rarity = defaultdict(list)
    for char in pickup_chars:
        override_rarity = rarity_overrides.get(char, "オーバーライドなし")
        count = char_results.get(char, 0)
        by_override_rarity[override_rarity].append((char, count))
    
    for rarity in ["N", "R", "SR", "SSR"]:
        if rarity in by_override_rarity:
            chars = by_override_rarity[rarity]
            total_count = sum(count for _, count in chars)
            print(f"\n  {rarity}設定の文字 (計{total_count:,}回):")
            for char, count in sorted(chars, key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                print(f"    {char}: {count:4} 回 ({percentage:.3f}%)")
    
    return results, char_results

def compare_gachas():
    """両ガチャの比較分析"""
    print("\n" + "=" * 70)
    print("🔍 設計意図の検証")
    print("=" * 70)
    
    print("📋 設計意図:")
    print("  1. 恒常ガチャ: ローマ数字は一切出ない")
    print("  2. ピックアップガチャ: ローマ数字が70%の確率で抽選対象")
    print("  3. Ⅰ,Ⅱ,Ⅲ を N に変更して出やすく")
    print("  4. Ⅹ,Ⅺ,Ⅻ は SSR のまま（レア感維持）")
    
    # 実際のテスト実行
    print("\n🧪 実証テスト開始...")
    
    normal_results, normal_chars = test_normal_gacha(5000)
    pickup_results, pickup_chars = test_pickup_gacha(5000)
    
    print("\n" + "=" * 70)
    print("📈 比較分析結果")
    print("=" * 70)
    
    # 1. ローマ数字除外の確認
    roman_chars = {"Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ", "Ⅺ", "Ⅻ"}
    normal_roman = sum(normal_chars.get(char, 0) for char in roman_chars)
    pickup_roman = sum(pickup_chars.get(char, 0) for char in roman_chars)
    
    print(f"1️⃣ ローマ数字除外検証:")
    print(f"   恒常ガチャ: {normal_roman} 回出現 ({'✅ 成功' if normal_roman == 0 else '❌ 失敗'})")
    print(f"   ピックアップ: {pickup_roman} 回出現 ({'✅ 期待通り' if pickup_roman > 0 else '❌ 出現なし'})")
    
    # 2. レアリティ分布の比較
    print(f"\n2️⃣ レアリティ分布比較:")
    normal_total = sum(normal_results.values())
    pickup_total = sum(pickup_results.values())
    
    for rarity in ["SSR", "SR", "R", "N"]:
        normal_pct = (normal_results.get(rarity, 0) / normal_total * 100) if normal_total > 0 else 0
        pickup_pct = (pickup_results.get(rarity, 0) / pickup_total * 100) if pickup_total > 0 else 0
        diff = pickup_pct - normal_pct
        
        print(f"   {rarity}: 恒常 {normal_pct:5.2f}% → ピックアップ {pickup_pct:5.2f}% ({diff:+.2f}%)")
    
    # 3. 1-3のローマ数字の出現確認
    easy_romans = {"Ⅰ", "Ⅱ", "Ⅲ"}
    hard_romans = {"Ⅹ", "Ⅺ", "Ⅻ"}
    
    easy_count = sum(pickup_chars.get(char, 0) for char in easy_romans)
    hard_count = sum(pickup_chars.get(char, 0) for char in hard_romans)
    
    print(f"\n3️⃣ Nレアリティ効果検証:")
    print(f"   Ⅰ,Ⅱ,Ⅲ (N設定): {easy_count} 回出現")
    print(f"   Ⅹ,Ⅺ,Ⅻ (SSR設定): {hard_count} 回出現")
    
    if easy_count > hard_count:
        print("   ✅ 設計通り: N設定の文字がSSR設定より多く出現")
    else:
        print("   ⚠️  要調査: SSR設定の文字の方が多く出現")
    
    print(f"\n🎯 総合評価:")
    success_count = 0
    total_checks = 3
    
    if normal_roman == 0:
        success_count += 1
        print("   ✅ 恒常ガチャでローマ数字除外")
    else:
        print("   ❌ 恒常ガチャでローマ数字が出現")
    
    if pickup_roman > 0:
        success_count += 1  
        print("   ✅ ピックアップガチャでローマ数字出現")
    else:
        print("   ❌ ピックアップガチャでローマ数字が出現せず")
    
    if easy_count > hard_count:
        success_count += 1
        print("   ✅ レアリティオーバーライド効果確認")
    else:
        print("   ❌ レアリティオーバーライド効果が不明確")
    
    print(f"\n🏆 設計意図達成度: {success_count}/{total_checks} ({success_count/total_checks*100:.0f}%)")

if __name__ == "__main__":
    compare_gachas()
