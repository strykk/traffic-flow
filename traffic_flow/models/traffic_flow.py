from __future__ import annotations

from collections import deque

from .traffic_lights import TrafficLights
from .vehicle import Vehicle


class TrafficFlow:
    """Single simulation of a traffic flow"""

    def __init__(
        self,
        vehicles_specification: list[dict],
        roadmap: dict[str, "Road"],  # type: ignore # noqa
        traffic_lights: list[TrafficLights] | None = None,
    ) -> None:
        self.time_step = 1 / 60  # seconds
        self.total_time = 120  # seconds

        self.vehicles_specification_queue = self._prepare_vehicles_specification_queue(
            vehicles_specification
        )

        self.vehicles = deque[Vehicle]()
        self.retired_vehicles = deque[Vehicle]()

        self.roadmap = roadmap
        self.traffic_lights = traffic_lights

        self.stop_simulation = False

    def _prepare_vehicles_specification_queue(
        self, vehicles_specification: list[dict]
    ) -> deque[dict]:
        if not vehicles_specification:
            raise ValueError("You cannot start simulation with no vehicle specified!")
        vehicles_specification = sorted(
            vehicles_specification, key=lambda vehicle_spec: vehicle_spec["ride_start_time"]
        )

        return deque(vehicles_specification)

    def start_vehicle_ride(self, vehicle_specification: dict) -> None:
        vehicle = Vehicle(**vehicle_specification)
        vehicle.start_ride(self.roadmap)

        self.vehicles.append(vehicle)

    def update(self):
        if not self.vehicles:
            if not self.vehicles_specification_queue:
                self.stop_simulation = True
            pass
        for _ in range(len(self.vehicles)):
            vehicle = self.vehicles.popleft()
            if vehicle.is_ride_finished:
                self.retired_vehicles.append(vehicle)
            else:
                self.vehicles.append(vehicle)

    def _gather_data(self):
        simulation_evolution = []
        travel_times = []

        for vehicle in self.retired_vehicles:
            travel_times.append(vehicle.travel_time)
        for vehicle in self.vehicles + self.retired_vehicles:
            simulation_evolution.append(vehicle.ride_data)

        self.simulation_evolution = simulation_evolution
        self.travel_times = travel_times

    def run(self):
        next_vehicle = self.vehicles_specification_queue.popleft()

        next_vehicle_ride_start_time = next_vehicle.pop(
            "ride_start_time"
        )  # NOTE: At the moment you cannot add vehicle at the same time.

        time = 0

        while not self.stop_simulation and time <= self.total_time:
            if next_vehicle_ride_start_time is not None and time >= next_vehicle_ride_start_time:
                self.start_vehicle_ride(next_vehicle)
                if self.vehicles_specification_queue:
                    next_vehicle = self.vehicles_specification_queue.popleft()
                    next_vehicle_ride_start_time = next_vehicle.pop("ride_start_time")
                else:
                    next_vehicle_ride_start_time = None

            for road in self.roadmap.values():
                for vehicle in list(road.vehicles):
                    vehicle.move(self.time_step)

            if self.traffic_lights:
                for trafffic_lights in self.traffic_lights:
                    trafffic_lights.tic(self.time_step)
            self.update()
            time += self.time_step

        self._gather_data()
