#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
漢字のレアリティを自動で分類するスクリプト
画数、学年、頻度、JLPTレベルなどを総合的に考慮してレアリティを決定する
"""

import json
from typing import Dict, Any

def calculate_kanji_rarity(kanji_data: Dict[str, Any]) -> str:
    """
    漢字のデータを元にレアリティを計算する
    
    Args:
        kanji_data: 漢字の詳細データ
        
    Returns:
        "N", "R", "SR", "SSR" のいずれか
    """
    strokes = kanji_data.get("strokes", 0)
    grade = kanji_data.get("grade", 10)  # gradeがない場合は10（高校レベル）とする
    freq = kanji_data.get("freq")  # 頻度
    if freq is None:
        freq = 9999  # データがない場合は低頻度とする
    jlpt_new = kanji_data.get("jlpt_new")  # JLPTレベル（5が最易、1が最難）
    if jlpt_new is None:
        jlpt_new = 1  # データがない場合は最難とする
    
    # スコアベースでレアリティを決定
    # より複雑で珍しい漢字ほど高レアリティになる
    score = 0
    
    # 画数による加点（画数が多いほど高レア）
    if strokes <= 3:
        score += 0
    elif strokes <= 6:
        score += 1
    elif strokes <= 9:
        score += 2
    elif strokes <= 12:
        score += 3
    elif strokes <= 15:
        score += 4
    else:
        score += 5
    
    # 学年による加点（高学年ほど高レア）
    if grade <= 2:
        score += 0
    elif grade <= 4:
        score += 1
    elif grade <= 6:
        score += 2
    elif grade <= 9:  # 中学生
        score += 3
    else:  # 高校生以上
        score += 4
    
    # 頻度による加点（低頻度ほど高レア）
    if freq <= 100:
        score += 0
    elif freq <= 500:
        score += 1
    elif freq <= 1000:
        score += 2
    elif freq <= 2000:
        score += 3
    else:
        score += 4
    
    # JLPTレベルによる加点（低レベル（難しい）ほど高レア）
    if jlpt_new >= 4:  # N4, N5
        score += 0
    elif jlpt_new == 3:  # N3
        score += 1
    elif jlpt_new == 2:  # N2
        score += 2
    else:  # N1 or なし
        score += 3
    
    # スコアに基づいてレアリティを決定
    # 理想的なピラミッド型の分布を目指す
    if score <= 9:
        return "N"
    elif score <= 12:
        return "R"
    elif score <= 14:
        return "SR"
    else:
        return "SSR"

def update_rarity_map():
    """
    常用漢字のデータを読み込んで、レアリティマップを更新する
    """
    print("漢字データを読み込み中...")
    
    # 常用漢字データを読み込み
    with open("assets/jouyou_kanji.json", "r", encoding="utf-8") as f:
        kanji_data = json.load(f)
    
    # 既存のレアリティマップを読み込み
    try:
        with open("assets/rarity_map.json", "r", encoding="utf-8") as f:
            rarity_map = json.load(f)
    except FileNotFoundError:
        rarity_map = {}
    
    print(f"総漢字数: {len(kanji_data)}")
    
    # 各漢字のレアリティを計算
    rarity_counts = {"N": 0, "R": 0, "SR": 0, "SSR": 0}
    new_entries = 0
    updated_entries = 0
    
    for kanji, data in kanji_data.items():
        old_rarity = rarity_map.get(kanji)
        new_rarity = calculate_kanji_rarity(data)
        
        if old_rarity is None:
            new_entries += 1
        elif old_rarity != new_rarity:
            updated_entries += 1
            print(f"変更: {kanji} {old_rarity} -> {new_rarity} (画数:{data.get('strokes')}, 学年:{data.get('grade')}, 頻度:{data.get('freq')})")
        
        rarity_map[kanji] = new_rarity
        rarity_counts[new_rarity] += 1
    
    # バックアップを作成
    try:
        with open("assets/rarity_map.json.backup", "w", encoding="utf-8") as f:
            json.dump(rarity_map, f, ensure_ascii=False, indent=2)
        print("バックアップを作成しました: assets/rarity_map.json.backup")
    except:
        print("バックアップの作成に失敗しましたが、処理を続行します")
    
    # 更新されたレアリティマップを保存
    with open("assets/rarity_map.json", "w", encoding="utf-8") as f:
        json.dump(rarity_map, f, ensure_ascii=False, indent=2)
    
    print("\n=== 更新結果 ===")
    print(f"新規追加: {new_entries} 文字")
    print(f"レアリティ変更: {updated_entries} 文字")
    print("\n=== レアリティ分布 ===")
    total = sum(rarity_counts.values())
    for rarity, count in rarity_counts.items():
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"{rarity}: {count} 文字 ({percentage:.1f}%)")
    
    print(f"\nレアリティマップを更新しました: assets/rarity_map.json")

def preview_rarity_distribution():
    """
    レアリティ分布をプレビューする（実際の更新は行わない）
    """
    print("レアリティ分布をプレビュー中...")
    
    with open("assets/jouyou_kanji.json", "r", encoding="utf-8") as f:
        kanji_data = json.load(f)
    
    rarity_counts = {"N": 0, "R": 0, "SR": 0, "SSR": 0}
    examples = {"N": [], "R": [], "SR": [], "SSR": []}
    
    for kanji, data in kanji_data.items():
        rarity = calculate_kanji_rarity(data)
        rarity_counts[rarity] += 1
        
        # 例として最初の5文字を保存
        if len(examples[rarity]) < 5:
            examples[rarity].append(f"{kanji}(画数:{data.get('strokes')},学年:{data.get('grade')},頻度:{data.get('freq')})")
    
    print("\n=== プレビュー結果 ===")
    total = sum(rarity_counts.values())
    for rarity, count in rarity_counts.items():
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"\n{rarity}: {count} 文字 ({percentage:.1f}%)")
        print(f"例: {', '.join(examples[rarity])}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        preview_rarity_distribution()
    else:
        print("漢字レアリティ自動分類スクリプト")
        print("='=" * 20)
        
        choice = input("実行モードを選択してください:\n1. プレビューのみ\n2. 実際に更新\n選択 (1/2): ")
        
        if choice == "1":
            preview_rarity_distribution()
        elif choice == "2":
            update_rarity_map()
        else:
            print("無効な選択です")
