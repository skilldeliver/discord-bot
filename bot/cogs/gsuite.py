import discord
from datetime import datetime

from bot.constants import GSuiteData

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
    async def create(self, ctx, *, raw_arg):
        """Creates a new event"""
        # TODO should the bot send invitation message in participants DMs?
        arguments = raw_arg.split(',')

        for field, arg in zip(GSuiteData.create_command_fields, arguments):
            pass

    @commands.command()
    async def edit(self, ctx):
        """Edits an existing event"""
        # TODO optional filters as argument to this command
        pass

    @commands.command()
    async def cancel(self, ctx):
        """Cancels an existing event"""
        # TODO add prompt "are you sure?"
        # TODO should the bot notify people in their DMs if an event is cancled?
        pass

    @commands.command()
    async def list_events(self, ctx):
        """LIst a events"""
        # TODO add filter support in arguments
        pass

    @staticmethod
    def create_command_parse(raw_arg: str) -> dict:
        """
        Parses a raw command string to separate arguments.
        """
        data = {
            'success': True,
            'reason': '', # reason if parsinng failed. :)
        }
        arguments = raw_arg.split(GSuiteData.command_arguments_delimiter)
        # filter arguments from empty values
        arguments = [a for a in arguments if len(a) > 0]

        # fill up the fields dictionary with arguments
        # this will make it easy to check arguments without particular order
        fields = GSuiteData.create_command_fields.copy()
        fields_delimiter = GSuiteData.command_fields_delimiter

        for arg in arguments:
            for field_name in fields:
                field_token = f'{field_name}{fields_delimiter}'
                if arg.startswith(field_token):
                    # Example of a border case - this is the behaviour
                    # >>> 'title: this is s title:'.split('title:')
                    # ['', ' this is a ', '']
                    fields[field_name] = arg.split(field_token)[1]
            else:
                pass

def setup(bot):
    bot.add_cog(GSuite(bot))
