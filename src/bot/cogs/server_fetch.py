import asyncio
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
 
        dt_pivot = self.dt_now() # a pivot to compare which dt timestamp fields are not deleted

        members = await self.guild.fetch_members(limit=None).flatten()

        await self.fetch_roles()
        await self.fetch_users(users=members)
        await self.bot.db.delete_not_updated(dt_pivot)

    def cog_unload(self):
        self.db_fetcher.cancel()

    @db_fetcher.before_loop
    async def db_fetcher_wait(self):
        await self.bot.wait_until_ready()

    async def fetch_roles(self):
        # Fetching roles into the db after bot start
        for role in sorted(await self.guild.fetch_roles()):
            args = self.__role_to_dict(role)
            await self.bot.db.update_roles([args])

    async def fetch_role(self, role):
        args = self.__role_to_dict(role)
        await self.bot.db.update_roles([args])

    # used in the initial fetcher from above
    async def fetch_users(self, users):
        # Fetching users into the db after bot start
        users_data = []
        users_roles = []
        dt_pivot = self.dt_now() # a pivot to compare which dt timestamp fields are not deleted

        for member in users:
            if not member.bot:
                args = self.__user_to_dict(member)
                users_data.append(args)

                # args for user roles is a list
                args = self.__user_roles_to_dict(member)
                users_roles += args

        await self.bot.db.update_users(users_data)
        # TODO: remove not updated roles
        # TODO: https://github.com/aio-libs/aiomysql/blob/master/examples/example_pool.py

        await self.bot.db.update_role_user(users_roles)
        await self.bot.db.delete_not_updated_role_user(dt_pivot)

    async def fetch_user(self, user):
        dt_pivot = self.dt_now() # a pivot to compare which dt timestamp fields are not deleted

        if not user.bot:
            user_data = self.__user_to_dict(user)
            user_roles = self.__user_roles_to_dict(user)

            await self.bot.db.update_users([user_data])
            await self.bot.db.update_role_user(user_roles)
            await self.bot.db.delete_not_updated_role_user(dt_pivot, user_id=user.id)

    # TODO add guild check
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.fetch_user(user=user)

    # TODO add guild check
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.bot:
            await self.bot.db.delete_user(member.id)

    # TODO add guild check
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await self.fetch_user(user=after)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if not after.bot:
            member = self.guild.get_member(after.id)
            assert member is not None, 'Failed fetching user update'
            await self.fetch_user(user=member)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await self.fetch_role(role=role)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.bot.db.delete_role(role.id)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        await self.fetch_role(role=after)

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
                    updated_at=self.dt_now(),
                    created_at=role.created_at
                    )
    
    def __user_to_dict(self, member: discord.User) -> dict:
        return dict(
                    discord_user_id=member.id,
                    discord_username=str(member),
                    server_nickname=member.display_name,
                    discord_avatar_hash=hash(member.avatar_url),
                    updated_at=self.dt_now(),
                    created_at=self.dt_now()
                    )

    def __user_roles_to_dict(self, member) -> dict:
        user_roles = []

        for role in member.roles:
            args = {
                'user_id': member.id,
                'role_id': role.id,
                'updated_at': self.dt_now(),
                'created_at': self.dt_now()  
            }
            user_roles.append(args)
        return user_roles

    def dt_now(self):
        """
        MySQL permits fractional seconds for TIME , DATETIME , and TIMESTAMP values, with up to microseconds (6 digits) precision. 
        """
        now = dt.now()
        now = now.replace(microsecond=0)
        return now

def setup(bot):
    bot.add_cog(ServerFetch(bot))
