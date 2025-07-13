# jp-letters-gacha

## ガチャボタン設定

ガチャボタンの表示文字列とメッセージは `assets/gacha_button_config.json` で管理されています。

### 設定項目

- `normal`: ノーマルガチャの設定
  - `single`: 単発ガチャボタンのラベル
  - `multi`: 10連ガチャボタンのラベル  
  - `message`: ガチャメッセージの内容
- `pickup`: ピックアップガチャの設定
  - `single`: 単発ガチャボタンのラベル
  - `multi`: 10連ガチャボタンのラベル
  - `message`: ガチャメッセージの内容
- `ssr`: SSR限定ガチャの設定
  - `single`: ガチャボタンのラベル
  - `message`: ガチャメッセージの内容

### 管理者コマンド

- `/set_gacha_config`: ガチャボタンの設定を変更
- `/show_gacha_config`: 現在のガチャボタン設定を表示

### 使用例

イベント期間中にピックアップガチャのボタンを変更したい場合：

```bash
/set_gacha_config mode:pickup button_type:single text:春祭り限定🌸
/set_gacha_config mode:pickup button_type:message text:🌸 春祭り限定ガチャ開催中！\n桜の文字が出やすくなってるよ✨
```

## Botメッセージ送信機能

管理者はBotに直接メッセージを送信させることができます。

### Botメッセージコマンド

- `/say`: Botに普通のメッセージを送信させる
- `/announce`: Botにお知らせ用の埋め込みメッセージを送信させる  
- `/event_announce`: イベント告知用の特別な埋め込みメッセージを送信させる

### Botメッセージ使用例

#### 普通のメッセージ

```bash
/say channel:#general message:こんにちは！今日も文字ガチャを楽しんでね〜 😊
```

#### お知らせメッセージ

```bash
/announce channel:#announcements title:メンテナンスのお知らせ description:明日の午前2時〜4時にメンテナンスを行います。ご了承ください。 color:FFFF00
```

#### イベント告知

```bash
/event_announce channel:#events event_title:春祭りガチャイベント event_description:桜をテーマにした特別なガチャイベントが開催中！ start_date:2024年3月20日 00:00 end_date:2024年3月31日 23:59 special_info:期間中は桜関連の文字が2倍出やすくなります🌸
```