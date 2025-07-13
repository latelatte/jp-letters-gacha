import json
import random
from pathlib import Path
from datetime import date
import discord
from logics.data_manager import get_user_data, update_user_data
from logics.gacha_utils import get_weight, add_ssr_points
from logics.char_loader import load_char_sets
_, _, _, _, rarity_map = load_char_sets()

# --- ピックアップガチャ設定の読み込み ---
def load_pickup_config():
    """イベント設定を読み込む（新形式と旧形式の両方に対応）"""
    # 新形式の設定ファイルを優先
    events_config_path = Path(__file__).parent.parent / "assets" / "events_config.json"
    if events_config_path.exists():
        try:
            with open(events_config_path, encoding="utf-8") as f:
                events_data = json.load(f)
            current_event_id = events_data.get("current_event")
            if current_event_id and current_event_id in events_data.get("events", {}):
                return events_data["events"][current_event_id]
        except Exception:
            pass
    
    # 旧形式へのフォールバック
    config_path = Path(__file__).parent.parent / "assets" / "pickup_gacha.json"
    if not config_path.exists():
        return None
    try:
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def is_pickup_active(config):
    if not config or not config.get("active", False):
        return False
    today = date.today()
    try:
        start = date.fromisoformat(config["start_date"])
        end = date.fromisoformat(config["end_date"])
    except Exception:
        return False
    return start <= today <= end

# ピックアップガチャ用: 恒常ガチャ + ピックアップ対象から1文字を選ぶ
def draw_pickup_char():
    from collections import defaultdict
    from logics.gacha_utils import get_event_excluded_chars, get_weight
    
    config = load_pickup_config()
    if not config or not is_pickup_active(config):
        return None, None

    # ピックアップ対象文字と設定を取得
    pickup_chars = set(config.get("characters", []))
    pickup_rate = config.get("pickup_rate_percentage", 50.0)  # ピックアップ率（%）
    
    # 恒常ガチャの文字（イベント除外文字以外）を取得
    excluded_chars = get_event_excluded_chars()
    
    # 恒常文字とピックアップ文字をレアリティ別に分類
    from logics.char_loader import load_char_sets
    hiragana_chars, katakana_chars, jouyou_chars, numbers_chars, _ = load_char_sets()
    all_chars = set(hiragana_chars + katakana_chars + jouyou_chars + numbers_chars + list(rarity_map.keys()))
    
    normal_chars_by_rarity = defaultdict(list)
    pickup_chars_by_rarity = defaultdict(list)
    
    # 恒常文字の分類
    for ch in all_chars:
        if ch in excluded_chars:
            continue  # イベント除外文字はスキップ
        rarity = rarity_map.get(ch, "N-kanji")
        normal_chars_by_rarity[rarity].append(ch)
    
    # ピックアップ文字の分類（イベント限定文字含む）
    rarity_overrides = config.get("rarity_overrides", {})
    for ch in pickup_chars:
        # レアリティオーバーライドがあれば優先、なければ通常のレアリティを使用
        rarity = rarity_overrides.get(ch, rarity_map.get(ch, "N"))
        pickup_chars_by_rarity[rarity].append(ch)
    
    # Step 1: レアリティを重み付きで選択（通常のガチャと同じ）
    rarities = []
    rarity_weights = []
    
    all_rarities = set(normal_chars_by_rarity.keys()) | set(pickup_chars_by_rarity.keys())
    for rarity in all_rarities:
        normal_count = len(normal_chars_by_rarity.get(rarity, []))
        pickup_count = len(pickup_chars_by_rarity.get(rarity, []))
        
        if normal_count > 0 or pickup_count > 0:
            rarities.append(rarity)
            rarity_weights.append(get_weight(rarity))
    
    if not rarities:
        return None, None
    
    selected_rarity = random.choices(rarities, weights=rarity_weights, k=1)[0]
    
    # Step 2: 選択されたレアリティ内でピックアップ vs 恒常を決定
    normal_chars = normal_chars_by_rarity.get(selected_rarity, [])
    pickup_chars_in_rarity = pickup_chars_by_rarity.get(selected_rarity, [])
    
    # ピックアップ文字と恒常文字の両方がある場合のみピックアップ率を適用
    if pickup_chars_in_rarity and normal_chars:
        if random.random() * 100 < pickup_rate:
            # ピックアップから選択
            selected = random.choice(pickup_chars_in_rarity)
        else:
            # 恒常から選択
            selected = random.choice(normal_chars)
    elif pickup_chars_in_rarity:
        # ピックアップ文字のみ
        selected = random.choice(pickup_chars_in_rarity)
    elif normal_chars:
        # 恒常文字のみ
        selected = random.choice(normal_chars)
    else:
        return None, None
    
    # レアリティオーバーライドがあれば優先、なければ通常のレアリティを返す
    config = load_pickup_config()
    rarity_overrides = config.get("rarity_overrides", {}) if config else {}
    final_rarity = rarity_overrides.get(selected, rarity_map.get(selected, "N"))
    
    return selected, final_rarity

async def run_gacha_pickup(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)

    if user["points"] <= 0:
        await interaction.response.send_message("💸 ポイントが足りないよ〜", ephemeral=True)
        return

    config = load_pickup_config()
    if not config or not is_pickup_active(config):
        await interaction.response.send_message("⚠️ 現在ピックアップガチャは開催されていないよ〜", ephemeral=True)
        return

    letter, rarity = draw_pickup_char()
    if not letter or not rarity:
        await interaction.response.send_message("⚠️ ピックアップガチャでエラーが発生したよ〜", ephemeral=True)
        return

    user["points"] -= 1
    event_title = config.get("title", "ピックアップガチャ")

    if letter in user["letters"]:
        bonus = add_ssr_points(user, rarity)
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"😮 {interaction.user.mention} はすでに **「{letter}」** を持ってたよ〜！（{event_title}）\nSSR限ポイント {bonus} 付与！（現在: {user['ssr_points']}pt）", ephemeral=True
        )
    else:
        user["letters"].append(letter)
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"🎯 {interaction.user.mention} が{event_title}を引いた！\n→ **「{letter}」** をGET！（レア度: {rarity}）\n(残りポイント: {user['points']})", ephemeral=True
        )

# 新規: 10連ピックアップガチャコマンド
async def run_gacha_pickup10(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)

    if user["points"] < 10:
        await interaction.response.send_message("💸 ポイントが足りないよ〜（10pt必要）", ephemeral=True)
        return

    config = load_pickup_config()
    if not config or not is_pickup_active(config):
        await interaction.response.send_message("⚠️ 現在ピックアップガチャは開催されていないよ〜", ephemeral=True)
        return

    results = []
    new_count = 0
    ssr_bonus_total = 0
    user["points"] -= 10
    event_title = config.get("title", "ピックアップガチャ")

    for _ in range(10):
        letter, rarity = draw_pickup_char()
        if not letter:
            results.append("⚠️ ピックアップ対象が存在しないガチャが混ざってたよ…")
            continue
        if letter in user["letters"]:
            results.append(f"😮 {letter}（{rarity}, 重複）")
            if rarity:
                ssr_bonus_total += {"SSR": 5, "SR": 3, "R": 2}.get(rarity, 1)
        else:
            user["letters"].append(letter)
            results.append(f"🎯 {letter}（{rarity}）")
            new_count += 1

    if ssr_bonus_total > 0:
        if "ssr_points" not in user:
            user["ssr_points"] = 0
        user["ssr_points"] += ssr_bonus_total

    update_user_data(interaction.user.id, user)
    
    summary = f"{interaction.user.mention} の{event_title}10連結果（新規 {new_count} / 10）\n残りポイント: {user['points']}"
    if ssr_bonus_total > 0:
        summary += f"\nSSR限ポイント +{ssr_bonus_total}pt（現在: {user['ssr_points']}pt）"
    summary += "\n\n"
    
    result_text = summary + "\n".join(results)
    await interaction.response.send_message(result_text, ephemeral=True)

async def show_pickup_info(interaction: discord.Interaction):
    config = load_pickup_config()
    if not config:
        await interaction.response.send_message("📋 現在ピックアップガチャの設定がないよ〜", ephemeral=True)
        return

    title = config.get("title", "ピックアップガチャ")
    description = config.get("description", "説明なし")
    start_date = config.get("start_date", "不明")
    end_date = config.get("end_date", "不明")
    characters = config.get("characters", [])
    pickup_rate = config.get("pickup_rate_percentage", 50.0)
    is_active = is_pickup_active(config)

    status = "🟢 開催中" if is_active else "🔴 未開催・終了"
    
    message = f"**{title}**\n"
    message += f"📅 期間: {start_date} ～ {end_date}\n"
    message += f"📊 状態: {status}\n\n"
    message += f"📖 {description}\n\n"
    
    if characters:
        message += f"🎯 ピックアップ対象（{pickup_rate}%）: {' '.join(characters[:20])}"
        if len(characters) > 20:
            message += f" ...他{len(characters) - 20}文字"
        message += "\n\n"
    else:
        message += "🎯 ピックアップ対象: なし\n\n"
    
    message += "💡 **ピックアップガチャの仕組み**\n"
    message += "1️⃣ 通常通りレアリティを抽選（SR: 5%など）\n"
    message += f"2️⃣ そのレアリティ内で{pickup_rate}%の確率でピックアップ対象を選択\n"
    message += "3️⃣ 残りは恒常文字から選択\n"
    message += "4️⃣ イベント限定文字はこのガチャからのみ入手可能"
    
    await interaction.response.send_message(message, ephemeral=True)