from collections import namedtuple
from datetime import datetime as dt, timedelta
import unittest

from random import randint
from bot.cogs.gsuite import GSuite
from bot.constants import Color


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


DiscordAuthorMock = namedtuple("DiscordAuthorMock", "display_name avatar_url")


class DiscordMessageMock:
    def __init__(self, guild, raw_mentions, raw_role_mentions):
        DiscordMentionMock = namedtuple("DiscordMentionMock", "mention")
        self.guild = guild
        self.mentions = [DiscordMentionMock(mention=f"<@!{m}>") for m in raw_mentions]
        self.raw_mentions = raw_mentions
        self.role_mentions = [
            DiscordMentionMock(mention=f"<@&{m}>") for m in raw_role_mentions
        ]
        self.raw_role_mentions = raw_role_mentions


class TestGSuiteCreateCommand(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.gsuite_cog = GSuite(bot=None)

    def _create_message(self, users, roles):
        message = DiscordMessageMock(
            guild=DiscordGuildStub(roles),
            raw_mentions=users,
            raw_role_mentions=list(roles.keys()),
        )
        return message

    def test_create_command_parse_defaults(self):
        """
        Test case for default values of create command parsing
        """
        users = [261115722007183362]
        users_mention = " ".join([f"<@!{u}>" for u in users])

        command_arg = f"start: Next week, participants: {users_mention}"

        expected = {
            "success": True,
            "reason": "",
            "fields": {
                "title": "No title",
                "start": GSuite._set_dt_resolution_to_min(dt.now()) + timedelta(days=7),
                "duration": timedelta(hours=1),
                "participants": f"{users_mention}",
                "description": "",
                "participants_ids": users,
            },
        }
        message = self._create_message(users, {})
        output = self.gsuite_cog._create_command_parse(
            raw_arg=command_arg, message=message
        )
        self.assertDictEqual(output, expected)

    def test_create_command_parse_unordered(self):
        users, roles = [365859941292048384], {786992565164441661: [365859941292048384]}
        users_mention = " ".join([f"<@!{u}>" for u in users])
        roles_mention = " ".join([f"<@&{r}>" for r in roles])

        command_arg = (
            f"participants: {users_mention} {roles_mention}, "
            "duration: 1 hour and 30 minutes, "
            "description: This is an event for our sprint planning, "
            "title: Sprint planning, start: In 3 days, "
        )

        expected = {
            "success": True,
            "reason": "",
            "fields": {
                "title": "Sprint planning",
                "start": GSuite._set_dt_resolution_to_min(dt.now()) + timedelta(days=3),
                "duration": timedelta(hours=1, minutes=30),
                "participants": f"{users_mention} {roles_mention}",
                "description": "This is an event for our sprint planning",
                "participants_ids": users,
            },
        }
        message = self._create_message(users, roles)
        output = self.gsuite_cog._create_command_parse(
            raw_arg=command_arg,
            message=message,
        )
        self.assertDictEqual(output, expected)

    def test_create_command_parse_end_field(self):
        users, roles = [576035433335619614, 161736242550013952, 269583153083973632], {
            786992565164441661: [
                430712909614809098,
                779268568336302091,
                779285629623599124,
            ]
        }
        users_mention = " ".join([f"<@!{u}>" for u in users])
        roles_mention = " ".join([f"<@&{r}>" for r in roles])

        command_arg = (
            "start: In 2 hours, "
            "end: In 4 hours, "
            "title: Emergency patch meeting, "
            f"participants: {roles_mention} {users_mention}"
        )

        expected = {
            "success": True,
            "reason": "",
            "fields": {
                "title": "Emergency patch meeting",
                "start": GSuite._set_dt_resolution_to_min(dt.now())
                + timedelta(hours=2),
                "duration": timedelta(hours=2),
                "participants": f"{roles_mention} {users_mention}",
                "description": "",
                "participants_ids": list(
                    set(users + list(i for v in roles.values() for i in v))
                ),
            },
        }
        message = self._create_message(users, roles)
        output = self.gsuite_cog._create_command_parse(
            raw_arg=command_arg,
            message=message,
        )
        self.assertDictEqual(output, expected)

    def test_create_command_parse_randomized(self):
        users, roles = [
            self._random_with_n_digits(18) for _ in range(randint(10, 15))
        ], {
            self._random_with_n_digits(18): [
                self._random_with_n_digits(18) for _ in range(randint(5, 10))
            ]
            for _ in range(randint(10, 15))
        }
        users_mention = " ".join([f"<@!{u}>" for u in users])
        roles_mention = " ".join([f"<@&{r}>" for r in roles])

        # TODO random mentions :)
        command_arg = (
            "start: In 2 hours, "
            "end: In 4 hours, "
            "title: Emergency patch meeting, "
            f"participants: {roles_mention} {users_mention}"
        )

        expected = {
            "success": True,
            "reason": "",
            "fields": {
                "title": "Emergency patch meeting",
                "start": GSuite._set_dt_resolution_to_min(dt.now())
                + timedelta(hours=2),
                "duration": timedelta(hours=2),
                "participants": f"{roles_mention} {users_mention}",
                "description": "",
                "participants_ids": list(
                    set(users + list(i for v in roles.values() for i in v))
                ),
            },
        }
        message = self._create_message(users, roles)
        output = self.gsuite_cog._create_command_parse(
            raw_arg=command_arg,
            message=message,
        )
        # TODO decide if this is a dirty fix for set unordering
        expected["fields"]["participants_ids"] = sorted(
            expected["fields"]["participants_ids"]
        )
        output["fields"]["participants_ids"] = sorted(
            output["fields"]["participants_ids"]
        )
        self.assertDictEqual(output, expected)

    def test_create_command_parse_missing_required_fields(self):
        command_arg = "title: Missing required fields"
        expected = {
            "success": False,
            "reason": "Missing required fields: start, participants",
            "fields": dict(),
        }
        message = self._create_message([], {})
        output = self.gsuite_cog._create_command_parse(
            raw_arg=command_arg,
            message=message,
        )
        self.assertDictEqual(output, expected)

    def test_create_command_invalid_participants(self):
        command_arg = "start: Tommorow, participants: Brooks"
        expected = {
            "success": False,
            "reason": "Invalid argument for participants: Brooks",
            "fields": dict(),
        }
        message = self._create_message([], {})
        output = self.gsuite_cog._create_command_parse(
            raw_arg=command_arg,
            message=message,
        )
        self.assertDictEqual(output, expected)

        command_arg = "start: Tommorow, participants: "
        expected = {
            "success": False,
            "reason": "No valid participants!",
            "fields": dict(),
        }
        message = self._create_message([], {})
        output = self.gsuite_cog._create_command_parse(
            raw_arg=command_arg,
            message=message,
        )
        self.assertDictEqual(output, expected)

    def test_create_command_embed_success(self):
        author = DiscordAuthorMock(
            display_name="Skilldeliver",
            avatar_url="https://cdn.discordapp.com/avatars/365859941292048384/3ff06472fa40b463dec368f818fbe3e7.png",
        )
        data = {
            "success": True,
            "reason": "",
            "fields": {
                "title": "General meeting",
                "start": dt(2020, 12, 11, 16, 0),
                "duration": timedelta(seconds=3600),
                "participants": "<@451118248616787968>",
                "description": "A meeting for adressing general questions.",
                "partcipants_ids": [451118248616787968],
            },
        }
        expected = {
            "title": "General meeting",
            "description": "A meeting for adressing general questions.",
            "color": Color.green,
            "author": {
                "name": "Skilldeliver created an event",
                "icon_url": "https://cdn.discordapp.com/avatars/365859941292048384/3ff06472fa40b463dec368f818fbe3e7.png",
            },
            "fields": [
                {"name": "Starts at: ", "value": "11, Dec (Friday) at 16:00"},
                {"name": "Ends at: ", "value": "11, Dec (Friday) at 17:00"},
                {"name": "Participants: ", "value": "<@451118248616787968>"},
            ],
        }
        output = self.gsuite_cog._create_command_embed_dict(data, author)
        self.assertDictEqual(expected, output)

    def test_create_command_embed_failed(self):
        author = DiscordAuthorMock(
            display_name="Skilldeliver",
            avatar_url="https://cdn.discordapp.com/avatars/365859941292048384/3ff06472fa40b463dec368f818fbe3e7.png",
        )
        data = {
            "success": False,
            "reason": "Invalid argument for participants: pi4",
            "fiealds": {},
        }

        expected = {
            "title": "Error!",
            "description": "Invalid argument for participants: pi4",
            "color": Color.red,
            "author": {
                "name": "Skilldeliver attempted to create an event",
                "icon_url": "https://cdn.discordapp.com/avatars/365859941292048384/3ff06472fa40b463dec368f818fbe3e7.png",
            },
        }
        output = self.gsuite_cog._create_command_embed_dict(data, author)
        self.assertDictEqual(expected, output)

    @staticmethod
    def _random_with_n_digits(n):
        range_start = 10 ** (n - 1)
        range_end = (10 ** n) - 1
        return randint(range_start, range_end)


if __name__ == "__main__":
    unittest.main()
