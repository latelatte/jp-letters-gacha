# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import CheckFailure
from typing import Literal
import json
from pathlib import Path

ASSETS_DIR = Path("./assets")
ASSETS_DIR.mkdir(exist_ok=True)

from logics.data_manager import get_user_data, update_user_data, set_current_answer
from views.gacha_view import GachaView

# 管理者用コマンド群
class AdminCommands(commands.Cog):
    @app_commands.command(name="setup_login_channel", description="ログインボタンをこのチャンネルに設置します（管理者用）")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_login_channel(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="ログインボーナスを受け取る", custom_id="login_bonus_button", style=discord.ButtonStyle.success))
        await interaction.response.send_message(
            "📝 このチャンネルはログイン確認専用です。\n以下のボタンからログインボーナスを受け取ってください！",
            view=view,
            ephemeral=False
        )
    def __init__(self, bot):
        self.bot = bot

    # 管理者用: 任意でポイント増減
    @commands.command(name="add")
    @commands.has_permissions(administrator=True)
    async def add_point(self, ctx, amount: int):
        # 指定があればその人に、なければ自分に
        target = ctx.message.mentions[0] if ctx.message.mentions else ctx.author
        user = get_user_data(target.id)
        user["points"] += amount
        update_user_data(target.id, user)

        await ctx.send(f"{target.mention} のポイントを {amount:+} 変動しました！(現在: {user['points']}pt / SSR限定: {user.get('ssr_points', 0)}pt)")

    @add_point.error
    async def add_point_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            await ctx.send("🚫 このコマンドは管理者しか使えないよ〜")

    # 管理者用: SSR限定ポイント増減
    @commands.command(name="addssr")
    @commands.has_permissions(administrator=True)
    async def add_ssr_point(self, ctx, amount: int):
        # 指定があればその人に、なければ自分に
        target = ctx.message.mentions[0] if ctx.message.mentions else ctx.author
        user = get_user_data(target.id)
        
        # SSR限定ポイントを初期化（存在しない場合）
        if "ssr_points" not in user:
            user["ssr_points"] = 0
        
        user["ssr_points"] += amount
        update_user_data(target.id, user)

        await ctx.send(f"{target.mention} のSSR限定ポイントを {amount:+} 変動しました！(現在: {user['points']}pt / SSR限定: {user['ssr_points']}pt)")

    @add_ssr_point.error
    async def add_ssr_point_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            await ctx.send("🚫 このコマンドは管理者しか使えないよ〜")

    @app_commands.command(name="points", description="現在のポイントを確認するよ！")
    async def points(self, interaction: discord.Interaction):
        user_data = get_user_data(interaction.user.id)
        await interaction.response.send_message(
            f"💠 {interaction.user.display_name} の所持ポイント：**{user_data['points']}pt** / SSR限定: **{user_data.get('ssr_points', 0)}pt**", 
            ephemeral=True
        )

    @app_commands.command(name="sync", description="スラッシュコマンドを同期するよ（管理者専用）")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def sync_commands(self, interaction: discord.Interaction):
        synced = await self.bot.tree.sync()
        await interaction.response.send_message(f"✅ コマンド {len(synced)} 件を同期したよ〜", ephemeral=True)

    @app_commands.command(name="post_gacha_buttons", description="指定チャンネルにガチャボタン常設メッセージを送る（管理者専用）")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="ガチャポストを送信するチャンネル", mode="ガチャボタンのモード (normal/pickup/ssr)")
    async def post_gacha_buttons(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        mode: Literal["normal", "pickup", "ssr"] = "normal"
    ):
        view = GachaView(mode)
        message = view.get_message()
        await channel.send(message, view=view)
        await interaction.response.send_message(f"✅ ガチャポストを {channel.mention} に送信しました", ephemeral=True)

    @app_commands.command(name="set_answer", description="ミッションの正解を設定する（管理者専用）")
    @app_commands.describe(answer="新しい正解文字列")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def set_answer(self, interaction: discord.Interaction, answer: str):
        answer = answer.strip()
        set_current_answer(answer)
        await interaction.response.send_message(f"✅ 新しい正解を設定したよ：**{answer}**", ephemeral=True)

    @set_answer.error
    async def set_answer_error(self, interaction: discord.Interaction, error):
        if isinstance(error, CheckFailure):
            await interaction.response.send_message("🚫 このコマンドは管理者しか使えないよ〜", ephemeral=True)


    @app_commands.command(name="set_channel", description="ミッションや制限チャンネルのIDを設定（管理者専用）")
    @app_commands.describe(kind="設定するチャンネルの種類", channel="設定したいチャンネル")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(self, interaction: discord.Interaction, kind: Literal["mission", "restricted"], channel: discord.TextChannel):
        config_path = Path("./assets/channel_config.json")
        config = {}
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
                config = json.load(f)

        key = "mission_channel_id" if kind == "mission" else "restricted_channel_id"
        config[key] = channel.id

        with config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        await interaction.response.send_message(f"✅ `{kind}` チャンネルを {channel.mention} に設定したよ〜", ephemeral=True)

    @app_commands.command(name="set_gacha_config", description="ガチャボタンの表示文字列を設定（管理者専用）")
    @app_commands.describe(
        mode="ガチャのモード (normal/pickup/ssr)",
        button_type="ボタンの種類 (single/multi/message)",
        text="設定したいテキスト"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def set_gacha_config(
        self,
        interaction: discord.Interaction,
        mode: Literal["normal", "pickup", "ssr"],
        button_type: Literal["single", "multi", "message"],
        text: str
    ):
        config_path = Path("./assets/gacha_button_config.json")
        config = {}
        
        # 既存の設定を読み込み
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            # デフォルト設定を作成
            config = {
                "normal": {
                    "single": "ガチャ🎯",
                    "multi": "10連🔥",
                    "message": "🎯 ガチャを引こう！\n下のボタンからいつでもガチャを引けるよ👇"
                },
                "pickup": {
                    "single": "ピックアップ🎯",
                    "multi": "ピックアップ10連🔥",
                    "message": "🌟 ピックアップガチャ開催中！\n特定の文字が出やすくなってるよ✨"
                },
                "ssr": {
                    "single": "SSR限定💎",
                    "message": "💎 SSR限定ガチャ！\nSSR限定ポイントでレア文字をゲットしよう🔥"
                }
            }

        # SSRガチャにmultiボタンはないため、チェック
        if mode == "ssr" and button_type == "multi":
            await interaction.response.send_message("❌ SSRガチャには10連ボタンがありません", ephemeral=True)
            return

        # 設定を更新
        if mode not in config:
            config[mode] = {}
        config[mode][button_type] = text

        # ファイルに保存
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        await interaction.response.send_message(
            f"✅ `{mode}` ガチャの `{button_type}` を「**{text}**」に設定しました", 
            ephemeral=True
        )

    @app_commands.command(name="show_gacha_config", description="現在のガチャボタン設定を表示（管理者専用）")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def show_gacha_config(self, interaction: discord.Interaction):
        config_path = Path("./assets/gacha_button_config.json")
        
        if not config_path.exists():
            await interaction.response.send_message("❌ ガチャボタン設定ファイルが見つかりません", ephemeral=True)
            return

        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)

        embed = discord.Embed(title="📋 ガチャボタン設定", color=0x00ff00)
        
        for mode, settings in config.items():
            mode_text = {
                "normal": "ノーマルガチャ",
                "pickup": "ピックアップガチャ", 
                "ssr": "SSR限定ガチャ"
            }.get(mode, mode)
            
            field_value = ""
            if "single" in settings:
                field_value += f"単発: `{settings['single']}`\n"
            if "multi" in settings:
                field_value += f"10連: `{settings['multi']}`\n"
            if "message" in settings:
                field_value += f"メッセージ: `{settings['message']}`"
            
            embed.add_field(name=mode_text, value=field_value, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="say", description="Botにメッセージを送信させる（管理者専用）")
    @app_commands.describe(
        channel="メッセージを送信するチャンネル",
        message="Botに送信させるメッセージ内容（\\nで改行、**太字**、*斜体*、~~取り消し~~対応）",
        as_embed="埋め込みメッセージとして送信するか（デフォルト: False）"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def say(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str,
        as_embed: bool = False
    ):
        # エスケープ文字を処理
        processed_message = self._process_message_formatting(message)
        
        if as_embed:
            # 埋め込みメッセージとして送信
            embed = discord.Embed(
                description=processed_message,
                color=0x00BFFF  # 青色
            )
            embed.set_footer(text="🤖 Bot メッセージ")
            await channel.send(embed=embed)
        else:
            # 通常のメッセージとして送信
            await channel.send(processed_message)
        
        await interaction.response.send_message(
            f"✅ {channel.mention} にメッセージを送信しました", 
            ephemeral=True
        )

    def _process_message_formatting(self, message: str) -> str:
        """メッセージの装飾処理を行う"""
        # 改行の処理（複数のパターンに対応）
        processed = message
        
        # 様々な改行パターンに対応
        processed = processed.replace("\\n", "\n")      # \n → 改行
        processed = processed.replace("\\\\n", "\n")    # \\n → 改行 (ダブルエスケープ)
        processed = processed.replace("<br>", "\n")     # HTML風の改行
        processed = processed.replace("[改行]", "\n")    # 日本語での明示的な改行
        processed = processed.replace("[br]", "\n")     # 短縮形
        
        # その他のエスケープ文字
        processed = processed.replace("\\t", "\t")      # タブ
        processed = processed.replace("\\\"", "\"")     # ダブルクォート
        processed = processed.replace("\\'", "'")       # シングルクォート
        
        # 特殊文字の置き換え
        processed = processed.replace("[tab]", "\t")    # 明示的なタブ
        processed = processed.replace("　", " ")        # 全角スペースを半角に（オプション）
        
        # バックスラッシュの処理は最後に（他の処理を邪魔しないように）
        processed = processed.replace("\\\\", "\\")
        
        return processed

    @app_commands.command(name="announce", description="Botに埋め込みメッセージでお知らせを送信させる（管理者専用）")
    @app_commands.describe(
        channel="お知らせを送信するチャンネル",
        title="お知らせのタイトル（\\nで改行可能）",
        description="お知らせの内容（\\nで改行、**太字**、*斜体*、~~取り消し~~対応）",
        color="埋め込みの色（16進数、例: FF0000）"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        description: str,
        color: str = "00FF00"
    ):
        try:
            # 色コードを16進数に変換
            color_int = int(color.replace("#", ""), 16)
        except ValueError:
            color_int = 0x00FF00  # デフォルトは緑色

        # タイトルと説明文を処理
        processed_title = self._process_message_formatting(title)
        processed_description = self._process_message_formatting(description)

        # 埋め込みメッセージを作成
        embed = discord.Embed(
            title=processed_title,
            description=processed_description,
            color=color_int
        )
        embed.set_footer(text="🤖 Bot からのお知らせ")

        # Botとして埋め込みメッセージを送信
        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ {channel.mention} にお知らせを送信しました", 
            ephemeral=True
        )

    @app_commands.command(name="event_announce", description="イベント告知用の特別な埋め込みメッセージを送信（管理者専用）")
    @app_commands.describe(
        channel="イベント告知を送信するチャンネル",
        event_title="イベント名（\\nで改行可能）",
        event_description="イベントの説明（\\nで改行、**太字**、*斜体*、~~取り消し~~対応）",
        start_date="開始日時（例: 2024年12月25日 00:00）",
        end_date="終了日時（例: 2024年12月31日 23:59）",
        special_info="特別な情報やボーナス内容など（装飾対応）"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def event_announce(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        event_title: str,
        event_description: str,
        start_date: str = "",
        end_date: str = "",
        special_info: str = ""
    ):
        # テキストを処理
        processed_title = self._process_message_formatting(event_title)
        processed_description = self._process_message_formatting(event_description)
        processed_special_info = self._process_message_formatting(special_info) if special_info else ""
        
        # イベント用の特別な埋め込みメッセージを作成
        embed = discord.Embed(
            title=f"🎉 {processed_title}",
            description=processed_description,
            color=0xFF6B35  # オレンジ色
        )

        if start_date:
            embed.add_field(name="📅 開始日時", value=start_date, inline=True)
        if end_date:
            embed.add_field(name="🏁 終了日時", value=end_date, inline=True)
        if special_info:
            embed.add_field(name="✨ 特別情報", value=processed_special_info, inline=False)

        embed.set_footer(text="🎊 みんなでイベントを楽しもう！")

        # Botとしてイベント告知を送信
        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ {channel.mention} にイベント告知を送信しました", 
            ephemeral=True
        )

    @app_commands.command(name="rich_message", description="高度な装飾付きメッセージを送信（管理者専用）")
    @app_commands.describe(
        channel="メッセージを送信するチャンネル",
        title="メッセージのタイトル（空欄可、装飾対応）",
        content="メッセージの内容（\\nで改行、**太字**、*斜体*、~~取り消し~~対応）",
        color="埋め込みの色（16進数、例: FF0000、デフォルト: 00BFFF）",
        image_url="画像のURL（空欄可）",
        thumbnail_url="サムネイル画像のURL（空欄可）",
        footer_text="フッターテキスト（空欄可、装飾対応）"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def rich_message(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        content: str,
        title: str = "",
        color: str = "00BFFF",
        image_url: str = "",
        thumbnail_url: str = "",
        footer_text: str = ""
    ):
        try:
            # 色コードを16進数に変換
            color_int = int(color.replace("#", ""), 16)
        except ValueError:
            color_int = 0x00BFFF  # デフォルトは青色

        # テキストを処理
        processed_content = self._process_message_formatting(content)
        processed_title = self._process_message_formatting(title) if title else None
        processed_footer = self._process_message_formatting(footer_text) if footer_text else None

        # 埋め込みメッセージを作成
        embed = discord.Embed(
            title=processed_title,
            description=processed_content,
            color=color_int
        )

        # 画像とサムネイルを設定
        if image_url:
            try:
                embed.set_image(url=image_url)
            except Exception:
                pass  # 無効なURLの場合は無視
                
        if thumbnail_url:
            try:
                embed.set_thumbnail(url=thumbnail_url)
            except Exception:
                pass  # 無効なURLの場合は無視

        # フッターを設定
        if processed_footer:
            embed.set_footer(text=processed_footer)
        else:
            embed.set_footer(text="🤖 Bot メッセージ")

        # Botとして埋め込みメッセージを送信
        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ {channel.mention} に装飾メッセージを送信しました", 
            ephemeral=True
        )

    @app_commands.command(name="message_help", description="メッセージ装飾の使い方を表示（管理者専用）")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def message_help(self, interaction: discord.Interaction):
        """メッセージ装飾機能の使い方を表示"""
        help_text = r"""
        
**📝 改良版メッセージコマンドの使い方**

**改行の方法（複数対応）:**
• `\n` → 改行（基本）
• `<br>` → 改行（HTML風）
• `[改行]` → 改行（日本語）
• `[br]` → 改行（短縮）

**基本的な装飾記法:**
• `**太字**` → **太字**
• `*斜体*` → *斜体*
• `~~取り消し~~` → ~~取り消し~~
• `` `コード` `` → `コード`
• `` ```コードブロック``` `` → コードブロック

**特殊文字:**
• `\t` または `[tab]` → タブ文字
• `\"` → ダブルクォート
• `\'` → シングルクォート

**利用可能なコマンド:**

🔹 **`/say`** - 基本的なメッセージ送信
• `as_embed: True` で埋め込み形式で送信可能

🔹 **`/announce`** - タイトル付きお知らせ
• 色指定可能（16進数、例: FF0000）

🔹 **`/rich_message`** - 高度な装飾メッセージ
• 画像・サムネイル対応
• カスタムフッター設定可能

🔹 **`/event_announce`** - イベント告知専用
• 開始・終了日時の専用フィールド

🔹 **`/test_formatting`** - 装飾テスト
• 処理結果をプレビュー確認可能

**使用例:**
```
/say channel:#general message:こんにちは！\n**今日は良い天気ですね**\n*お疲れ様です* as_embed:True
```

または

```
/say channel:#general message:こんにちは！[改行]**重要**[改行]よろしくお願いします
```

**注意事項:**
• 複数の改行方法が使用可能です
• 埋め込みメッセージでは一部制限があります
• `/test_formatting` で動作確認ができます
• 管理者権限が必要です
        """
        
        embed = discord.Embed(
            title="📚 メッセージ装飾ガイド",
            description=help_text.strip(),
            color=0x7289DA
        )
        embed.set_footer(text="💡 うまく改行できない場合は /test_formatting でテストしてください")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="test_formatting", description="メッセージ装飾のテスト（管理者専用）")
    @app_commands.describe(
        test_message="テストしたいメッセージ（装飾記法を含む）"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def test_formatting(self, interaction: discord.Interaction, test_message: str):
        """メッセージ装飾のテスト用コマンド"""
        
        # 元のメッセージを表示
        original_repr = repr(test_message)
        
        # 処理後のメッセージ
        processed = self._process_message_formatting(test_message)
        processed_repr = repr(processed)
        
        # 結果をembedで表示
        embed = discord.Embed(
            title="🔧 メッセージ装飾テスト結果",
            color=0xFFD700
        )
        
        embed.add_field(
            name="📥 入力されたメッセージ",
            value=f"```\n{original_repr}\n```",
            inline=False
        )
        
        embed.add_field(
            name="📤 処理後のメッセージ（内部表現）",
            value=f"```\n{processed_repr}\n```",
            inline=False
        )
        
        embed.add_field(
            name="👁️ 表示プレビュー",
            value=processed,
            inline=False
        )
        
        embed.set_footer(text="💡 このコマンドで改行が正しく処理されているか確認できます")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Cogとして登録
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))