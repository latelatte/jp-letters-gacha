#!/usr/bin/env python3
# 重複文字を常用漢字から除外する実装例

import json
from pathlib import Path

def remove_number_duplicates():
    """常用漢字辞書から数字と重複する文字を除外"""
    
    # ファイルパス
    base = Path("assets")
    jouyou_path = base / "jouyou_kanji.json"
    numbers_path = base / "numbers.json"
    backup_path = base / "jouyou_kanji_backup.json"
    
    # データ読み込み
    with open(jouyou_path, encoding="utf-8") as f:
        jouyou_data = json.load(f)
    
    with open(numbers_path, encoding="utf-8") as f:
        numbers_data = json.load(f)
    
    # 数字文字セット作成
    number_chars = {entry["character"] for entry in numbers_data}
    
    # バックアップ作成
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(jouyou_data, f, ensure_ascii=False, indent=4)
    
    # 重複文字を除外
    original_count = len(jouyou_data)
    filtered_jouyou = {k: v for k, v in jouyou_data.items() if k not in number_chars}
    new_count = len(filtered_jouyou)
    
    print(f"常用漢字から除外:")
    print(f"  元の文字数: {original_count}")
    print(f"  除外後: {new_count}")
    print(f"  除外した文字: {original_count - new_count}")
    print(f"  除外文字: {sorted(number_chars.intersection(set(jouyou_data.keys())))}")
    
    # 新しいファイルに保存
    with open(jouyou_path, "w", encoding="utf-8") as f:
        json.dump(filtered_jouyou, f, ensure_ascii=False, indent=4)
    
    print(f"\nバックアップ: {backup_path}")
    print(f"更新済み: {jouyou_path}")

if __name__ == "__main__":
    print("重複文字除去ツール")
    print("=" * 30)
    print("この処理により、常用漢字辞書から数字と重複する文字が除外されます。")
    print("バックアップが作成されるので、問題があれば復元できます。")
    print()
    
    response = input("実行しますか？ (y/N): ")
    if response.lower() == 'y':
        remove_number_duplicates()
        print("\n完了しました！")
    else:
        print("キャンセルしました。")
