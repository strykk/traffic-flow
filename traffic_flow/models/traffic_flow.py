from collections import deque

from traffic_flow.models.vehicle import Vehicle


class TrafficFlow:
    """Single simulation of a traffic flow"""

    def __init__(self) -> None:
        self.time_step = 1 / 60  # seconds
        self.total_time = 120  # seconds

        self.vehicles = deque[Vehicle]()
        self.retired_vehicles = deque[Vehicle]()

    def add_vehicle(self, vehicle: Vehicle) -> None:
        self.vehicles.append(vehicle)

    def update(self):
        if not self.vehicles:
            pass
        for _ in range(len(self.vehicles)):
            vehicle = self.vehicles.popleft()
            if vehicle.is_ride_finished:
                self.retired_vehicles.append(vehicle)
            else:
                vehicle.move(self.time_step)
                self.vehicles.append(vehicle)

    def _gather_data(self):
        simulation_evolution = []

        for vehicle in self.vehicles + self.retired_vehicles:
            simulation_evolution.append(vehicle.ride_data)

        self.simulation_evolution = simulation_evolution

    def run(self):
        time = self.time_step

        while time <= self.total_time:
            self.update()
            time += self.time_step

        self._gather_data()
