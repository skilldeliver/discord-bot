from datetime import datetime as dt, timedelta

import dateparser as dp
import discord
from discord.ext import commands

from bot.constants import Color, GSuiteData


class ServerFetch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(ServerFetch(bot))
