# イベント設定テンプレート

新しいイベントを追加する際は、以下のような構造で events_config.json に追加してください：

```json
{
  "current_event": "新しいイベントのID",
  "events": {
    "新しいイベントのID": {
      "active": true,
      "start_date": "2025-08-01",
      "end_date": "2025-08-15",
      "title": "夏祭り特別ガチャ",
      "description": "夏祭りにちなんだ特別な文字がピックアップ！",
      "characters": [
        "祭", "夏", "花", "火"
      ],
      "event_exclusive": true,
      "exclude_from_normal_gacha": [
        "祭", "夏", "花", "火"
      ],
      "pickup_rate_percentage": 60.0
    }
  }
}
```

## フィールド説明

- `active`: イベントがアクティブかどうか
- `start_date`: イベント開始日 (YYYY-MM-DD形式)
- `end_date`: イベント終了日 (YYYY-MM-DD形式)  
- `title`: イベントタイトル
- `description`: イベント説明
- `characters`: ピックアップ対象の文字配列
- `event_exclusive`: true の場合、通常ガチャから除外される
- `exclude_from_normal_gacha`: 通常ガチャから除外する文字の配列
- `pickup_rate_percentage`: レアリティ内でのピックアップ確率（%、デフォルト: 50.0）

## 管理コマンド

- `/event_list` - 登録されているイベント一覧を表示
- `/event_switch [event_id]` - アクティブなイベントを切り替え
- `/event_disable` - すべてのイベントを無効化
- `/pickup_info` - 現在のピックアップガチャ情報を表示

## イベント追加の手順

1. `events_config.json` にイベント設定を追加
2. `/event_switch [event_id]` でイベントを有効化
3. 必要に応じて文字データ（rarity等）を更新
4. テスト実行して動作確認

これにより、コードを変更することなく新しいイベントを追加・管理できます。
