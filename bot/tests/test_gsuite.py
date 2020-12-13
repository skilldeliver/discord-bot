from collections import namedtuple
from datetime import datetime as dt, timedelta
import unittest

from bot.cogs.gsuite import GSuite

# TODO write dummy structures for these below:
class DiscordGuildStub:
    def __init__(self, roles):
        self.roles_map = self.__set_up_roles_map(roles)

    @staticmethod
    def __set_up_roles_map(roles):
        roles_map = dict()
        for role in roles:
            roles[role] = role.strip("<&>")
        return roles_map

    def get_role(self, role):
        return self.roles_map


class DiscordMessageMock:
    def __init__(self, guild, menitons, raw_mentions, role_menitons, raw_role_mentions):
        self.guild = guild
        self.menitons = menitons
        self.raw_mentions = raw_mentions
        self.role_menitons = role_menitons
        self.raw_role_mentions = raw_role_mentions


class TestGSuiteCog(unittest.TestCase):
    def setUp(self):
        roles = ["<@&786992565164441661>"]
        self.gsuite_cog = GSuite(bot=None)
        self.guild = DiscordGuildStub(roles)

    def test_create_command_parse(self):
        expected_command_parse_unordered = {
            "success": True,
            "reason": "",
            "fields": {
                "title": "Sprint planning",
                "start": dt.now() + timedelta(days=3),
                "duration": timedelta(hours=1),
                "participants": "<@!365859941292048384> <@&786992565164441661>",
                "description": "",
                "partcipants_ids": {365859941292048384},
            },
        }
        message = DiscordMessageMock(
            guild=self.guild,
            mentions=["<@365859941292048384"],
            raw_mentions=[365859941292048384],
            role_menitons=["<@&786992565164441661>"],
            raw_role_mentions=[786992565164441661],
        )
        self.assertEqual(
            self.gsuite_cog._create_command_parse(
                raw_arg=(
                    "title: Sprint planning,"
                    "start: after 3 days,"
                    "participants: <@!365859941292048384> <@&786992565164441661>"
                )
            ),
            expected_command_parse_unordered,
        )

    def test_create_command_embed(self):
        self.assertTrue("FOO".isupper())
        self.assertFalse("Foo".isupper())

    def test_split(self):
        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == "__main__":
    unittest.main()
