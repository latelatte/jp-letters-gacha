import json
from pathlib import Path
from datetime import date
import discord
from discord.ext import commands
from discord import app_commands, Interaction

class EventManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_events_config(self):
        """イベント設定を読み込む"""
        config_path = Path(__file__).parent.parent / "assets" / "events_config.json"
        if not config_path.exists():
            return {"current_event": None, "events": {}}
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"current_event": None, "events": {}}

    def save_events_config(self, config):
        """イベント設定を保存する"""
        config_path = Path(__file__).parent.parent / "assets" / "events_config.json"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    @app_commands.command(name="event_list", description="登録されているイベント一覧を表示します")
    @app_commands.default_permissions(administrator=True)
    async def event_list(self, interaction: Interaction):
        config = self.load_events_config()
        events = config.get("events", {})
        current_event = config.get("current_event")
        
        if not events:
            await interaction.response.send_message("📋 登録されているイベントはありません", ephemeral=True)
            return
        
        message = "📋 **登録イベント一覧**\n\n"
        today = date.today()
        
        for event_id, event_data in events.items():
            status_icon = "🟢" if event_id == current_event else "⚪"
            title = event_data.get("title", event_id)
            start_date = event_data.get("start_date", "不明")
            end_date = event_data.get("end_date", "不明")
            
            # 期間チェック
            try:
                start = date.fromisoformat(start_date)
                end = date.fromisoformat(end_date)
                if today < start:
                    period_status = "開始前"
                elif today > end:
                    period_status = "終了"
                else:
                    period_status = "開催中"
            except:
                period_status = "期間不明"
            
            message += f"{status_icon} **{title}** (`{event_id}`)\n"
            message += f"   📅 {start_date} ～ {end_date} ({period_status})\n\n"
        
        await interaction.response.send_message(message, ephemeral=True)

    @app_commands.command(name="event_switch", description="アクティブなイベントを切り替えます")
    @app_commands.describe(event_id="切り替え先のイベントID")
    @app_commands.default_permissions(administrator=True)
    async def event_switch(self, interaction: Interaction, event_id: str):
        config = self.load_events_config()
        events = config.get("events", {})
        
        if event_id not in events:
            await interaction.response.send_message(f"❌ イベントID `{event_id}` が見つかりません", ephemeral=True)
            return
        
        config["current_event"] = event_id
        if self.save_events_config(config):
            event_title = events[event_id].get("title", event_id)
            await interaction.response.send_message(f"✅ アクティブイベントを **{event_title}** (`{event_id}`) に切り替えました", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 設定の保存に失敗しました", ephemeral=True)

    @app_commands.command(name="event_disable", description="すべてのイベントを無効化します")
    @app_commands.default_permissions(administrator=True)
    async def event_disable(self, interaction: Interaction):
        config = self.load_events_config()
        config["current_event"] = None
        
        if self.save_events_config(config):
            await interaction.response.send_message("✅ すべてのイベントを無効化しました", ephemeral=True)
        else:
            await interaction.response.send_message("❌ 設定の保存に失敗しました", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EventManagement(bot))
