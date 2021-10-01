from spacetraders.errors import HTTPError
import aiohttp
import asyncio
import logging
import json

logging.getLogger('asyncio').setLevel(logging.CRITICAL)  # I know it isnt good, but still


class HTTPClient:
    def __init__(self):
        """
        Base HTTP Client for communication
        """

        self._client = aiohttp.ClientSession()
        self.log = logging.getLogger('spacetraders')

    async def communicate(self, requesttype: str = 'GET', url=None, headers: dict = None, params: dict = None):
        self.log.debug(f'Making request to {url} using {requesttype}, {headers}')

        # Get type function and run checks
        if requesttype not in ('GET', 'POST', 'PUT'):
            raise HTTPError(f'Request must be GET or POST, not {requesttype}')

        if url is None:
            raise HTTPError('URL is None')

        # Get the request function for the type we want
        # Better (but shitty) implementation than if's and else's
        send = getattr(self._client, requesttype.lower())

        response = await send(url, headers=headers, params=params)

        respjson = await response.json()
        self.log.debug(f'Recieved response for request {requesttype} {url}: {respjson}')

        

        with open('dump.json', 'w') as f:
            json.dump(respjson, f, indent=4)

        if 'error' in respjson:

            # THIS WILL BE REWORKED, IT SHALL BE BETTER!

            error = f'Error: {respjson["error"]["message"]}: {respjson["error"]["code"]}'
            self.log.critical(error)
            raise HTTPError(error)

        self.log.debug('Finished with request, returning response')
        return respjson

    async def _close_session(self):
        """
        Function to close the session
        """
        self.log.warn('Closing session!')
        await self._client.close()
