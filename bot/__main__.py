"""
Main program for running the bot:

python -m bot
"""

import os

from discord.ext import commands

from bot.constants import PREFIX

# create a Client object
bot = commands.Bot(command_prefix=PREFIX)

# loads an extenison for GSuite
bot.load_extension("bot.cogs.gsuite")

# run the bot with enviroment variable
token = os.environ["BOT_TOKEN"]
bot.run(token)
