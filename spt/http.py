from aiohttp import ClientSession, ClientResponse
from .errors import ReachedMaximumRetries, HTTPError
from asyncio import AbstractEventLoop
from .route import Route
from threading import Lock

import asyncio
import logging


class HTTPClient:
    """Client for web requests"""

    def __init__(self, token: int, loop: AbstractEventLoop, **kwargs):
        """Client for web requests. Requires a Token"""
        self._max_retries = (
            5
            if not kwargs.get("max_retries", False)
            else kwargs.get("max_retries", False)
        )
        self._log = logging.getLogger("spacetraders-http")
        self.__token = token
        self.__session: ClientSession = ClientSession(
            headers={"Authorization": f"Bearer {token}"}
        )
        self.__lock = kwargs.get("lock", Lock())
        self.__loop: AbstractEventLoop = loop

        self.__kwargs = kwargs

    async def __handle_status(self, response: ClientResponse):
        """Checks a response's `status_code` and raises an error"""

        code = response.status

        if code in (401,):
            json = await response.json()
            err = json.get("error")
            err_code = err.get("code", "Unknown")
            err_message = err.get("message", "Unknown Error")
            raise HTTPError(f"Code {err_code}: {err_message}")

        elif code in (503,):
            raise HTTPError("Error 503: Service Unavailable")

    async def _request(self, route: Route) -> dict:
        """Make a request using a Route"""
        retries = 0
        _log = self._log
        timeout = (
            route.timeout
            if not self.__kwargs.get("timeout", False)
            else self.__kwargs.get("timeout", False)
        )


        _log.info(route.__str__())
        _log.info(route.kwargs)

        with self.__lock:
            while retries != self._max_retries:
                try:
                    async with self.__session.request(
                        url=route.url,
                        method=route.method,
                        headers=route.headers,
                        json=route.json,
                        params=route.params,
                        timeout=timeout,
                    ) as response:
                        headers = dict(response.headers)  # Maybe unnecessary?
                        await self.__handle_status(response)

                        json = await response.json()

                        remain = int(headers.get("x-ratelimit-remaining"))
                        wait_for = float(headers.get("Retry-After"))

                        if remain == 0 and wait_for != 0:
                            _log.warn(
                                f"Client has hit ratelimit, waiting for {wait_for} seconds"
                            )
                            await asyncio.sleep(wait_for)

                        return json

                except asyncio.TimeoutError:
                    _log.warn(f"Request timed out after {timeout} seconds")
                    retries += 1
                _log.info("Hit timeout")

        raise ReachedMaximumRetries(f"Hit maximum retries: {self._max_retries}")

        # ==================== Account ==================== #

    async def account(self):
        res = await self._request(
            Route("get", "https://api.spacetraders.io/my/account")
        )

        return res

    # ==================== Flight Plans ==================== #

    async def flight_plan_info(self, flightPlanId: str):
        res = await self._request(
            Route("get", f"https://api.spacetraders.io/my/flight-plans/{flightPlanId}")
        )

        return res

    async def flight_plan_create(self, shipId: str, destination: str):
        res = await self._request(
            Route(
                "get",
                "https://api.spacetraders.io/my/flight-plans",
                params={"shipId": shipId, "destination": destination},
            )
        )

        return res

    # ==================== Game ==================== #

    async def game_status(self):
        res = await self._request(
            Route("get", "https://api.spacetraders.io/game/status")
        )

        return res

    # ==================== Leaderboard ==================== #

    async def get_leaderboard(self):
        res = await self._request(
            Route("get", "https://api.spacetraders.io/game/leaderboard/net-worth")
        )

        return res

    # ==================== Loans ==================== #

    async def loan_get_all(self):
        res = await self._request(Route("get", "https://api.spacetraders.io/my/loans"))

        return res

    async def loan_pay(self, loanId: str):
        res = await self._request(
            Route("put", f"https://api.spacetraders.io/my/loans/{loanId}")
        )

        return res

    async def loan_take(self, type: str):
        res = await self._request(
            Route("post", "https://api.spacetraders.io/my/loans", params={"type": type})
        )

        return res

    # ==================== Locations ==================== #

    async def location_get_info(self, locationSymbol: str):
        res = await self._request(
            Route("get", f"https://api.spacetraders.io/locations/{locationSymbol}")
        )

        return res

    async def location_get_market(self, locationSymbol: str):
        res = await self._request(
            Route(
                "get",
                f"https://api.spacetraders.io/locations/{locationSymbol}/marketplace",
            )
        )

        return res

    async def location_get_ships(self, locationSymbol: str):
        res = await self._request(
            Route(
                "get", f"https://api.spacetraders.io/locations/{locationSymbol}/ships"
            )
        )

        return res

    # ==================== Purchase Orders and Sell Orders ==================== #

    async def order_purchase(self, shipId: str, good: str, quantity: int):
        res = await self._request(
            Route(
                "post",
                "https://api.spacetraders.io/my/purchase-orders",
                params={"shipId": shipId, "good": good, "quantity": quantity},
            )
        )

        return res

    async def order_sell(self, shipId: str, good: str, quantity: int):
        res = await self._request(
            Route(
                "post",
                "https://api.spacetraders.io/my/sell-orders",
                params={"shipId": shipId, "good": good, "quantity": quantity},
            )
        )

        return res

    # ==================== Ships ==================== #

    async def ship_purchase(self, location: str, type: str):
        res = await self._request(
            Route(
                "post",
                "https://api.spacetraders.io/my/ships",
                params={"location": location, "type": type},
            )
        )

        return res

    async def ship_get_info(self, shipId: str):
        res = await self._request(
            Route("get", f"https://api.spacetraders.io/my/ships/{shipId}")
        )

        return res

    async def ship_get_all(self):
        res = await self._request(Route("get", "https://api.spacetraders.io/my/ships"))

        return res

    async def ship_cargo_jettison(self, shipId: str, good: str, quantity: int):
        res = await self._request(
            Route(
                "post",
                f"https://api.spacetraders.io/my/ships/{shipId}/jettison",
                params={"shipId": shipId, "good": good, "quantity": quantity},
            )
        )

        return res

    async def ship_scrap(self, shipId: str):
        res = await self._request(
            Route("delete", f"https://api.spacetraders.io/my/ships/{shipId}/")
        )

        return res

    async def ship_cargo_transfer(
        self, fromShipId: str, toShipId: str, good: str, quantity: int
    ):
        res = await self._request(
            Route(
                "post",
                f"https://api.spacetraders.io/my/ships/{fromShipId}/transfer",
                params={
                    "fromShipId": fromShipId,
                    "toShipId": toShipId,
                    "good": good,
                    "quantity": quantity,
                },
            )
        )

        return res

    # ==================== Structures ==================== #

    async def structure_create_new(self, location: str, type: str):
        res = await self._request(
            Route(
                "post",
                f"https://api.spacetraders.io/my/structures",
                params={"location": location, "type": type},
            )
        )

        return res

    async def structure_deposit_owned(
        self, structureId: str, shipId: str, good: str, quantity: int
    ):
        res = await self._request(
            Route(
                "post",
                f"https://api.spacetraders.io/my/structures/{structureId}/deposit",
                params={
                    "structureId": structureId,
                    "shipId": shipId,
                    "good": good,
                    "quantity": quantity,
                },
            )
        )

        return res

    async def structure_deposit(
        self, structureId: str, shipId: str, good: str, quantity: int
    ):
        res = await self._request(
            Route(
                "post",
                f"https://api.spacetraders.io/structures/{structureId}/deposit",
                params={
                    "structureId": structureId,
                    "shipId": shipId,
                    "good": good,
                    "quantity": quantity,
                },
            )
        )

        return res

    async def structure_get_info(self, structureId):
        res = await self._request(
            Route(
                "get",
                f"https://api.spacetraders.io/structures/{structureId}",
                params={"structureId": structureId},
            )
        )

        return res

    async def structure_transfer_to_ship(
        self, structureId: str, shipId: str, good: str, quantity: int
    ):
        res = await self._request(
            Route(
                "post",
                f"https://api.spacetraders.io/my/structures/{structureId}/transfer",
                params={
                    "structureId": structureId,
                    "shipId": shipId,
                    "good": good,
                    "quantity": quantity,
                },
            )
        )

        return res

    async def structure_get_owned_info(self, structureId: str):
        res = await self._request(
            Route(
                "get",
                f"https://api.spacetraders.io/my/structures/{structureId}",
                params={"structureId": structureId},
            )
        )

        return res

    async def structure_get_all_info(self):
        res = await self._request(
            Route("get", "https://api.spacetraders.io/my/structures")
        )

        return res

    # ==================== Systems ==================== #

    async def system_get_all_available_ships(self, systemSymbol: str):
        res = await self._request(
            Route(
                "get",
                f"https://api.spacetraders.io/systems/{systemSymbol}/ship-listings",
                params={"systemSymbol": systemSymbol},
            )
        )

        return res

    async def system_get_all_flight_plans(self, systemSymbol: str):
        res = await self._request(
            Route(
                "get",
                f"https://api.spacetraders.io/systems/{systemSymbol}/flight-plans",
                params={"systemSymbol": systemSymbol},
            )
        )

        return res

    async def system_get_docked_ships(self, systemSymbol: str):
        res = await self._request(
            Route(
                "get",
                f"https://api.spacetraders.io/systems/{systemSymbol}/ships",
                params={"systemSymbol": systemSymbol},
            )
        )

        return res

    async def system_get_locations(self, systemSymbol: str):
        res = await self._request(
            Route(
                "get",
                f"https://api.spacetraders.io/systems/{systemSymbol}/locations",
                params={"systemSymbol": systemSymbol},
            )
        )

        return res

    async def system_get_info(self, systemSymbol: str):
        res = await self._request(
            Route(
                "get",
                f"https://api.spacetraders.io/systems/{systemSymbol}",
                params={"systemSymbol": systemSymbol},
            )
        )

        return res

    # ==================== Types ==================== #

    async def type_goods(self):
        res = await self._request(
            Route("get", "https://api.spacetraders.io/types/goods")
        )

        return res

    async def type_loans(self):
        res = await self._request(
            Route("get", "https://api.spacetraders.io/types/loans")
        )

        return res

    async def type_structures(self):
        res = await self._request(
            Route("get", "https://api.spacetraders.io/types/structures")
        )

        return res

    async def type_ships(self, ship_class: str = None):
        res = await self._request(
            Route(
                "get",
                "https://api.spacetraders.io/types/ships",
                params=None if ship_class is None else {"class": ship_class},
            )
        )

        return res

    # ==================== Users (i have no clue why this would be used) ==================== #

    async def username_claim(self, username: str):
        res = await self._request(
            Route(
                "post",
                f"https://api.spacetraders.io/users/{username}/claim",
                params={"username": username},
            )
        )

        return res

    # ==================== Warp Jump ==================== #

    async def warp_attempt(self, shipId: str):
        res = await self._request(
            Route(
                "post",
                "https://api.spacetraders.io/my/warp-jumps",
                params={"shipId": shipId},
            )
        )

        return res
