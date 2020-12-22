from datetime import datetime as dt, timedelta
from pathlib import PurePath
import dateparser as dp
import io

import discord
from discord.ext import tasks
from discord.ext import commands
from time import time

from bot.constants import Color, GSuiteData, PODKREPI_BG_GUILD_ID


class ServerFetch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(PODKREPI_BG_GUILD_ID)
        self.db_fetcher.start()

    @tasks.loop(count=1)
    async def db_fetcher(self):
        """Fetches Discord information into the DB."""
        
        assert self.guild is not None, "Server fetching failed, can't find the guild."

        async for member in guild.fetch_members(limit=None):
            if not member.bot:
                mem = {
                    "id": member.id,
                    "nickname": member.display_name,
                    "username": str(member),
                }

                await self.bot.db.update_user(
                    discord_user_id=member.id,
                    discord_username=str(member),
                    server_nickname=member.display_name,
                    discord_avatar_hash=hash(member.avatar_url),
                    updated_at=dt.now(),
                )
                print(member.name)

    def cog_unload(self):
        self.db_fetcher.cancel()

    @db_fetcher.before_loop
    async def db_fetcher_wait(self):
        await self.bot.wait_until_ready()

    async def __update_member(self, member):
        await self.bot.db.update_user(
            discord_user_id=member.id,
            discord_username=str(member),
            server_nickname=member.display_name,
            discord_avatar_hash=hash(member.avatar_url),
            updated_at=dt.now(),
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            await self.__update_member(member)

    @command.Cog.listener()
    async def on_member_remove(self, member):
        if not member.bot:
            await self.bot.db.delete_user(member.id)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not after.bot:
            await self.__update_member(after)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if not after.bot:
            member = self.guild.get_member(after.id)
        assert member is not None, 'Failed fetching user update'

        await self.__update_member(member)

    # on_member_join
    # on_member_remove
    # on_member_update
    # on_user_update

    # on_guild_role_create
    # on_guild_role_delete
    # on_guild_role_update


def setup(bot):
    bot.add_cog(ServerFetch(bot))
