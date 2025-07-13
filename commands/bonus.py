import discord
from discord.ext import commands
from datetime import date
from logics.data_manager import get_user_data, update_user_data

async def login_bonus(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)
    today = str(date.today())

    if user.get("login_count", 0) == 0:
        user["points"] = user.get("points", 0) + 100
        user["login_count"] = 1
        user["last_claim_date"] = today
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"🎉 はじめまして！{interaction.user.mention} に 100ポイントのウェルカムボーナスをプレゼントしたよ〜（今 {user['points']}pt）",
            ephemeral=True
        )
    elif user.get("last_claim_date") != today:
        user["points"] += 3
        user["last_claim_date"] = today
        user["login_count"] += 1
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"✨ ログインボーナス！{interaction.user.mention} に 3ポイント付与されたよ〜（今 {user['points']}pt）",
            ephemeral=True
        )
    else:
        await interaction.response.send_message("今日はすでにログインボーナスを受け取ってるよ〜", ephemeral=True)


class BonusListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @discord.app_commands.command(name="login_bonus", description="ログインボーナスを受け取る")
    async def login_bonus_cmd(self, interaction: discord.Interaction):
        await login_bonus(interaction)

    @discord.app_commands.command(name="show_login_button", description="ログインボタンを表示する")
    async def show_login_button(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="ログインボーナスを受け取る", custom_id="login_bonus_button", style=discord.ButtonStyle.primary))
        await interaction.response.send_message("🎁 ログインボーナスはこちらから！", view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data.get("custom_id") == "login_bonus_button":
            await login_bonus(interaction)

async def setup(bot):
    await bot.add_cog(BonusListener(bot))