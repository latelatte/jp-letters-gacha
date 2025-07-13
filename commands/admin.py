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

from logics.data_manager import get_user_data, update_user_data
from views.gacha_view import GachaView

current_answer = ""

# 管理者用コマンド群
class AdminCommands(commands.Cog):
    @app_commands.command(name="setup_login_channel", description="ログインボタンをこのチャンネルに設置します（管理者用）")
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
    @commands.command(name="addpoint")
    @commands.has_permissions(administrator=True)
    async def add_point(self, ctx, amount: int):
        # 指定があればその人に、なければ自分に
        target = ctx.message.mentions[0] if ctx.message.mentions else ctx.author
        user = get_user_data(target.id)
        user["points"] += amount
        update_user_data(target.id, user)

        await ctx.send(f"{target.mention} のポイントを {amount:+} 変動しました！(現在: {user['points']}pt)")

    @add_point.error
    async def add_point_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            await ctx.send("🚫 このコマンドは管理者しか使えないよ〜")

    @app_commands.command(name="points", description="現在のポイントを確認するよ！")
    async def points(self, interaction: discord.Interaction):
        user_data = get_user_data(interaction.user.id)
        await interaction.response.send_message(
            f"💠 {interaction.user.display_name} の所持ポイント：**{user_data['points']}pt**", ephemeral=True
        )

    @app_commands.command(name="sync", description="スラッシュコマンドを同期するよ（管理者専用）")
    @app_commands.checks.has_permissions(administrator=True)
    async def sync_commands(self, interaction: discord.Interaction):
        synced = await self.bot.tree.sync()
        await interaction.response.send_message(f"✅ コマンド {len(synced)} 件を同期したよ〜", ephemeral=True)

    @app_commands.command(name="post_gacha_buttons", description="指定チャンネルにガチャボタン常設メッセージを送る（管理者専用）")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="ガチャポストを送信するチャンネル", mode="ガチャボタンのモード (normal/pickup/ssr)")
    async def post_gacha_buttons(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        mode: Literal["normal", "pickup", "ssr"] = "normal"
    ):
        view = GachaView(mode)
        await channel.send("🎯 ガチャを引こう！\n下のボタンからいつでもガチャを引けるよ👇", view=view)
        await interaction.response.send_message(f"✅ ガチャポストを {channel.mention} に送信しました", ephemeral=True)

    @app_commands.command(name="set_answer", description="ミッションの正解を設定する（管理者専用）")
    @app_commands.describe(answer="新しい正解文字列")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_answer(self, interaction: discord.Interaction, answer: str):
        global current_answer
        current_answer = answer.strip()
        await interaction.response.send_message(f"✅ 新しい正解を設定したよ：**{current_answer}**", ephemeral=True)

    @set_answer.error
    async def set_answer_error(self, interaction: discord.Interaction, error):
        if isinstance(error, CheckFailure):
            await interaction.response.send_message("🚫 このコマンドは管理者しか使えないよ〜", ephemeral=True)


    @app_commands.command(name="set_channel", description="ミッションや制限チャンネルのIDを設定（管理者専用）")
    @app_commands.describe(kind="設定するチャンネルの種類", channel="設定したいチャンネル")
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


# Cogとして登録
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))