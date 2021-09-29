# spacetraders
import logging
from typing import List

with open('spacetraders.log', 'w') as f:
    pass

logger = logging.getLogger('spacetraders')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler('spacetraders.log')
fh.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# add the handlers to logger
logger.addHandler(fh)

# ----------------


from spacetraders.HTTP import HTTPClient
from spacetraders.models import CurrentProfile, FlightPlan, leaderboardEntry
from spacetraders.errors import ClientError

import asyncio
import json


class User:
    pass


class Client(User):
    def __init__(self, token: str):
        """
        The client to communicate with the game. Represents you as the Player

        :param token: - type 'str' - the API token to authenticate with
        """

        self.log = logging.getLogger('spacetraders')
        self.http = HTTPClient()
        self.headers = {'Authorization': f'Bearer {token}'}
        self.token = token
        self.log.info(f'Initialised Client for {token}')

    async def profile(self) -> CurrentProfile:
        resp = await self.http.communicate('GET', 'https://api.spacetraders.io/my/account', headers = self.headers)
        profile = await CurrentProfile().profile(resp)
        return profile

    async def flightPlan(self, id: str) -> FlightPlan:
        """
        Gets the information of a Flight Plan using the ID

        Returns FlightPlan
        """
        resp = await self.http.communicate('GET', f'https://api.spacetraders.io/my/flight-plans/{id}', self.headers)
        plan = await FlightPlan().plan(resp)
        return plan

    async def makeFlightPlan(self, shipId, destination) -> FlightPlan:
        resp =  await self.http.communicate('POST', f'https://api.spacetraders.io/my/flight-plans', headers=self.headers, params={'shipId': shipId, 'destination': destination})
        plan = await FlightPlan().plan(resp)
        return plan

    async def serverStatus(self):
        resp = await self.http.communicate('GET', 'https://api.spacetraders.io/game/status')
        return resp['status']

    async def getLeaderboard(self) -> List[leaderboardEntry]:
        resp = await self.http.communicate('GET', 'https://api.spacetraders.io/game/leaderboard/net-worth', headers=self.headers)

        entries = []
        for entry in resp["netWorth"]:
            entries.append(leaderboardEntry().make(entry))

        return entries

    async def new_profile(self, name: str = None) -> CurrentProfile:
        """
        REMOVED - This function has been removed!
        -----------------------------------------

        Register a new profile using the username provided

        :param name:
        :return:
        """
        return None  # Blocks it from executing

        resp = await self.http.communicate('POST', f'https://api.spacetraders.io/users/{name}/claim')
        self.log.info(f'Made account: {resp["token"]}')
        
