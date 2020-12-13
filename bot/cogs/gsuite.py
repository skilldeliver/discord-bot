from datetime import datetime

import dateparser
import discord
from discord.ext import commands

from bot.constants import Color, GSuiteData


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
            print(fields)
            # now parse every field
            required_fields = list()
            participants_ids = set()

            for key, value in fields.items():
                # START
                if key == "start" and fields["start"] is not True:
                    fields["start"] = dateparser.parse(fields["start"])
                    # TODO add check if command is passed in the past
                # END
                elif key == "end" and fields["start"] is not True:
                    start = fields["start"]
                    if not isinstance(start, datetime):
                        start = dateparser.parse(fields["start"])

                    fields["duration"] = dateparser.parse(fields["end"]) - start
                # DURATION
                elif (
                    key == "duration" and not fields["duration"]
                ):  # if it is not set by the 'end' field
                    fields["duration"] = datetime.now() - dateparser.parse(
                        fields["duration"]
                    )
                # PARTICIPANTS
                elif key == "participants":

                    participants_mentions = dict(
                        zip(
                            [m.mention.replace("!", "") for m in message.mentions],
                            message.raw_mentions,
                        )
                    )
                    participants_role_mentions = dict(
                        zip(
                            [m.mention.replace("!", "") for m in message.role_mentions],
                            message.raw_role_mentions,
                        )
                    )

                    print(participants_mentions)
                    print(participants_role_mentions)

                    for token in fields["participants"].split():
                        # tokens can be a profile tag or a role tag
                        token = token.replace("!", "")

                        try:
                            user = self.bot.get_user(participants_mentions[token])
                            participants_ids.add(user.id)
                        except Exception as e:
                            print(e)
                            try:
                                role = message.guild.get_role(
                                    participants_role_mentions[token]
                                )
                                participants_ids.union(set([i for i in role.members]))
                            except Exception as e:
                                print(e)
                                fields["success"] = False
                                fields[
                                    "reason"
                                ] = f"Invalid argument for participants: {token}"
                                return fields

                # check if requited field is missing
                # if it is not requiref fields - assign default value
                if isinstance(value, bool):
                    if value:
                        required_fields.append(key)
                    else:
                        fields[key] = GSuiteData.create_command_default_values[key]
        except Exception as e:
            data["success"] = False
            data["reason"] = e

        if len(required_fields) > 0:
            data["success"] = False
            data["reason"] = f'Missing required fields: {" ".join(required_fields)}'

        del fields["end"]
        if len(participants_ids) > 0:
            fields["partcipants_ids"] = participants_ids
        else:
            data["success"] = False
            data["reason"] = "No valid participants!"

        data["fields"] = fields
        return data

    @staticmethod
    def _create_command_embed_dict(data: dict, author) -> dict:
        if data["success"]:
            data = data["fields"]
            fields = list()
            fields = [
                {"name": "Starts at: ", "value": str(data["start"])},
                {"name": "Ends at: ", "value": str(data["start"] + data["duration"])},
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
            return self._command_error_embed_dict(data, author)

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

def setup(bot):
    bot.add_cog(GSuite(bot))
