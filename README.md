# ことのは(仮)

**ことのは(仮)** は、Discord上で遊べる「文字ガチャ」ボットです。  
ひらがな・カタカナ・漢字など、日本語の文字をコレクションするという、  
ソシャゲ風のガチャ体験を楽しめます。

## 主な機能

- **ポイント製ガチャ機能**：ポイントを貯めて文字のガチャができます。ポイントはログインボーナスやミッションをこなすことで貯めることができます。
- **文字ガチャ**：N〜SSRまで、レアリティ付きで文字が排出されます。
- **ピックアップガチャ**：期間限定イベントで特定の文字が出やすくなります。
- **ガチャボタンのカスタマイズ**：管理者コマンドでボタンの表示や文言を自由に変更。
- **検閲チャット (ことのは狩り)**：持っている文字以外は使えないテキストチャンネルを作成し、チャットを楽しむことができます。持っていない文字が文の中に含まれていた場合、その旨が通知され、送信したメッセージは即座に消去されます。
- **Botメッセージ機能**：お知らせやイベント告知などをBotから投稿可能。
- **データ永続化**：Herokuなどの制限を回避し、GitHub Gistにユーザーデータを保存。

---

## セットアップ

### 1. クローン & 依存ライブラリのインストール

```bash
git clone https://github.com/latelatte/kotonoha.git
cd kotonoha
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## データの永続化（Heroku対応）

webデプロイ時でのエフェメラルファイルシステムでもデータが永続化されるよう、GitHub Gistを使用してユーザーデータを保存しています。

### 環境変数の設定

`.env`ファイルに以下の環境変数を設定してください：

```env
GITHUB_TOKEN='あなたのGitHubアクセストークン'
GIST_ID='あなたのGitHub Gist ID'
```

GitHubアクセストークンについては、スコープでgistにチェックを入れてください。

GistのIDについては、作成したGistのURLから ID を取得してください。
`https://gist.github.com/username/ここがGist_ID`

## ガチャボタン設定

ボタンの表示名やメッセージは `assets/gacha_button_config.json` で管理されています。

- `normal`: 通常ガチャ
- `pickup`: ピックアップガチャ
- `ssr`: SSR限定ガチャ

### 管理者コマンド例

```bash
/set_gacha_config mode:pickup button_type:single text:春祭り限定🌸
/set_gacha_config mode:pickup button_type:message text:🌸 春祭り限定ガチャ開催中！
```

---

## 📢 Botメッセージ送信コマンド

- `/say`: 通常メッセージ
- `/announce`: 埋め込みお知らせ
- `/event_announce`: 特別イベント告知

使用例：

```bash
/event_announce channel:#event event_title:春祭り event_description:桜テーマのガチャ登場！ ...
```

---

## 👤 開発者

- 🧑‍💻 [latelatte](https://github.com/latelatte)
- 🍵 普段のチャットをより面白くする和製ソシャゲ風文字コレクションBotです。

---

## 📝 ライセンス

このプロジェクトは [MIT License](LICENSE) の下でライセンスされています。
