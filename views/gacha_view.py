import discord
from logics.normal_gacha import run_gacha, run_gacha10
from logics.pickup_gacha import run_gacha_pickup, run_gacha_pickup10
from logics.ssr_gacha import run_gacha_ssr
from commands.bonus import login_bonus

from typing import Literal
import json
from pathlib import Path

def load_gacha_button_config():
    """ガチャボタンの設定を読み込む"""
    config_path = Path("./assets/gacha_button_config.json")
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # デフォルト設定
        return {
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

class GachaView(discord.ui.View):
    def __init__(self, mode: Literal["normal", "pickup", "ssr"] = "normal"):
        super().__init__(timeout=None)
        self.mode = mode
        self.config = load_gacha_button_config()

        if self.mode == "normal":
            self.add_item(NormalGachaButton(self.config["normal"]["single"]))
            self.add_item(NormalGacha10Button(self.config["normal"]["multi"]))
        elif self.mode == "pickup":
            self.add_item(PickupGachaButton(self.config["pickup"]["single"]))
            self.add_item(PickupGacha10Button(self.config["pickup"]["multi"]))
        elif self.mode == "ssr":
            self.add_item(SsrGachaButton(self.config["ssr"]["single"]))
    
    def get_message(self) -> str:
        """ガチャボタンと一緒に表示するメッセージを取得"""
        return self.config[self.mode]["message"]

class NormalGachaButton(discord.ui.Button):
    def __init__(self, label: str = "ガチャ🎯"):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id="normal_gacha")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha(interaction)

class NormalGacha10Button(discord.ui.Button):
    def __init__(self, label: str = "10連🔥"):
        super().__init__(label=label, style=discord.ButtonStyle.success, custom_id="normal_gacha10")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha10(interaction)

class PickupGachaButton(discord.ui.Button):
    def __init__(self, label: str = "ピックアップ🎯"):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id="pickup_gacha")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha_pickup(interaction)

class PickupGacha10Button(discord.ui.Button):
    def __init__(self, label: str = "ピックアップ10連🔥"):
        super().__init__(label=label, style=discord.ButtonStyle.success, custom_id="pickup_gacha10")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha_pickup10(interaction)

class SsrGachaButton(discord.ui.Button):
    def __init__(self, label: str = "SSR限定💎"):
        super().__init__(label=label, style=discord.ButtonStyle.danger, custom_id="ssr_gacha")

    async def callback(self, interaction: discord.Interaction):
        await run_gacha_ssr(interaction)
        
class LoginBonusButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ログインボーナス🎁", style=discord.ButtonStyle.success, custom_id="login_bonus_button")

    async def callback(self, interaction: discord.Interaction):
        await login_bonus(interaction)