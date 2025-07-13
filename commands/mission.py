
# ==== ミッション機能（クイズ回答） ====

import discord
from discord.ext import commands
from datetime import date

from logics.data_manager import get_user_data, update_user_data, get_channel_id

current_answer = "あかさたな"  # ダミー

class MissionListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # ===== 持ち文字制限チャンネルでの検閲処理 =====
        if message.channel.id == get_channel_id("restricted"):
            user = get_user_data(message.author.id)
            owned_set = set(user["letters"])
            used_chars = set(c for c in message.content if c != " ")

            illegal_chars = used_chars - owned_set

            if illegal_chars:
                await message.delete()
                warn_msg = await message.channel.send(
                    f"{message.author.mention} ❌ 持ってない文字が含まれているよ！\n"
                    f"（使えなかった文字: {'、'.join(sorted(illegal_chars))}）\n"
                    f"※このメッセージは10秒後に自動で消えます。"
                )
                await warn_msg.delete(delay=10)
                return

        # ===== ミッション回答処理 =====
        if message.channel.id == get_channel_id("mission"):
            content = message.content.strip()
            
            # メッセージ削除を試行（権限がない場合はスキップ）
            try:
                await message.delete()
            except discord.Forbidden:
                pass  # 権限がない場合は無視して続行

            user = get_user_data(message.author.id)
            today = str(date.today())

            if content == current_answer:
                if user.get("mission_cleared") == today:
                    msg = await message.channel.send(
                        f"{message.author.mention} ⚠️ 今日はすでに正解してるよ〜"
                    )
                else:
                    user["points"] += 10
                    user["mission_cleared"] = today
                    update_user_data(message.author.id, user)
                    msg = await message.channel.send(
                        f"{message.author.mention} 🥳 正解！10ポイント付与されたよ！（現在: {user['points']}pt）"
                    )
            else:
                msg = await message.channel.send(
                    f"{message.author.mention} ❌ 不正解みたいです…。\n"
                    f"全角カタカナで入力されているか確認してください！\n"
                    f"※このメッセージは5秒後に自動で消えます。"
                )

            await msg.delete(delay=5)
            return

async def setup(bot):
    await bot.add_cog(MissionListener(bot))