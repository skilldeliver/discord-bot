from discord.ext import commands
from bot.db import BotDataBase

extensions = ("bot.cogs.gsuite", "bot.cogs.server_fetch")


class BotClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        self.db = await BotDataBase()
        print("Loaded the db!")

        for ext in extensions:
            try:
                self.load_extension(ext)
                print("Loaded the extension: ", ext)
            except Exception as e:
                print(f"Failed to load extension {ext}. {e}")
