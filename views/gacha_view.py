import discord
from logics.normal_gacha import run_gacha, run_gacha10
from logics.pickup_gacha import run_gacha_pickup, run_gacha_pickup10
from logics.ssr_gacha import run_gacha_ssr

from typing import Literal

class GachaView(discord.ui.View):
    def __init__(self, mode: Literal["normal", "pickup", "ssr"] = "normal"):
        super().__init__(timeout=None)
        self.mode = mode

        if self.mode == "normal":
            self.add_item(NormalGachaButton())
            self.add_item(NormalGacha10Button())
        elif self.mode == "pickup":
            self.add_item(PickupGachaButton())
            self.add_item(PickupGacha10Button())
        elif self.mode == "ssr":
            self.add_item(SsrGachaButton())

class NormalGachaButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ガチャ🎯", style=discord.ButtonStyle.primary, custom_id="gacha")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha(interaction)

class NormalGacha10Button(discord.ui.Button):
    def __init__(self):
        super().__init__(label="10連🔥", style=discord.ButtonStyle.success, custom_id="gacha10")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha10(interaction)

class PickupGachaButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ピックアップ🎯", style=discord.ButtonStyle.primary, custom_id="gacha_pickup")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha_pickup(interaction)

class PickupGacha10Button(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ピックアップ10連🔥", style=discord.ButtonStyle.success, custom_id="gacha_pickup10")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha_pickup10(interaction)

class SsrGachaButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="SSR限定💎", style=discord.ButtonStyle.danger, custom_id="gacha_ssr")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha_ssr(interaction)