"""
Main program for running the bot:

python -m bot
"""

import os

import discord
from discord.ext import commands

from bot.constants import PREFIX

# create an intents object
intents = discord.Intents.default()
intents.members = True

# create a Client object
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# loads an extenison for GSuite
bot.load_extension("bot.cogs.gsuite")

# run the bot with enviroment variable
token = os.environ["BOT_TOKEN"]
bot.run(token)
