from typing import Optional
from aiohttp import ClientSession, ClientResponse

import asyncio
import logging

class Route:
    def __init__(
        self, 
        url: Optional[str] = None,
        method: Optional[str] = None,
        headers: Optional[str] = None,
        json: Optional[str] = None,
        params: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """Make a Route for the HTTP Client"""
        self.url = url
        self.method = method
        self.headers = headers
        self.json = json
        self.params = params
        self.timeout = timeout
    
    def __str__(self):
        return self.url

    @property
    def kwargs(self):
        return {
            'url': self.url,
            'method': self.method,
            'headers': self.headers,
            'json': self.json,
            'params': self.params,
            'timeout': self.timeout,
        }
    
class HTTPClient:
    """Client for web requests"""
    def __init__(self, token: int):
        """Client for web requests. Requires a Token"""
        self.max_retries = 5
        self._log = logging.getLogger('http_module')
        self.token = token
        self.session: ClientSession = ClientSession(headers = {})

    async def request(self, route: Route) -> dict:
        """Make a request using a Route"""
        retries = 0
        _log = self._log.debug
        while retries <= self.max_retries:  # Max: 5 retries
            try:
                with self.session.request(**route.kwargs) as response:
                    response: ClientResponse

                    print(response.status)  
                    return await response.json()     
            except asyncio.TimeoutError:
                _log.warn(f'Request timed out after {route.timeout} seconds')
                retries += 1

        raise ReachedMaximumRetries(f'Hit max retries {self.max_retries}')