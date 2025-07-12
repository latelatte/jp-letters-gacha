import discord
from discord.ext import commands
from datetime import date
from logics.data_manager import get_user_data, update_user_data

class BonusListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        user = get_user_data(message.author.id)
        today = str(date.today())

        # 初回ログインチェック
        if user.get("login_count", 0) == 0:
            user["points"] = user.get("points", 0) + 100
            user["login_count"] = user.get("login_count", 0) + 1
            user["last_claim_date"] = today
            update_user_data(message.author.id, user)
            await message.channel.send(
                f"🎉 はじめまして！{message.author.mention} に 100ポイントのウェルカムボーナスをプレゼントしたよ〜（今 {user['points']}pt）"
            )

        # 通常のログインボーナス処理（2回目以降）
        elif user.get("last_claim_date") != today:
            user["points"] += 3
            user["last_claim_date"] = today
            user["login_count"] += 1
            update_user_data(message.author.id, user)
            await message.channel.send(
                f"✨ ログインボーナス！{message.author.mention} に 3ポイント付与されたよ〜（今 {user['points']}pt）"
            )

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(BonusListener(bot))