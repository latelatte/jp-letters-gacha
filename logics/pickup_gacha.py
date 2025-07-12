import json
import random
from pathlib import Path
from datetime import date
import discord
from logics.data_manager import get_user_data, update_user_data
from logics.gacha_utils import get_weight, add_ssr_points
from logics.char_loader import load_char_sets
_, _, _, rarity_map = load_char_sets()

# --- ピックアップガチャ設定の読み込み ---
def load_pickup_config():
    config_path = Path(__file__).parent / "assets" / "pickup_gacha.json"
    if not config_path.exists():
        return None
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)

def is_pickup_active(config):
    if not config or not config.get("active", False):
        return False
    today = date.today()
    try:
        start = date.fromisoformat(config["start"])
        end = date.fromisoformat(config["end"])
    except Exception:
        return False
    return start <= today <= end

# ピックアップガチャ用: 現在のピックアッププールから1文字を選ぶ
def draw_pickup_char():
    from datetime import datetime
    base = Path(__file__).parent / "assets"
    pickup_file = base / "pickup_gacha.json"

    if not pickup_file.exists():
        return None, None

    with open(pickup_file, encoding="utf-8") as f:
        data = json.load(f)

    today = datetime.now().date().isoformat()

    if not (data.get("start_date") <= today <= data.get("end_date")):
        return None, None

    chars = data.get("characters", [])
    pool = []
    for ch in chars:
        rarity = rarity_map.get(ch, "N")
        weight = get_weight(rarity)
        pool.extend([ch] * weight)

    if not pool:
        return None, None

    selected = random.choice(pool)
    return selected, rarity_map.get(selected, "N")

async def run_gacha_pickup(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)

    if user["points"] <= 0:
        await interaction.response.send_message("💸 ポイントが足りないよ〜", ephemeral=True)
        return

    letter, rarity = draw_pickup_char()
    if not letter or not rarity:
        await interaction.response.send_message("⚠️ 現在ピックアップガチャは開催されていないよ〜", ephemeral=True)
        return

    user["points"] -= 1

    if letter in user["letters"]:
        bonus = add_ssr_points(user, rarity)
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"😮 {interaction.user.mention} はすでに **「{letter}」** を持ってたよ〜！（ピックアップ）\nSSR限ポイント {bonus} 付与！（現在: {user['ssr_points']}pt）", ephemeral=True
        )
    else:
        user["letters"].append(letter)
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"🎯 {interaction.user.mention} がピックアップガチャを引いた！\n→ **「{letter}」** をGET！（レア度: {rarity}）\n(残りポイント: {user['points']})", ephemeral=True
        )

# 新規: 10連ピックアップガチャコマンド
async def run_gacha_pickup10(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)

    if user["points"] < 10:
        await interaction.response.send_message("💸 ポイントが足りないよ〜（10pt必要）", ephemeral=True)
        return

    config = load_pickup_config()
    if not is_pickup_active(config):
        await interaction.response.send_message("⚠️ 現在ピックアップガチャは開催されていないよ〜", ephemeral=True)
        return

    results = []
    new_count = 0
    user["points"] -= 10

    for _ in range(10):
        letter, rarity = draw_pickup_char()
        if not letter:
            results.append("⚠️ ピックアップ対象が存在しないガチャが混ざってたよ…")
            continue
        if letter in user["letters"]:
            results.append(f"😮 {letter}（{rarity}, 重複）")
        else:
            user["letters"].append(letter)
            results.append(f"🎯 {letter}（{rarity}）")
            new_count += 1

    update_user_data(interaction.user.id, user)
    summary = f"{interaction.user.mention} のピックアップ10連結果（新規 {new_count} / 10）\n残りポイント: {user['points']}\n\n"
    result_text = summary + "\n".join(results)
    await interaction.response.send_message(result_text, ephemeral=True)