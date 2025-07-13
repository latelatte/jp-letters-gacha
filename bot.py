import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import asyncio

from views.gacha_view import GachaView

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN が設定されていません") # こうしないとリンターがうるさい

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands synced: {len(synced)}コマンド")
        
        bot.add_view(GachaView("normal"))   # 通常ガチャ
        bot.add_view(GachaView("pickup"))   # ピックアップガチャ
        bot.add_view(GachaView("ssr"))      # SSR限定ガチャ
        
        print("✅ 永続ビューを登録しました")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"Logged in as {bot.user}")

async def load_extensions():
    for ext in [
        "commands.gacha",
        "commands.letters",
        "commands.admin",
        "commands.points",
        "commands.mission",
        "commands.bonus"
    ]:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded extension: {ext}")
        except Exception as e:
            print(f"❌ Failed to load extension {ext}: {e}")

async def main():
    async with bot:
        await load_extensions()
        if TOKEN:
            await bot.start(TOKEN)
        else:
            raise ValueError("DISCORD_TOKEN が設定されていません") # ここもリンターが怒る

if __name__ == "__main__":
    asyncio.run(main())