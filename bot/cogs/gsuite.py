import discord
from datetime import datetime


class GSuite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def administrators(self, ctx):
        # TODO should add initial check who can use this command 
        # maybe only people with admin permissions
        """Sets a role or members to be administrators of the bot"""
        pass

    @commands.command()
    async def create(self, ctx):
        """Creates a new event"""
        pass

    @commands.command()
    async def edit(self, ctx):
        """Edits an existing event"""
        pass

    @commands.command()
    async def delete(self, ctx):
        """Deletes an existing event"""
        pass

    @commands.command()
    async def list_events(self, ctx):
        """LIst a events"""
        # TODO add filter support in arguments
        pass

def setup(bot):
    bot.add_cog(GSuite(bot))
