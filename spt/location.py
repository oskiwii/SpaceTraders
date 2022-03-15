from .http import HTTPClient


class Location:
    def __init__(self, http: HTTPClient, data: dict):
        self.allows_construction = data.get("allowsConstruction", False)
        self.docked_ships = data.get("dockedShips", None)
        self.name = data.get("name", None)
        self.symbol = data.get("symbol", None)
