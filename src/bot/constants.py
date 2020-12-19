from dataclasses import dataclass
from datetime import datetime

PREFIX = ":"


@dataclass
class GSuiteData:
    # defining default values for an event
    title = "No title"
    description = ""
    duration = 3600  # 1h in seconds
