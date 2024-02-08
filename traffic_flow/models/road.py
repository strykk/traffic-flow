# Postpone evaluation of annotations so you can use own class in a method definitions.
from __future__ import annotations

from collections import deque

import numpy as np

from .traffic_lights import TrafficLights
from .vehicle import Vehicle


class Road:
    """Single lane of a road in a simulation

    For now, it's simply given by a start and an end point on a 2d grid.
    The scale is 1 -> 1 m.
    """

    def __init__(
        self, start_point: tuple[int, int], end_point: tuple[int, int], road_name: str | int
    ) -> None:
        self.start_point = start_point
        self.end_point = end_point
        self.length = self._calculate_road_length()  # length in meters

        # TODO: Use graphs for it.
        self.next_roads: dict[str | int, Road] = {}
        self.road_name = road_name

        self.vehicles = deque[Vehicle]()  # type: ignore

        self.green_light = True
        self.traffic_lights: TrafficLights | None = None  # type: ignore # noqa

    def add_next_road(self, next_road: Road) -> None:
        self.next_roads[next_road.road_name] = next_road

    def get_next_road(self, road_name: str) -> Road:
        return self.next_roads[road_name]

    def set_traffic_lights(self, traffic_lights: "TrafficLights"):  # type: ignore # noqa
        self.traffic_lights = traffic_lights

    def set_green_light(self, green_light_state: bool) -> None:
        self.green_light = green_light_state

    def _calculate_road_length(self):
        # float() used to get rid of annoying warning.
        return float(np.linalg.norm(np.array(self.start_point) - np.array(self.end_point)))

    def add_vehicle(self, vehicle: "Vehicle") -> None:  # type: ignore # noqa
        self.vehicles.append(vehicle)

    def remove_vehicle(self) -> None:
        self.vehicles.popleft()
