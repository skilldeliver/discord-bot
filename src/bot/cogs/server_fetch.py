from collections import defaultdict
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

    @commands.command(aliases=['q'])
    async def query(self, ctx, *, arg):
        o = await self.bot.db.query(arg)
        await ctx.send(o)

    @tasks.loop(count=1)
    async def db_fetcher(self):
        """Fetches Discord information into the DB after Cog loading."""

        assert self.guild is not None, "Server fetching failed, can't find the guild."
 
        dt_pivot = dt.now() # a pivot to compare which dt timestamp fields are not deleted
        s = time()

        members = await self.guild.fetch_members(limit=None).flatten()

        await self.fetch_roles()
        await self.fetch_users(users=members)
        await self.bot.db.delete_not_updated(dt_pivot)
        e = time()
        print('Done!', e-s)
        # TODO: remove time monitoring from above

    def cog_unload(self):
        self.db_fetcher.cancel()

    @db_fetcher.before_loop
    async def db_fetcher_wait(self):
        await self.bot.wait_until_ready()

    async def fetch_roles(self):
        # Fetching roles into the db after bot start
        roles_data = []
        for role in sorted(await self.guild.fetch_roles()):
            args = self.__role_to_dict(role)
            roles_data.append(args)

        await self.bot.db.update_roles(roles_data)

    async def fetch_users(self, users):
        # Fetching users into the db after bot start
        users_data = []
        users_roles = []
        for member in users:
            if not member.bot:
                args = self.__user_to_dict(member)
                users_data.append(args)

                # args for user roles is a list
                args = self.__user_roles_to_dict(member)
                users_roles += args

        await self.bot.db.update_users(users_data)
        await self.bot.db.update_role_user(users_roles)

    # TODO add guild check
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            await self.fetch_users(users=[member,])

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.bot:
            await self.bot.db.delete_user(member.id)

    # @commands.Cog.listener()
    # async def on_member_update(self, before, after):
    #     if not after.bot:
    #         await self.fetch_users(users=[after,])

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

    def __role_to_dict(self, role: discord.Role) -> dict:
         return  dict(
                    discord_role_id=role.id,
                    name=role.name,
                    color=role.color.value, 
                    has_pannel_access=role.permissions.administrator,
                    updated_at=dt.now(),
                    created_at=role.created_at
                    )
    
    def __user_to_dict(self, member: discord.User) -> dict:
        return dict(
                    discord_user_id=member.id,
                    discord_username=str(member),
                    server_nickname=member.display_name,
                    discord_avatar_hash=hash(member.avatar_url),
                    updated_at=dt.now(),
                    created_at=dt.now()
                    )

    def __user_roles_to_dict(self, member) -> dict:
        user_roles = []

        for role in member.roles:
            args = {
                'user_id': member.id,
                'role_id': role.id,
                'updated_at': dt.now(),
                'created_at': dt.now()
            }
            user_roles.append(args)
        return user_roles


def setup(bot):
    bot.add_cog(ServerFetch(bot))
