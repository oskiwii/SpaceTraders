import logging
import asyncio

from .http import Route, HTTPClient
from .user import User


class Client:
    def __init__(self, token: str, **kwargs):
        """Client for Spacetraders"""
        self._log = logging.getLogger('spacetraders')
        self.http = HTTPClient(token, **kwargs)
         

        verbose = kwargs.get('verbose')
        if verbose is True:
            sh = logging.StreamHandler()
            sh.setLevel(logging.DEBUG)
            sh.setFormatter(logging.Formatter('[%(name)s]  %(levelname)s - %(message)s'))
            self._log.addHandler(sh)
            logging.getLogger('spacetraders-http').addHandler(sh)  # Add handler to HTTP logging

        # Attempt test of token
        loop = asyncio.get_event_loop()
        self.profile = User(loop.run_until_complete(self.test()))


    async def test(self):
        return await self.http.request(Route('get', 'https://api.spacetraders.io/my/account'))

    