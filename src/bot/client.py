from discord.ext import commands
from bot.db import BotDataBase
import aiomysql
import asyncio

extensions = ("bot.cogs.gsuite", "bot.cogs.server_fetch")

class BotClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        self.db = BotDataBase(self.loop)
        print("Connecting to the db!")
        while True:
            try:
                await self.db.connect()
                break
            except Exception as e:
                print(e)
                print("Retrying connecting to db...")
                await asyncio.sleep(3)

        for ext in extensions:
            try:
                self.load_extension(ext)
                print("Loaded the extension: ", ext)
            except Exception as e:
                print(f"Failed to load extension {ext}. {e}")
