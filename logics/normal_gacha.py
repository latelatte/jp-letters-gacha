import random
import discord
from logics.data_manager import get_user_data, update_user_data
from logics.gacha_utils import get_weight, add_ssr_points, draw_weighted_char
from logics.char_loader import load_char_sets

hiragana_chars, katakana_chars, jouyou_chars, rarity_map = load_char_sets()

def draw_random_char():
    letter = draw_weighted_char()
    rarity = rarity_map.get(letter, "N")
    return letter, rarity

async def run_gacha(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)

    if user["points"] <= 0:
        await interaction.response.send_message("💸 ポイントが足りないよ〜", ephemeral=True)
        return

    user["points"] -= 1
    letter, rarity = draw_random_char()
    if letter in user["letters"]:
        bonus = add_ssr_points(user, rarity)
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"😮 {interaction.user.mention} はすでに **「{letter}」** を持ってたよ〜！\nSSR限ポイント {bonus} 付与！（現在: {user['ssr_points']}pt）"
            , ephemeral=True
        )
    else:
        user["letters"].append(letter)
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"🎊 {interaction.user.mention} がガチャを引いた！\n→ **「{letter}」** をGET！（レア度: {rarity}）\n(残りポイント: {user['points']})"
            , ephemeral=True
        )

## 共通の10連ガチャ処理関数
async def run_gacha10(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)

    if user["points"] < 10:
        await interaction.response.send_message("💸 ポイントが足りないよ〜（10pt必要）", ephemeral=True)
        return

    user["points"] -= 10
    results = []
    new_count = 0

    for _ in range(10):
        letter, rarity = draw_random_char()
        if letter in user["letters"]:
            results.append(f"😮 {letter}（{rarity}, 重複）")
        else:
            user["letters"].append(letter)
            results.append(f"🎊 {letter}（{rarity}）")
            new_count += 1

    update_user_data(interaction.user.id, user)
    summary = f"{interaction.user.mention} の10連ガチャ結果（新規 {new_count} / 10）\n残りポイント: {user['points']}\n\n"
    result_text = summary + "\n".join(results)
    await interaction.response.send_message(result_text)