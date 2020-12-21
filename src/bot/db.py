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

    async def _create_tables():
        pass

    async def fetch_info(members, roles):
        pass

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
