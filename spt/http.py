from aiohttp import ClientSession, ClientResponse
from .errors import ReachedMaximumRetries, HTTPError
from asyncio import AbstractEventLoop
from .route import Route


import asyncio
import logging
    
class HTTPClient:
    """Client for web requests"""
    def __init__(self, token: int, loop: AbstractEventLoop, **kwargs):
        """Client for web requests. Requires a Token"""
        self.max_retries = 5 if not kwargs.get('max_retries', False) else kwargs.get('max_retries', False)
        self._log = logging.getLogger('spacetraders-http')
        self.__token = token
        self.session: ClientSession = ClientSession(headers = {'Authorization': f'Bearer {token}'})
        self.__lock = asyncio.Lock()
        self.loop: AbstractEventLoop = loop

        self.kwargs = kwargs

    async def __handle_status(self, response: ClientResponse):
        """Checks a reponse's `status_code` and raises an error"""

        code = response.status
        

        if code in (401,):
            json = await response.json()
            err = json.get('error')
            err_code = err.get('code', 'Unknown')
            err_message = err.get('message', 'Unknown Error')
            raise HTTPError(f'Code {err_code}: {err_message}')

        elif code in (503,):
            raise HTTPError('Error 503: Service Unavailable')

    async def request(self, route: Route) -> dict:
        """Make a request using a Route"""
        retries = 0
        _log = self._log
        timeout = route.timeout if not self.kwargs.get('timeout', False) else self.kwargs.get('timeout', False)
        
        _log.debug(f'{route.method.upper()} {route.url} with params {route.json}')

        async with self.__lock:
            while retries != self.max_retries:
                try:
                    async with self.session.request(
                        url = route.url,
                        method = route.method,
                        headers = route.headers,
                        json = route.json,
                        params = route.params,
                        timeout = timeout
                    ) as response:

                        headers = dict(response.headers)
                        await self.__handle_status(response)

                        json = await response.json()
                        
                        remain = int(headers.get('x-ratelimit-remaining'))
                        wait_for = float(headers.get('Retry-After'))

                        if remain == 0 and wait_for != 0:
                            _log.warn(f'Client has hit ratelimit, locking and waiting for {wait_for} seconds')
                            await asyncio.sleep(wait_for)

                        return json

                except asyncio.TimeoutError:
                    _log.warn(f'Request timed out after {timeout} seconds')
                    retries += 1

        raise ReachedMaximumRetries(f'Hit maximum retries: {self.max_retries}') 

                 


    async def account(self):
        """Get User"""
        res = await self.request(Route('get', 'https://api.spacetraders.io/my/account'))

        return res

    async def get_flight_plan(self, id: str):
        res = await self.request(Route('get', f'https://api.spacetraders.io/my/flight-plans/{id}'))

        return res

    async def create_flight_plan(self, id: str, destination: str):
        res = await self.request(
            Route(
                'get', 'https://api.spacetraders.io/my/flight-plans',
                params = {'shipId': id, 'destination': destination}
            )
        )

        return res

    async def get_game_status(self):
        res = await self.request(Route('get', 'https://api.spacetraders.io/game/status'))

        return res

    async def get_leaderboard(self):
        res = await self.request(Route('get', 'https://api.spacetraders.io/game/leaderboard/net-worth'))

        return res

    async def get_loans(self):
        res = await self.request(Route('get', 'https://api.spacetraders.io/my/loans'))

        return res

    async def pay_loan(self, id: str):
        res = await self.request(Route('put', f'https://api.spacetraders.io/my/loans/{id}'))

        return res

    async def take_loan(self, type: str):
        res = await self.request(
            Route(
                'post', 'https://api.spacetraders.io/my/loans',
                params = {'type': type}
            )
        )

        return res

    async def get_location(self, symbol: str):
        res = await self.request(Route('get', f'https://api.spacetraders.io/locations/{symbol}'))

        return res

    async def get_location_marketplace(self, symbol: str):
        res = await self.request(Route('get', f'https://api.spacetraders.io/locations/{symbol}/marketplace'))

        return res

    async def get_location_ships(self, symbol: str):
        res = await self.request(Route('get', f'https://api.spacetraders.io/locations/{symbol}/ships'))

        return res

    async def make_purchase(self, id: str, good: str, quantity: int):
        res = await self.request(
            Route(
                'post', 'https://api.spacetraders.io/my/purchase-orders',
                params = {'shipId': id, 'good': good, 'quantity': quantity}
            )
        )

        return res

    async def make_sell(self, id: str, good: str, quantity: int):
        res = await self.request(
            Route(
                'post', 'https://api.spacetraders.io/my/sell-orders',
                params = {'shipId': id, 'good': good, 'quantity': quantity}
            )
        )

    async def purchase_ship(self, location: str, type: str):
        res = await self.request(
            Route(
                'post', 'https://api.spacetraders.io/my/ships',
                params = {'location': location, 'type': type}
            )
        )

        return res

    async def get_ship_info(self, id: str):
        res = await self.request(Route('get', f'https://api.spacetraders.io/my/ships/{id}'))

        return res

    async def get_ships_info(self):
        res = await self.request(Route('get', 'https://api.spacetraders.io/my/ships'))

        return res

    async def jettison_cargo(self, id: str, good: str, quantity: int):
        res = await self.request(
            Route(
                'post', f'https://api.spacetraders.io/my/ships/{id}/jettison',
                params = {'shipId': id, 'good': good, 'quantity': quantity}
            )
        )

        return res

    async def scrap_ship(self, id: str):
        res = await self.request(Route('delete', f'https://api.spacetraders.io/my/ships/{id}/'))

        return res

    async def transfer_cargo(self, from: str, to: str, good: str, quantity: str)