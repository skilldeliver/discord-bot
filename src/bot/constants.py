from dataclasses import dataclass
from datetime import timedelta

PREFIX = "%"
PODKREPI_BG_GUILD_ID = 778984868146577458


@dataclass
class Color:
    green = int("0x34A853", base=16)
    red = int("0xE94235", base=16)


@dataclass
class GSuiteData:
    command_arguments_delimiter = ","
    command_fields_delimiter = ":"

    # every command field maps with a value
    # which determines if it is required or not
    # TODO replace False values with defaults :)
    create_command_fields = {
        "title": False,
        "start": True,
        "end": False,
        "duration": False,
        "participants": True,
        "description": False,
    }

    create_command_default_values = {
        # defining default values for an event
        "title": "No title",
        "description": "",
        "duration": timedelta(seconds=3600),  # 1h in seconds
    }
