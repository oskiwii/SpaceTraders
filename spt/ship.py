from __future__ import annotations
from typing import Union, Tuple

from .flight import FlightPlan
from .http import HTTPClient
from .location import Location
from .structure import Structure, OwnedStructure


class ShipInfo:
    ...


class Ship:
    def __init__(self, http: HTTPClient, data: dict) -> None:
        self.http = http
        self.data = data

        self.cargo = data.get("cargo", [])
        self.ship_class = data.get("class", None)
        self.id = data.get("id", None)
        self.location = Location(data.get("location"))
        self.manufacturer = data.get("manufacturer")
        self.max_cargo = data.get("maxCargo", 0)
        self.plating = data.get("plating", 0)
        self.spaceAvailable = data.get("spaceAvailable", 0)
        self.speed = data.get("speed", 0)
        self.ship_type = data.get("type", None)
        self.weapons = data.get("weapons", 0)

        self.x, self.y = data.get("x", 0), data.get("y", 0)

        self.flight_plan_id = data.get("flightPlanId", None)

    async def travel_to(
        self, destination: Union[str, Location, Structure, OwnedStructure]
    ) -> FlightPlan:
        if isinstance(destination, str):
            result = await self.http.flight_plan_create(self.id, destination)

        elif isinstance(destination, Location):
            result = await self.http.flight_plan_create(self.id, destination.__str__())

        elif isinstance(destination, Structure) or isinstance(
            destination, OwnedStructure
        ):
            result = await self.http.flight_plan_create(self.id, destination.location)

        else:
            raise Exception("Type is not of (str, Location, Structure, OwnedStructure)")

        return FlightPlan(self.http, result)

    @property
    async def flight_plan(self) -> Union[None, FlightPlan]:
        if self.flight_plan_id is None:
            return

        result = await self.http.flight_plan_info(self.flight_plan_id)

        return FlightPlan(self.http, result)

    async def purchase(self, good: str, quantity: int) -> (int, Order):
        result = await self.http.order_purchase(self.id, good, quantity)

        self.__init__(self.http, result.get("ship", None))
        return result.get("credits", None), Order(result.get("order", None))

    async def sell(self, good: str, quantity: int) -> (int, Order):
        result = await self.http.order_sell(self.id, good, quantity)

        self.__init__(self.http, result.get("ship", None))
        return result.get("credits", None), Order(result.get("order"))

    async def update(self):
        result = await self.http.ship_get_info(self.id)
        self.__init__(self.http, result.get("ship", None))
        return

    async def jettison(self, good: str, amount: int):
        result = await self.http.ship_cargo_jettison(self.id, good, amount)

        return result  # TODO: Maybe make an object for this ?  | Or, return the 'quantityRemaining' attribute ?

    async def scrap(self):
        result = await self.http.ship_scrap(self.id)

        return result["success"]

    async def transfer_cargo(
        self, target_ship: Union[str, Ship], good: str, amount: int
    ) -> Tuple[Ship, Ship]:
        if isinstance(target_ship, str):
            result = await self.http.ship_cargo_transfer(
                self.id, target_ship, good, amount
            )

        elif isinstance(target_ship, Ship):
            result = await self.http.ship_cargo_transfer(
                self.id, target_ship.id, good, amount
            )

        else:
            raise Exception("Type is not of (str, Ship)")

        return Ship(self.http, result["fromShip"]), Ship(self.http, result["toShip"])

    async def deposit_to_owned_structure(
        self, structure: Union[OwnedStructure, str], good: str, quantity: int
    ):
        if isinstance(structure, OwnedStructure):
            result = await self.http.structure_deposit_owned(
                structure.id, self.id, good, quantity
            )

        elif isinstance(structure, str):
            result = await self.http.structure_deposit_owned(
                structure, self.id, good, quantity
            )

        else:
            raise Exception("Type is not of (OwnedStructure, str)")

        self.__init__(self.http, result.get("ship", None))

        return OwnedStructure(self.http, result.get("structure"))

    async def deposit_to_structure(
        self, structure: Union[Structure, str], good: str, quantity: int
    ):
        if isinstance(structure, Structure):
            result = await self.http.structure_deposit(
                structure.id, self.id, good, quantity
            )

        elif isinstance(structure, str):
            result = await self.http.structure_deposit(
                structure, self.id, good, quantity
            )

        else:
            raise Exception("Type is not of (OwnedStructure, str)")

        self.__init__(self.http, result.get("ship", None))

        return OwnedStructure(self.http, result.get("structure"))

    async def transfer_to_ship(
        self, structure: Union[OwnedStructure, str], good: str, quantity: int
    ):
        if isinstance(structure, Structure):
            result = await self.http.structure_transfer_to_ship(
                structure.id, self.id, good, quantity
            )

        elif isinstance(structure, str):
            result = await self.http.structure_transfer_to_ship(
                structure, self.id, good, quantity
            )

        else:
            raise Exception("Type is not of (OwnedStructure, str)")

        self.__init__(self.http, result.get("ship", {"none": None}))

        return self, OwnedStructure(self.http, result.get("structure"))
