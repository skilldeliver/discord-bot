"""
Main program for running the bot:

python -m bot
"""
import asyncio
import os

import discord

from bot.client import BotClient
from bot.constants import PREFIX


async def main():
    # create an intents object
    intents = discord.Intents.default()
    intents.members = True

    # create a Client object
    bot = BotClient(command_prefix=PREFIX, intents=intents)

    # run the bot with enviroment variable
    token = os.environ["BOT_TOKEN"]
    await bot.start(token)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
