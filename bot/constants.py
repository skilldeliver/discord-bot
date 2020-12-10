from dataclasses import dataclass
from datetime import datetime

PREFIX = "%"

@dataclass
class GSuiteData:
    # defining default values for an event
    title = "No title"
    description = ""
    duration = 3600  # 1h in seconds

    command_arguments_delimiter = ','
    command_fields_delimiter = ':'

    # every command field maps with a value
    # which determines if it is required or not
    create_command_fields = {
        'title': False,
        'start': True,
        'end': False,
        'duration': False,
        'participants': True,
        'description': False
    }
