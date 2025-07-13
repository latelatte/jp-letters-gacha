from discord.ext import commands
from discord import app_commands, Interaction
from logics.normal_gacha import run_gacha, run_gacha10
from logics.pickup_gacha import run_gacha_pickup, run_gacha_pickup10, show_pickup_info
from logics.ssr_gacha import run_gacha_ssr

class GachaCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gacha", description="1ポイント使って50音ガチャを引くよ！")
    @app_commands.default_permissions(administrator=True)
    async def gacha(self, interaction: Interaction):
        await run_gacha(interaction)

    @app_commands.command(name="gacha10", description="10ポイント使って10連ガチャを引くよ！")
    @app_commands.default_permissions(administrator=True)
    async def gacha10(self, interaction: Interaction):
        await run_gacha10(interaction)

    @app_commands.command(name="gacha_pickup", description="ピックアップ対象から1文字ガチャを引くよ！（通常ポイント消費）")
    @app_commands.default_permissions(administrator=True)
    async def gacha_pickup(self, interaction: Interaction):
        await run_gacha_pickup(interaction)

    @app_commands.command(name="gacha_pickup10", description="10ポイント使ってピックアップ10連ガチャを引くよ！")
    @app_commands.default_permissions(administrator=True)
    async def gacha_pickup10(self, interaction: Interaction):
        await run_gacha_pickup10(interaction)

    @app_commands.command(name="gacha_ssr", description="SSR限ポイントを10pt使ってSSR限定ガチャを引くよ！")
    @app_commands.default_permissions(administrator=True)
    async def gacha_ssr(self, interaction: Interaction):
        await run_gacha_ssr(interaction)

    @app_commands.command(name="pickup_info", description="現在開催中のピックアップガチャの情報を表示するよ！")
    async def pickup_info(self, interaction: Interaction):
        await show_pickup_info(interaction)

async def setup(bot):
    await bot.add_cog(GachaCommands(bot))