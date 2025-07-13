import discord
from discord.ext import commands
from discord import app_commands

from logics.data_manager import get_user_data
from logics.char_loader import load_char_sets

class LettersCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="letters", description="今までに集めた文字を確認するよ！")
    async def letters(self, interaction: discord.Interaction):
        user = get_user_data(interaction.user.id)
        hiragana_chars, katakana_chars, jouyou_chars, rarity_map = load_char_sets()
        letters = user["letters"]

        if not letters:
            await interaction.response.send_message("まだ何も当たってないよ〜🥺", ephemeral=True)
            return

        # 分類とソート
        h = sorted([c for c in letters if c in hiragana_chars])
        k = sorted([c for c in letters if c in katakana_chars])
        j = sorted([c for c in letters if c in jouyou_chars])

        text = ""
        if h: text += f"ひらがな：{' '.join(h)}\n"
        if k: text += f"カタカナ：{' '.join(k)}\n"
        if j: text += f"漢字：{' '.join(j)}\n"

        await interaction.response.send_message(f"🧩 {interaction.user.mention} の持ち文字：\n{text}", ephemeral=True)

    @app_commands.command(name="collection", description="集めた文字をレア度別に表示するよ！")
    async def collection(self, interaction: discord.Interaction):
        user = get_user_data(interaction.user.id)
        hiragana_chars, katakana_chars, jouyou_chars, rarity_map = load_char_sets()
        owned_letters = user["letters"]

        rarity_categories = {"N": [], "R": [], "SR": [], "SSR": []}
        for ch in owned_letters:
            rarity = rarity_map.get(ch, "N")
            if rarity in rarity_categories:
                rarity_categories[rarity].append(ch)

        lines = []
        for rarity in ["N", "R", "SR", "SSR"]:
            chars = sorted(rarity_categories[rarity])
            if chars:
                display = " ".join(chars[:10])
                if len(chars) > 10:
                    display += "…"
                lines.append(f"{rarity}（{len(chars)}個）：{display}")
        result = "\n".join(lines) if lines else "まだ何も当たってないよ〜🥺"
        await interaction.response.send_message(result, ephemeral=True)

async def setup(bot):
    await bot.add_cog(LettersCommands(bot))