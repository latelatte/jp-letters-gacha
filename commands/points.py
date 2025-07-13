import discord
from discord.ext import commands

from logics.data_manager import get_user_data

class PointsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="points")
    @commands.has_permissions(administrator=True)
    async def points_cmd(self, ctx):
        target = ctx.message.mentions[0] if ctx.message.mentions else ctx.author
        user = get_user_data(target.id)
        await ctx.send(f"💠 {target.mention} の所持ポイント：**{user['points']}pt**, **{user['ssr_points']}pt**")

async def setup(bot):
    await bot.add_cog(PointsCommands(bot))