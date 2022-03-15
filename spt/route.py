from typing import Optional
from .errors import HTTPError


class Route:
    def __init__(
        self,
        method: Optional[str],
        url: Optional[str],
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        timeout: Optional[float] = 5.0,
    ):
        """Make a Route for the HTTP Client"""
        if method is None or url is None:
            raise HTTPError("Method or URL is None")

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
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "json": self.json,
            "params": self.params,
            "timeout": self.timeout,
        }
