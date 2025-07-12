# import discord
# from discord.ext import commands
# from logics.data_manager import get_user_data, update_user_data

# class WelcomeBonus(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @commands.Cog.listener()
#     async def on_message(self, message: discord.Message):
#         if message.author.bot:
#             return

#         user = get_user_data(message.author.id)
#         if "points" not in user:
#             user["points"] = 100
#             update_user_data(message.author.id, user)
#             await message.channel.send(
#                 f"🎉 ウェルカムボーナス！{message.author.mention} に 100ポイント付与されたよ！（今 {user['points']}pt）"
#             )
#         await self.bot.process_commands(message)

# async def setup(bot):
#     await bot.add_cog(WelcomeBonus(bot))