from collections import deque

import numpy as np


class Road:
    """Single lane of a road in a simulation

    For now, it's simply given by a start and an end point on a 2d grid.
    The scale is 1 -> 1 m.
    """

    def __init__(
        self, start_point: tuple[int, int], end_point: tuple[int, int], index: str | int
    ) -> None:
        self.start_point = start_point
        self.end_point = end_point
        self.length = self._calculate_road_length()  # length in meters

        self.index = index
        self.vehicles = deque["Vehicle"]()  # type: ignore

    def _calculate_road_length(self):
        return np.linalg.norm(np.array(self.start_point) - np.array(self.end_point))

    def add_vehicle(self, vehicle: "Vehicle") -> None:  # type: ignore # noqa
        self.vehicles.append(vehicle)

    def update(self, time_step) -> list[float]:
        leading_vehicle = None
        positions = []

        for vehicle in list(self.vehicles):
            vehicle_position = vehicle.move(time_step, leading_vehicle)

            leading_vehicle = vehicle
            if vehicle_position > self.length:
                self.vehicles.popleft()
            else:
                positions.append(vehicle_position)

        return positions
