from . import HTTP
import json
import logging
log = logging.getLogger('spacetraders')
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

        log.debug('Made a currentProfile object')
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

        log.debug('Made a flightPlan object')
        return self

class leaderboardEntry:
    def __init__(self):
        self.username = ''
        self.netWorth = 0
        self.rank = 0

    def construct(self, resp):
        
        for k, v in resp.items():
            setattr(self, k, v)

        log.debug('Made a leaderboardEntry object')
        return self

class loan:
    def __init__(self):
        self.due = ''
        self.id = ''
        self.repaymentAmount = 0
        self.status = ''
        self.type = ''

    def construct(self, resp):

        for k, v in resp.items():
            setattr(self, k, v)

        log.debug('Made a loan object')