from discord.ext import commands
from bot.db import BotDataBase

extensions = (
    "bot.cogs.gsuite",
)

class BotClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for ext in extensions:
            try:
                self.load_extension(ext)
            except Exception as e:
                print(f'Failed to load extension {ext}. {e}')
 
    async def load_db(self):
        self.db = await BotDataBase()
