from . import HTTP
import json
CLIENT = HTTP.HTTPClient()

# Models


class CurrentProfile():
    def __init__(self):
        """
        The current users profile.
        """
        self.credits = 0
        self.joinedAt = ''
        self.shipCount = 0
        self.structureCount = 0
        self.username = ''

    async def construct(self, resp: dict):
        user = resp['user']
        
        for k, v in user.items():
            setattr(self, k, v)

        return self

class FlightPlan:
    def __init__(self):
        self.arrivesAt = ''
        self.createdAt = ''
        self.departure = ''
        self.destination = ''
        self.distance = 0
        self.fuelConsumed = 0
        self.fuelRemaining = 0
        self.id = ''
        self.shipId = ''
        self.terminatedAt = None
        self.timeRemainingInSeconds = 0

    async def construct(self, resp):
        user = resp['flightPlan']
        
        for k, v in user.items():
            setattr(self, k, v)

        return self

class leaderboardEntry:
    def __init__(self):
        self.username = ''
        self.netWorth = 0
        self.rank = 0

    def construct(self, resp):
        
        for k, v in resp.items():
            setattr(self, k, v)

        return self