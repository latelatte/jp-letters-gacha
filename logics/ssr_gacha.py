import random
import discord
from logics.data_manager import get_user_data, update_user_data
from logics.gacha_utils import draw_ssr_char

async def run_gacha_ssr(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)

    if user.get("ssr_points", 0) < 10:
        await interaction.response.send_message("💸 SSR限ポイントが足りないよ〜（10pt必要）", ephemeral=True)
        return

    ssr_char = draw_ssr_char()
    if not ssr_char:
        await interaction.response.send_message("⚠️ SSRの文字が設定されてないみたい…", ephemeral=True)
        return

    user["ssr_points"] -= 10
    if ssr_char in user["letters"]:
        msg = f"😮 {interaction.user.mention} はすでに **「{ssr_char}」** を持ってたよ〜！\n(現在: {user['ssr_points']}pt)"
    else:
        user["letters"].append(ssr_char)
        msg = f"🎉 {interaction.user.mention} がSSR限定ガチャを引いた！\n→ **「{ssr_char}」** をGET！\n(残りSSR限ポイント: {user['ssr_points']})"

    update_user_data(interaction.user.id, user)
    await interaction.response.send_message(msg, ephemeral=True)