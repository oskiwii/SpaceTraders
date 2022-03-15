import asyncio
import pprint

from .http import HTTPClient


class User:
    def __init__(self, data: dict):
        self.credits = data.get("credits", 0)
        self.joined_at = data.get("joinedAt", None)
        self.ship_count = data.get("shipCount", 0)
        self.structure_count = data.get("structureCount", 0)
        self.name = data.get("username", "None")


class PartialUser:
    """A user that is not full, such as those on a Leaderboard"""

    def __init__(self, data: dict):
        self.net_worth = data.get("netWorth", None)
        self.rank = data.get("rank", None)
        self.username = data.get("username", None)
