#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
イベント設定のレアリティオーバーライドをテストする簡易スクリプト
"""

import json
from pathlib import Path
from datetime import date

def test_rarity_override_config():
    """
    events_config.jsonのレアリティオーバーライド設定をテスト
    """
    print("📋 イベント設定のレアリティオーバーライドテスト")
    print("=" * 50)
    
    # イベント設定を読み込み
    events_config_path = Path("assets/events_config.json")
    if not events_config_path.exists():
        print("❌ events_config.json が見つかりません")
        return
    
    try:
        with open(events_config_path, encoding="utf-8") as f:
            events_data = json.load(f)
    except Exception as e:
        print(f"❌ 設定ファイルの読み込みエラー: {e}")
        return
    
    current_event_id = events_data.get("current_event")
    print(f"🎯 現在のイベント: {current_event_id}")
    
    if not current_event_id or current_event_id not in events_data.get("events", {}):
        print("❌ 現在のイベントが設定されていません")
        return
    
    event_config = events_data["events"][current_event_id]
    
    # イベント基本情報
    print(f"\n📅 イベント情報:")
    print(f"  タイトル: {event_config.get('title', 'N/A')}")
    print(f"  開始日: {event_config.get('start_date', 'N/A')}")
    print(f"  終了日: {event_config.get('end_date', 'N/A')}")
    print(f"  アクティブ: {event_config.get('active', False)}")
    print(f"  ピックアップ率: {event_config.get('pickup_rate_percentage', 'N/A')}%")
    
    # 期間チェック
    today = date.today()
    try:
        start = date.fromisoformat(event_config["start_date"])
        end = date.fromisoformat(event_config["end_date"])
        is_in_period = start <= today <= end
        print(f"  期間内: {is_in_period} (今日: {today})")
    except Exception as e:
        print(f"  期間チェックエラー: {e}")
        is_in_period = False
    
    # ピックアップ文字
    characters = event_config.get("characters", [])
    print(f"\n🎯 ピックアップ文字 ({len(characters)}文字):")
    print(f"  {', '.join(characters)}")
    
    # レアリティオーバーライド
    rarity_overrides = event_config.get("rarity_overrides", {})
    if rarity_overrides:
        print(f"\n⭐ レアリティオーバーライド ({len(rarity_overrides)}文字):")
        
        # レアリティ別に分類して表示
        by_rarity = {}
        for char, rarity in rarity_overrides.items():
            if rarity not in by_rarity:
                by_rarity[rarity] = []
            by_rarity[rarity].append(char)
        
        for rarity in ["N", "R", "SR", "SSR"]:
            if rarity in by_rarity:
                chars = ', '.join(by_rarity[rarity])
                print(f"    {rarity}: {chars}")
        
        # 元の設定と比較（numbers.jsonから）
        print(f"\n🔄 元の設定との比較:")
        try:
            with open("assets/numbers.json", encoding="utf-8") as f:
                numbers_data = json.load(f)
            
            original_rarities = {}
            for entry in numbers_data:
                if entry["character"] in rarity_overrides:
                    original_rarities[entry["character"]] = entry.get("rarity", "N")
            
            for char in sorted(rarity_overrides.keys()):
                original = original_rarities.get(char, "未設定")
                override = rarity_overrides[char]
                status = "変更" if original != override else "同じ"
                print(f"    {char}: {original} → {override} ({status})")
                
        except Exception as e:
            print(f"    元設定の読み込みエラー: {e}")
    else:
        print(f"\n⚠️  レアリティオーバーライドが設定されていません")
    
    # テスト用サンプル排出
    print(f"\n🎲 排出テスト（レアリティ重み考慮なし）:")
    rarity_counts = {}
    for char, rarity in rarity_overrides.items():
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
    
    for rarity, count in sorted(rarity_counts.items()):
        percentage = (count / len(rarity_overrides)) * 100
        print(f"    {rarity}: {count}文字 ({percentage:.1f}%)")
    
    print(f"\n✅ 設定テスト完了")

if __name__ == "__main__":
    test_rarity_override_config()
