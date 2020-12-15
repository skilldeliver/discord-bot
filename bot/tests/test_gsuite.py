from collections import namedtuple
import time
from datetime import datetime as dt, timedelta
import unittest

from bot.cogs.gsuite import GSuite

# TODO write dummy structures for these below:
class DiscordGuildStub:
    def __init__(self, roles_members_map):
        self.roles_membeers_map = roles_members_map
        self.DiscordRoleMock = namedtuple("DiscordRoleMock", "members")
        self.DiscordMemberMock = namedtuple("DiscordMemberMock", "id bot")

    def get_role(self, role):
        return self.DiscordRoleMock(
            members=[
                self.DiscordMemberMock(id=m, bot=False)
                for m in self.roles_membeers_map[role]
            ]
        )


class DiscordMessageMock:
    def __init__(self, guild, mentions, raw_mentions, role_mentions, raw_role_mentions):
        DiscordMentionMock = namedtuple("DiscordMentionMock", "mention")
        self.guild = guild
        self.mentions = [DiscordMentionMock(mention=m) for m in mentions]
        self.raw_mentions = raw_mentions
        self.role_mentions = [DiscordMentionMock(mention=m) for m in role_mentions]
        self.raw_role_mentions = raw_role_mentions


class TestGSuiteCog(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.gsuite_cog = GSuite(bot=None)

    def test_create_command_parse(self):
        user_id, role_id = 365859941292048384, 786992565164441661
        expected_command_parse_unordered = {
            "success": True,
            "reason": "",
            "fields": {
                "title": "Sprint planning",
                "start": dt.now() + timedelta(days=3),
                "duration": timedelta(hours=1),
                "participants": f"<@!{user_id}> <@&{role_id}>",
                "description": "",
                "participants_ids": [user_id],
            },
        }
        message = DiscordMessageMock(
            guild=DiscordGuildStub({786992565164441661: [365859941292048384]}),
            mentions=[f"<@!{user_id}>"],
            raw_mentions=[user_id],
            role_mentions=[f"<@&{role_id}>"],
            raw_role_mentions=[role_id],
        )
        gsuite_create_command_parse_output = self.gsuite_cog._create_command_parse(
            raw_arg="title: Sprint planning, start: In 3 days, participants: <@!365859941292048384> <@&786992565164441661>",
            message=message,
        )
        gsuite_create_command_parse_output["fields"][
            "start"
        ] = gsuite_create_command_parse_output["fields"]["start"].replace(
            microsecond=expected_command_parse_unordered["fields"]["start"].microsecond
        )
        self.assertDictEqual(
            gsuite_create_command_parse_output,
            expected_command_parse_unordered,
        )

    def test_create_command_embed(self):
        # what? what?
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
