import asyncio
import aiomysql
from os import environ


def asyncinit(cls):
    """Decorator for an async instantiation of a class."""
    __new__ = cls.__new__

    async def init(obj, *arg, **kwarg):
        await obj.__init__(*arg, **kwarg)
        return obj

    def new(cls, *arg, **kwarg):
        obj = __new__(cls, *arg, **kwarg)
        coro = init(obj, *arg, **kwarg)
        return coro

    cls.__new__ = new
    return cls


@asyncinit
class BotDataBase:
    """
    Represents a interface to the MySQL database.
    """

    async def __init__(self):
        self.conn = await aiomysql.connect(
            user=environ["DB_USER"],
            password=environ["DB_PASS"].strip("'"),
            db=environ["DB_NAME"],
            port=int(environ["DB_PORT"]),
            host="localhost",
            autocommit=True,
        )
        await self._create_tables()

    #TODO: remove this function for debuging purposes
    async def query(self, arg):
        async with self.conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(arg)
            return await cur.fetchall()

    async def _create_tables(self):
        await self.__create_user_table()
        await self.__create_role_table()
        await self.__create_role_users_table()
        await self.__create_bot_administrators_table()

    async def __create_user_table(self):
        query = """
             CREATE TABLE IF NOT EXISTS `users`(
            `discord_user_id` bigint unsigned NOT NULL,
            `remember_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
            `discord_username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
            `discord_avatar_hash` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
            `server_nickname` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
            `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
            `created_at` timestamp NULL DEFAULT NULL,
            `updated_at` timestamp NULL DEFAULT NULL,
            PRIMARY KEY (`discord_user_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query)

    async def __create_role_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS `roles` (
            `discord_role_id` bigint unsigned NOT NULL,
            `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
            `color` mediumint unsigned NOT NULL,
            `has_pannel_access` tinyint(1) NOT NULL,
            `created_at` timestamp NULL DEFAULT NULL,
            `updated_at` timestamp NULL DEFAULT NULL,
            PRIMARY KEY (`discord_role_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query)

    async def __create_role_users_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS `role_user` (
            `user_id` bigint unsigned NOT NULL,
            `role_id` bigint unsigned NOT NULL,
            `created_at` timestamp NULL DEFAULT NULL,
            `updated_at` timestamp NULL DEFAULT NULL,
            PRIMARY KEY (`user_id`,`role_id`),
            KEY `role_user_role_id_foreign` (`role_id`),
            CONSTRAINT `role_user_role_id_foreign`
                FOREIGN KEY (`role_id`) REFERENCES `roles` (`discord_role_id`)
                ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT `role_user_user_id_foreign` 
                FOREIGN KEY (`user_id`) REFERENCES `users` (`discord_user_id`) 
                ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query)

    async def __create_bot_administrators_table(self):
        # TODO
        # query = """
        #     CREATE TABLE IF NOT EXISTS bot_administrators (
        #                 role_id BIGINT,
        #                 FOREIGN KEY (role_id) REFERENCES role(id),
        #                 PRIMARY KEY (role_id)
        #             )
        # """
        # async with self.conn.cursor() as cur:
        #     await cur.execute(query)
        pass

    async def update_users(
        self,
        data: list
    ) -> None:
        """
        data = [
            dict(discord_user_id = member.id,
                discord_username = str(member),
                server_nickname = member.display_name,
                discord_avatar_hash = hash(member.avatar_url),
                updated_at=dt.now(),
                created_at=dt.now()
                ),
            ...
            ]
        """

        query = """
            INSERT INTO users (discord_user_id, discord_username,
                              server_nickname, discord_avatar_hash,
                              updated_at, created_at)
            VALUES (%(discord_user_id)s, %(discord_username)s, 
                    %(server_nickname)s, %(discord_avatar_hash)s,
                    %(updated_at)s, %(created_at)s)
            ON DUPLICATE KEY UPDATE
                discord_username=VALUES(discord_username),
                server_nickname=VALUES(server_nickname),
                discord_avatar_hash=VALUES(discord_avatar_hash),
                updated_at=VALUES(updated_at)
        """
        async with self.conn.cursor() as cur:
            await cur.executemany(query, data)

    async def update_roles(
        self,
        data: list
    ):
        # NOTE: not updating has panel access if a new role has an admin permissions 
        query = """
            INSERT INTO roles (discord_role_id, name,
                              color, has_pannel_access, 
                              updated_at, created_at)
            VALUES (%(discord_role_id)s, %(name)s, 
                    %(color)s, %(has_pannel_access)s,
                    %(updated_at)s, %(created_at)s)
            ON DUPLICATE KEY UPDATE
                name=VALUES(name),
                color=VALUES(color),
                updated_at=VALUES(updated_at)
            """

        async with self.conn.cursor() as cur:
            await cur.executemany(query, data)

    async def update_role_user(self, data):
        # TODO Write docstring of the form of data
        query = """
            INSERT INTO role_user (user_id, role_id,
                                   updated_at, created_at)
            VALUES (%(user_id)s, %(role_id)s,
                    %(updated_at)s, %(created_at)s)
            ON DUPLICATE KEY UPDATE
                updated_at=VALUES(updated_at)
        """

        async with self.conn.cursor() as cur:
            await cur.executemany(query, data)


    async def delete_user(self, discord_user_id):
        query = """
            DELETE FROM users WHERE discord_user_id=%s;
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (discord_user_id,))

    async def delete_not_updated(self, dt_pivot):
        """Deletes all enties from users and roles which are not recently updated."""
        #TODO continue from here (roles deleting does not work properly)
        query = """
            DELETE FROM roles WHERE updated_at < %(dt_pivot)s;
            DELETE FROM users WHERE updated_at < %(dt_pivot)s;
        """
        #  
        async with self.conn.cursor() as cur:
            return await cur.execute(query, {'dt_pivot': dt_pivot,})

    async def insert_administrator(self, role_id: int) -> None:
        """Inserts a administrator role with role id into the database."""

        query = """
            INSERT INTO administrators (role)
            VALUES (%s)
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (role_id,))

    async def get_all_administrators(self):
        query = """
            SELECT role FROM administrators
        """
        async with self.conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query)
            return await cur.fetchall()


if __name__ == "__main__":

    async def run():
        db = await BotDataBase()
        print("Connected!", db)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
