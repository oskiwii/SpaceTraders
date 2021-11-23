from typing import Optional
from aiohttp import ClientSession, ClientResponse
from .errors import ReachedMaximumRetries, HTTPError
import asyncio
import logging
import json as _json

class Route:
    def __init__(
        self,
        method: Optional[str],
        url: Optional[str],
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        timeout: Optional[int] = None
    ):
        """Make a Route for the HTTP Client"""
        if method is None or url is None:
            raise HTTPError('Method or URL is None')

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
    def __init__(self, token: int, **kwargs):
        """Client for web requests. Requires a Token"""
        self.max_retries = 5 if not kwargs.get('max_retries', False) else kwargs.get('max_retries', False)
        self._log = logging.getLogger('spacetraders-http')
        self.__token = token
        self.session: ClientSession = ClientSession(headers = {'Authorization': f'Bearer {token}'})
        self.__lock = asyncio.Lock()

    async def __handle_status(self, response: ClientResponse):
        """Checks a reponse's `status_code` and raises an error"""

        code = response.status
        json = await response.json()

        if code in (401,):
            err = json.get('error')
            err_code = err.get('code', 'Unknown')
            err_message = err.get('message', 'Unknown Error')
            raise HTTPError(f'Code {err_code}: {err_message}')

    async def request(self, route: Route) -> dict:
        """Make a request using a Route"""
        retries = 0
        _log = self._log
        
        _log.debug(f'{route.method.upper()} {route.url} with params {route.json}')
        _log.debug(f'Maximum retries: {self.max_retries}')

        await self.__lock.acquire()
        while retries <= self.max_retries:  # Max: 5 retries
            try:
                async with self.session.request(
                    url = route.url,
                    method = route.method,
                    headers = route.headers,
                    json = route.json,
                    params = route.params,
                    timeout = route.timeout
                ) as response:
                    headers = dict(response.headers)
                    await self.__handle_status(response)

                    json = await response.json()
                    _log.debug(f'URL has returned {json}')
                    
                    remain = int(headers.get('x-ratelimit-remaining'))
                    wait_for = float(headers.get('Retry-After'))

                    if remain == 0 and wait_for != 0:
                        _log.warn(f'Client has hit ratelimit, locking and waiting for {wait_for} seconds')
                        await asyncio.sleep(wait_for)

                        _log.warn('Wait over, releasing lock and returning response')
                    
                    self.__lock.release()
                    return json

            except asyncio.TimeoutError:
                _log.warn(f'Request timed out after {route.timeout} seconds')
                
                try:
                    self.__lock.release()
                except:
                    pass    
                
                retries += 1

        self.__lock.release()
        raise ReachedMaximumRetries(f'Hit max retries {self.max_retries}')