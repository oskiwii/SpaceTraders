import logging
import asyncio
import traceback
import pprint

from .http import Route, HTTPClient
from .user import User, PartialUser
from .flight import FlightPlan
from .loan import Loan
from .ship import Ship
from .structure import Structure, OwnedStructure

from typing import Coroutine, Dict, List, Tuple


class __Colour:
    """
    An class holding colour codes.
    """

    black = "\033[0;30m"
    red = "\033[0;31m"
    green = "\033[0;32m"
    brown = "\033[0;33m"
    blue = "\033[0;34m"
    purple = "\033[0;35m"
    cyan = "\033[0;36m"
    lightgrey = "\033[0;37m"
    grey = "\033[1;30m"
    lightred = "\033[1;31m"
    lime = "\033[1;32m"
    yellow = "\033[1;33m"
    lightblue = "\033[1;34m"
    lightpurple = "\033[1;35m"
    lightcyan = "\033[1;36m"
    white = "\033[1;37m"
    bold = "\033[1m"
    faint = "\033[2m"
    italic = "\033[3m"
    underline = "\033[4m"
    blink = "\033[5m"
    crossed = "\033[9m"
    end = "\033[0m"


class Client:
    def __init__(self, token: str, **kwargs):
        """Client for Spacetraders"""
        self._log = logging.getLogger("spacetraders")
        self.loop: asyncio.AbstractEventLoop = (
            asyncio.get_event_loop()
            if kwargs.get("loop", None) is None
            else kwargs.get("loop", None)
        )
        self.http = HTTPClient(token, self.loop, **kwargs)
        self.events: Dict[str, List[Coroutine]] = {"on_ready": [self.on_ready]}

        # Attempt test of token
        # self.profile = User(loop.run_until_complete(self.test()))

    async def on_ready(self):
        pass

    def event(self, event_name: str = None):
        def inner(func: Coroutine):
            """Register an event. Must be a coroutine"""
            name = func.__name__ if event_name is None else event_name

            # Look up the name in the event's dictionary and see if they are registered
            is_present = self.events.get(name, False)

            if not is_present:
                self.events[name] = [
                    func,
                ]

                return func

            else:
                self.events[name].append(func)

            return func

        return inner

    def _raise_warning(self):
        print(__Colour.red)
        traceback.print_exc()
        print(__Colour.end)

    async def _dispatch(self, event_name: str):
        """Dispatches an event. The event must be a coroutine"""
        self._log.info(f"Dispatching event {event_name}")
        coro_list = self.events.get(event_name, None)

        if coro_list is None or len(coro_list) == 0:
            self._log.warning(f"Event {event_name} is not registered to any coroutines")
            return

        for coro in coro_list:
            try:
                if not asyncio.iscoroutinefunction(coro):
                    self._log.warning(
                        f"Event {event_name} func {coro.__name__} is not a coroutine"
                    )
                    continue
                await coro()
            except Exception:
                self._raise_warning()

    def start(self, func: Coroutine = None):
        """
        Starts the bot. Pass in `func` to be executed

        Equivalant to
        ```
        try:
            self.loop.run_until_complete(func())
        except Exception as e:
            raise e
        """

        try:
            self.loop.create_task(self._dispatch("on_ready"))
            self.loop.run_until_complete(func())
        except Exception as e:
            raise e

    @property
    async def account(self) -> User:
        result = await self.http.account()

        return User(result.get("user", {"none": None}))

    @property
    async def online(self):
        result = await self.http.game_status()
        if result.get("status", False):
            return True

        return False

    @property
    async def leaderboard(self):
        result = await self.http.get_leaderboard()

        return [PartialUser(x) for x in result["netWorth"]]

    @property
    async def loans(self) -> List[Loan]:
        result = await self.http.loan_get_all()

        return [Loan(self.http, x) for x in result["loans"]]

    @property
    async def ships(self) -> List[Ship]:
        result = await self.http.ship_get_all()

        return [Ship(self.http, x) for x in result["ships"]]

    @property
    async def structures(self) -> List[OwnedStructure]:
        result = await self.http.structure_get_all_info()

        return [OwnedStructure(self.http, x) for x in result["structures"]]
