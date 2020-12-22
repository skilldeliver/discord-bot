from datetime import datetime as dt, timedelta

import dateparser as dp
import discord
from discord.ext import commands

from bot.constants import Color, GSuiteData


class GSuite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def administrators(self, ctx, arg):
        # TODO should add initial check who can use this command
        # maybe only people with admin permissions
        # self.bot.reload_extension(f"bot.cogs.{arg}")
        # await ctx.send(f"bot.cogs.{arg} reloaded.")
        pass

    @commands.command()
    async def create(self, ctx, *, raw_arg):
        """Creates a new event"""
        # TODO should the bot send invitation message in participants DMs?

        # TODO consider using Converter https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#converters
        # instead of parsing with this method
        data = self._create_command_parse(raw_arg, ctx.message)
        await ctx.send(data)
        await ctx.send(
            embed=discord.Embed.from_dict(
                self._create_command_embed_dict(data, ctx.message.author)
            )
        )

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

    def _create_command_parse(self, raw_arg: str, message: discord.Message) -> dict:
        """
        Parses a raw command string to separate arguments.
        """
        data = {
            "success": True,
            "reason": str(),  # reason if parsinng failed. :)
            "fields": dict(),
        }
        arguments = raw_arg.split(GSuiteData.command_arguments_delimiter)
        # filter arguments from empty values
        arguments = [a for a in arguments if len(a) > 0]

        # fill up the fields dictionary with arguments
        # this will make it easy to check arguments without particular order
        fields = GSuiteData.create_command_fields.copy()
        fields_delimiter = GSuiteData.command_fields_delimiter

        try:
            for arg in arguments:
                for field_name in fields:
                    field_token = f"{field_name}{fields_delimiter}"
                    if arg.strip().startswith(field_token):
                        # Example of a border case - this is the behaviour
                        # >>> 'title: this is s title:'.split('title:')
                        # ['', ' this is a ', '']
                        fields[field_name] = arg.split(field_token)[1].strip()
                        break
            # fields contain only string values by now

            # check if the input is missing required field
            required_fields_missing = list()
            for key, value in fields.items():
                if value is True:
                    required_fields_missing.append(key)

            # TODO maybe remove this if the API is going to validate
            assert (
                len(required_fields_missing) == 0
            ), "Missing required fields: " + ", ".join(required_fields_missing)

            # now parse every field
            defaults = GSuiteData.create_command_default_values
            # TODO add check if command is passed in the past
            # START AND TITLE:
            fields["start"] = self._set_dt_resolution_to_min(dp.parse(fields["start"]))
            fields["title"] = fields["title"] if fields["title"] else defaults["title"]
            # DESCRIPION:
            fields["description"] = (
                fields["description"]
                if fields["description"]
                else defaults["description"]
            )
            # END:
            fields["duration"] = (
                (
                    self._set_dt_resolution_to_min(dp.parse(fields["end"]))
                    - fields["start"]
                )
                if fields["end"]
                else fields["duration"]
            )
            del fields["end"]
            # DURATION:
            if not isinstance(fields["duration"], timedelta):
                fields["duration"] = (
                    dt.now() - dp.parse(fields["duration"])
                    if fields["duration"]
                    else defaults["duration"]
                )
            # rounding up the seconds to the nearest 10th
            fields["duration"] = timedelta(
                seconds=round(fields["duration"].total_seconds(), -1),
                microseconds=0,
            )

            # PARTICIPANTS IDS:
            fields["participants_ids"] = self.__parse_particpants(
                fields["participants"], message
            )

        except Exception as e:

            data["success"] = False
            data["reason"] = str(e)
            return data

        data["fields"] = fields
        return data

    @staticmethod
    def __parse_particpants(participants: str, message: discord.Message) -> list:
        participants_ids = set()

        mentions = [m.mention.replace("!", "") for m in message.mentions]
        participants_mentions = dict(zip(mentions, message.raw_mentions))

        role_mentions = [m.mention for m in message.role_mentions]
        participants_role_mentions = dict(zip(role_mentions, message.raw_role_mentions))

        for token in participants.split():
            # tokens can be a profile tag or a role tag
            token = token.replace("!", "")
            try:
                user = participants_mentions[token]
                participants_ids.add(user)
            except KeyError:
                try:
                    role = message.guild.get_role(participants_role_mentions[token])
                    participants_ids = participants_ids.union(
                        set([i.id for i in role.members if not i.bot])
                    )
                except KeyError:
                    # TODO maybe leave this validation for participants despite the API support for validating
                    assert False, "Invalid argument for participants: " + token
        assert len(participants_ids) > 0, "No valid participants!"

        return list(participants_ids)

    @staticmethod
    def _create_command_embed_dict(data: dict, author) -> dict:
        if data["success"]:
            data = data["fields"]
            fields = list()
            fields = [
                {
                    "name": "Starts at: ",
                    "value": data["start"].strftime("%d, %b (%A) at %H:%M"),
                },
                {
                    "name": "Ends at: ",
                    "value": (data["start"] + data["duration"]).strftime(
                        "%d, %b (%A) at %H:%M"
                    ),
                },
                {"name": "Participants: ", "value": data["participants"]},
            ]

            embed_dict = {
                "title": data["title"],
                "description": data["description"],
                "color": Color.green,
                "author": {
                    "name": f"{author.display_name} created an event",
                    "icon_url": str(author.avatar_url),
                },
                "fields": fields,
            }

            return embed_dict
        else:
            return GSuite._command_error_embed_dict(data, author)

    @staticmethod
    def _command_error_embed_dict(data: dict, author) -> dict:
        embed_dict = {
            "title": "Error!",
            "description": str(data["reason"]),
            "color": Color.red,
            "author": {
                "name": f"{author.display_name} attempted to create an event",
                "icon_url": str(author.avatar_url),
            },
        }
        return embed_dict

    @staticmethod
    def _set_dt_resolution_to_min(obj: dt) -> dt:
        """
        Sets the resolution of a datetime object to minutes
        """
        if obj is not None:
            obj = obj.replace(second=0, microsecond=0)
        return obj


def setup(bot):
    bot.add_cog(GSuite(bot))
