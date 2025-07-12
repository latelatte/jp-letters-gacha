import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from discord.ext.commands import has_permissions, CheckFailure
import os
from datetime import date
import random


from data_manager import get_user_data, update_user_data

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # on_messageで必要
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ガチャに使う50音リスト（テスト用）
kana_list = [
    "ア", "イ", "ウ", "エ", "オ",
    "カ", "キ", "ク", "ケ", "コ",
    "サ", "シ", "ス", "セ", "ソ",
    "タ", "チ", "ツ", "テ", "ト",
    "ナ", "ニ", "ヌ", "ネ", "ノ",
    "ハ", "ヒ", "フ", "ヘ", "ホ",
    "マ", "ミ", "ム", "メ", "モ",
    "ヤ", "ユ", "ヨ",
    "ラ", "リ", "ル", "レ", "ロ",
    "ワ", "ヲ", "ン"
]

# ログインボーナス付与
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user = get_user_data(message.author.id)
    today = str(date.today())

    if user["last_claim_date"] != today:
        user["points"] += 1
        user["last_claim_date"] = today
        update_user_data(message.author.id, user)
        await message.channel.send(f"✨ ログインボーナス！{message.author.mention} に 1ポイント付与されたよ〜（今 {user['points']}pt）")

    await bot.process_commands(message)  # スラッシュコマンドと共存するために必要


# スラッシュコマンドの登録準備
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands synced: {len(synced)}コマンド")
        bot.add_view(GachaView())  # 永続ボタンの登録（再起動時）
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"Logged in as {bot.user}")


# /gacha コマンド
@bot.tree.command(name="gacha", description="1ポイント使って50音ガチャを引くよ！")
async def gacha(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)

    if user["points"] <= 0:
        await interaction.response.send_message("💸 ポイントが足りないよ〜", ephemeral=True)
        return

    user["points"] -= 1
    letter = random.choice(kana_list)
    if letter in user["letters"]:
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"😮 {interaction.user.mention} はすでに **「{letter}」** を持ってたよ〜！残念！（ポイントは消費されました）"
        )
    else:
        user["letters"].append(letter)
        update_user_data(interaction.user.id, user)
        await interaction.response.send_message(
            f"🎊 {interaction.user.mention} がガチャを引いた！\n→ **「{letter}」** をGET！\n(残りポイント: {user['points']})"
        )
        
# プレフィックス対応 (動作は同じ、消しても良い)
@bot.command(name="gacha")
async def gacha_cmd(ctx):
    user = get_user_data(ctx.author.id)

    if user["points"] <= 0:
        await ctx.send("💸 ポイントが足りないよ〜")
        return

    user["points"] -= 1
    letter = random.choice(kana_list)
    if letter in user["letters"]:
        update_user_data(ctx.author.id, user)
        await ctx.send(
            f"😮 {ctx.author.mention} はすでに **「{letter}」** を持ってたよ〜！残念！（ポイントは消費されました）"
        )
    else:
        user["letters"].append(letter)
        update_user_data(ctx.author.id, user)
        await ctx.send(
            f"🎊 {ctx.author.mention} がガチャを引いた！\n→ **「{letter}」** をGET！\n(残りポイント: {user['points']})"
        )


# /gacha10 コマンド
@bot.tree.command(name="gacha10", description="10ポイント使って10連ガチャを引くよ！")
async def gacha10(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)

    if user["points"] < 10:
        await interaction.response.send_message("💸 ポイントが足りないよ〜（10pt必要）", ephemeral=True)
        return

    user["points"] -= 10
    results = []
    new_count = 0

    for _ in range(10):
        letter = random.choice(kana_list)
        if letter in user["letters"]:
            results.append(f"😮 {letter}（重複）")
        else:
            user["letters"].append(letter)
            results.append(f"🎊 {letter}")
            new_count += 1

    update_user_data(interaction.user.id, user)
    summary = f"{interaction.user.mention} の10連ガチャ結果（新規 {new_count} / 10）\n残りポイント: {user['points']}\n\n"
    result_text = summary + "\n".join(results)
    await interaction.response.send_message(result_text)
    


# プレフィックス版 !gacha10 コマンド
@bot.command(name="gacha10")
async def gacha10_cmd(ctx):
    user = get_user_data(ctx.author.id)

    if user["points"] < 10:
        await ctx.send("💸 ポイントが足りないよ〜（10pt必要）")
        return

    user["points"] -= 10
    results = []
    new_count = 0

    for _ in range(10):
        letter = random.choice(kana_list)
        if letter in user["letters"]:
            results.append(f"😮 {letter}（重複）")
        else:
            user["letters"].append(letter)
            results.append(f"🎊 {letter}")
            new_count += 1

    update_user_data(ctx.author.id, user)
    summary = f"{ctx.author.mention} の10連ガチャ結果（新規 {new_count} / 10）\n残りポイント: {user['points']}\n\n"
    result_text = summary + "\n".join(results)
    await ctx.send(result_text)


# /letters コマンド
@bot.tree.command(name="letters", description="今までに集めた文字を確認するよ！")
async def letters(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)
    letters = user["letters"]

    if not letters:
        await interaction.response.send_message("まだ何も当たってないよ〜🥺", ephemeral=True)
        return

    letter_str = " ".join(letters)
    await interaction.response.send_message(
        f"🧩 {interaction.user.mention} の持ち文字：\n{letter_str}"
    )
    

# プレフィックス対応 (動作は同じ、消しても良い)
@bot.command(name="letters")
async def letters_cmd(ctx):
    user = get_user_data(ctx.author.id)
    letters = user["letters"]

    if not letters:
        await ctx.send("まだ何も当たってないよ〜🥺")
        return

    letter_str = " ".join(letters)
    await ctx.send(
        f"🧩 {ctx.author.mention} の持ち文字：\n{letter_str}"
    )


# 管理者用: 任意でポイント増減
@bot.command(name="add_point")
@commands.has_permissions(administrator=True)
async def add_point(ctx, amount: int):
    # 指定があればその人に、なければ自分に
    target = ctx.message.mentions[0] if ctx.message.mentions else ctx.author
    user = get_user_data(target.id)
    user["points"] += amount
    update_user_data(target.id, user)

    await ctx.send(f"{target.mention} のポイントを {amount:+} 変動しました！(現在: {user['points']}pt)")

@add_point.error
async def add_point_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("🚫 このコマンドは管理者しか使えないよ〜")

# /points コマンド
@bot.tree.command(name="points", description="現在のポイントを確認するよ！")
@app_commands.describe(user="確認したいユーザー（省略時は自分）")
async def points(interaction: discord.Interaction, user: discord.User = None):
    target = user or interaction.user

    # 他人を見るには管理者である必要あり
    if target != interaction.user:
        member = interaction.guild.get_member(interaction.user.id)
        if not member.guild_permissions.administrator:
            await interaction.response.send_message("🚫 他人のポイントを見るには管理者権限が必要だよ〜", ephemeral=True)
            return

    user_data = get_user_data(target.id)

    await interaction.response.send_message(
        f"💠 {target.display_name} の所持ポイント：**{user_data['points']}pt**"
    )


# プレフィックス版 !points コマンド
@bot.command(name="points")
async def points_cmd(ctx):
    user = get_user_data(ctx.author.id)
    await ctx.send(f"💠 {ctx.author.display_name} の所持ポイント：**{user['points']}pt**")
    
# /collection コマンド
@bot.tree.command(name="collection", description="集めた文字の進捗を表示するよ！")
async def collection(interaction: discord.Interaction):
    user = get_user_data(interaction.user.id)
    owned_letters = set(user["letters"])
    total_letters = kana_list

    collected = sum(1 for ch in total_letters if ch in owned_letters)
    display_lines = []

    for i in range(0, len(total_letters), 5):
        row = total_letters[i:i+5]
        line = []
        for ch in row:
            if ch in owned_letters:
                line.append(f"✅{ch}")
            else:
                line.append(f"❌{ch}")
        display_lines.append(" ".join(line))

    progress = f"🧩 {interaction.user.display_name} のコレクション（{collected} / {len(total_letters)}）\n"
    result = progress + "\n" + "\n".join(display_lines)

    await interaction.response.send_message(result)

# プレフィックス版 !collection コマンド
@bot.command(name="collection")
async def collection_cmd(ctx):
    user = get_user_data(ctx.author.id)
    owned_letters = set(user["letters"])
    total_letters = kana_list

    collected = sum(1 for ch in total_letters if ch in owned_letters)
    display_lines = []

    for i in range(0, len(total_letters), 5):
        row = total_letters[i:i+5]
        line = []
        for ch in row:
            if ch in owned_letters:
                line.append(f"✅{ch}")
            else:
                line.append(f"❌{ch}")
        display_lines.append(" ".join(line))

    progress = f"🧩 {ctx.author.display_name} のコレクション（{collected} / {len(total_letters)}）\n"
    result = progress + "\n" + "\n".join(display_lines)

    await ctx.send(result)

# テスト用 スラッシュコマンドの同期
@bot.tree.command(name="sync", description="スラッシュコマンドを同期するよ（管理者専用）")
@commands.has_permissions(administrator=True)
async def sync_commands(interaction: discord.Interaction):
    synced = await bot.tree.sync()
    await interaction.response.send_message(f"✅ コマンド {len(synced)} 件を同期したよ〜", ephemeral=True)


# ボタン付きガチャ UI の定義
class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="ガチャをひく🎯", style=discord.ButtonStyle.primary, custom_id="gacha_once")
    async def gacha_once(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = get_user_data(interaction.user.id)
        if user["points"] <= 0:
            await interaction.response.send_message("💸 ポイントが足りないよ〜", ephemeral=True)
            return

        user["points"] -= 1
        letter = random.choice(kana_list)
        if letter in user["letters"]:
            update_user_data(interaction.user.id, user)
            await interaction.response.send_message(
                f"😮 {interaction.user.mention} はすでに **「{letter}」** を持ってたよ〜！残念！（ポイントは消費されました）", ephemeral=True
            )
        else:
            user["letters"].append(letter)
            update_user_data(interaction.user.id, user)
            await interaction.response.send_message(
                f"🎊 {interaction.user.mention} がガチャを引いた！\n→ **「{letter}」** をGET！\n(残りポイント: {user['points']})", ephemeral=True
            )

    @discord.ui.button(label="10連ガチャ🔥", style=discord.ButtonStyle.success, custom_id="gacha_ten")
    async def gacha_ten(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = get_user_data(interaction.user.id)
        if user["points"] < 10:
            await interaction.response.send_message("💸 ポイントが足りないよ〜（10pt必要）", ephemeral=True)
            return

        user["points"] -= 10
        results = []
        new_count = 0

        for _ in range(10):
            letter = random.choice(kana_list)
            if letter in user["letters"]:
                results.append(f"😮 {letter}（重複）")
            else:
                user["letters"].append(letter)
                results.append(f"🎊 {letter}")
                new_count += 1

        update_user_data(interaction.user.id, user)
        summary = f"{interaction.user.mention} の10連ガチャ結果（新規 {new_count} / 10）\n残りポイント: {user['points']}\n\n"
        result_text = summary + "\n".join(results)
        await interaction.response.send_message(result_text, ephemeral=True)

# /gacha_buttons コマンド（ボタン付き）
@bot.tree.command(name="gacha_buttons", description="ボタンでガチャを引けるよ！")
async def gacha_buttons(interaction: discord.Interaction):
    await interaction.response.send_message("👇 好きなガチャを選んでね！", view=GachaView(), ephemeral=True)


# 管理者専用: ガチャボタンメッセージを任意チャンネルに送信
@bot.tree.command(name="post_gacha_buttons", description="指定チャンネルにガチャボタン常設メッセージを送る（管理者専用）")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel="ガチャポストを送信するチャンネル")
async def post_gacha_buttons(interaction: discord.Interaction, channel: discord.TextChannel):
    view = GachaView()
    msg = await channel.send("🎯 ガチャを引こう！\n下のボタンからいつでもガチャを引けるよ👇", view=view)
    await interaction.response.send_message(f"✅ ガチャポストを {channel.mention} に送信しました", ephemeral=True)
    
# 実行

# ==== ミッション機能（クイズ回答） ====

# 現在の正解＆対象チャンネルID
current_answer = "あかさたな"  # 仮の答え（例）
MISSION_CHANNEL_ID = 1393526860977012827  # 実際のチャンネルIDに置き換えてください

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # IDでチェック（ミッション回答）
    if message.channel.id == MISSION_CHANNEL_ID:
        content = message.content.strip()
        await message.delete()

        user = get_user_data(message.author.id)
        today = str(date.today())

        if content == current_answer:
            if user.get("mission_cleared") == today:
                msg = await message.channel.send(
                    f"{message.author.mention} ⚠️ 今日はすでに正解してるよ〜"
                )
            else:
                user["points"] += 10
                user["mission_cleared"] = today
                update_user_data(message.author.id, user)
                msg = await message.channel.send(
                    f"{message.author.mention} 🎉 正解！10ポイント付与されたよ！（現在: {user['points']}pt）"
                )
        else:
            msg = await message.channel.send(
                f"{message.author.mention} ❌ 残念、不正解だったよ〜"
            )

        await msg.delete(delay=5)
        return

    # 通常のログインボーナス処理
    user = get_user_data(message.author.id)
    today = str(date.today())

    if user["last_claim_date"] != today:
        user["points"] += 1
        user["last_claim_date"] = today
        update_user_data(message.author.id, user)
        await message.channel.send(f"✨ ログインボーナス！{message.author.mention} に 1ポイント付与されたよ〜（今 {user['points']}pt）")

    await bot.process_commands(message)


# ミッションの正解を変更する管理者用コマンド
@bot.tree.command(name="set_answer", description="ミッションの正解を設定する（管理者専用）")
@app_commands.describe(answer="新しい正解文字列")
@commands.has_permissions(administrator=True)
async def set_answer(interaction: discord.Interaction, answer: str):
    global current_answer
    current_answer = answer.strip()
    await interaction.response.send_message(f"✅ 新しい正解を設定したよ：**{current_answer}**", ephemeral=True)

@set_answer.error
async def set_answer_error(interaction: discord.Interaction, error):
    if isinstance(error, CheckFailure):
        await interaction.response.send_message("🚫 このコマンドは管理者しか使えないよ〜", ephemeral=True)

bot.run(TOKEN)