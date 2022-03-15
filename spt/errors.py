class SPTError(Exception):
    """Error that is raised for SpaceTraders"""


class HTTPError(SPTError):
    """Error that is raised for HTTP requests"""

    pass


class ReachedMaximumRetries(HTTPError):
    pass
