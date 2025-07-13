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
        hiragana_chars, katakana_chars, jouyou_chars, numbers_chars, rarity_map = load_char_sets()
        letters = user["letters"]

        if not letters:
            await interaction.response.send_message("まだ何も当たってないよ〜🥺", ephemeral=True)
            return

        # 記号と数字の文字セットを作成
        import json
        from pathlib import Path
        base = Path(__file__).parents[1] / "assets"
        with open(base / "symbols.json", encoding="utf-8") as f:
            symbols_data = json.load(f)
        symbols_chars = list(symbols_data.keys())

        # 分類とソート（重複を避けるため優先順位で分類）
        h = []
        k = []
        j = []
        n = []
        s = []
        
        for c in letters:
            if c in numbers_chars:
                n.append(c)  # 数字が最優先
            elif c in symbols_chars:
                s.append(c)  # 次に記号
            elif c in hiragana_chars:
                h.append(c)  # ひらがな
            elif c in katakana_chars:
                k.append(c)  # カタカナ
            elif c in jouyou_chars:
                j.append(c)  # 漢字は最後
        
        # ソート
        h = sorted(h)
        k = sorted(k)
        j = sorted(j)
        n = sorted(n)
        s = sorted(s)

        text = ""
        if h: text += f"ひらがな：{' '.join(h)}\n"
        if k: text += f"カタカナ：{' '.join(k)}\n"
        if j: text += f"漢字：{' '.join(j)}\n"
        if n: text += f"数字：{' '.join(n)}\n"
        if s: text += f"記号：{' '.join(s)}\n"

        await interaction.response.send_message(f"🧩 {interaction.user.mention} の持ち文字：\n{text}", ephemeral=True)

    @app_commands.command(name="collection", description="集めた文字をレア度別に表示するよ！")
    async def collection(self, interaction: discord.Interaction):
        user = get_user_data(interaction.user.id)
        hiragana_chars, katakana_chars, jouyou_chars, numbers_chars, rarity_map = load_char_sets()
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