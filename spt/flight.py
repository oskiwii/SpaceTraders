from typing import Dict, Union


class FlightPlan:
    def __init__(self, data: Dict[str, Dict[str, Union[str, int, None]]]):
        data = data["flightPlan"]

        self.arrives = data.get("arrivesAt")
        self.created_at = data.get("createdAt")
        self.departure = data.get("departure")
        self.destination = data.get("destination")

        self.distance = data.get("distance")
        self.fuel_used = data.get("fuelConsumed")
        self.fuel_remaining = data.get("fuelRemaining")

        self.id = data.get("id")
        self.ship_id = data.get("shipId")

        self.terminated_at = data.get("terminatedAt")
        self.terminated = None if self.terminated_at is None else True
