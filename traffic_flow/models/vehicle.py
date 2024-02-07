# Postpone evaluation of annotations so you can use own class in a method definitions.
from __future__ import annotations

from collections import defaultdict, deque

from traffic_flow.models.road import Road


class Vehicle:
    """Single agent in a simulation

    A vehicle is defined by a set of parameters required by the model
    (references will be placed in README).
    """

    def __init__(self, route: deque[Road], ride_data: dict = {}) -> None:
        self.route = route
        self.ride_data = self._initialize_ride_data(ride_data)

        self.leading_vehicle = None
        self._start_ride()

        # For now, the vehicle params are hardcoded. The values are
        # from the original paper. In the comment, the symbol and the unit.
        self.vehicle_length = 5  # l, m
        self.desired_velocity = 33.333  # v0, m/s
        self.maximum_acceleration = 0.73  # a, m/s²
        self.desired_deceleration = 1.67  # b, m/s²,
        self.mininimal_desired_distance = 2  # s0, m
        self.acceleration_exponent = 4  # delta
        self.driver_reaction_time = 1.6  # T, s

        # Position in meters with respect to the road the vehicle is currently on.
        self.position = 0.0

        self.velocity = 0
        self.acceleration = 0

    def _enter_road(self) -> None:
        current_road = self.route.popleft()
        if current_road.vehicles:
            self.leading_vehicle = current_road.vehicles[-1]
        current_road.add_vehicle(self)
        self.current_road = current_road

    def _start_ride(self) -> None:
        try:
            self._enter_road()
            self.is_ride_finished = False
        except IndexError:
            raise ValueError("Each Vehicle must have non-empty route!")

    def _initialize_ride_data(self, ride_data: dict) -> dict:
        roads_data = {}
        for road in self.route:
            roads_data[road.index] = defaultdict(list)

        ride_data["roads_data"] = roads_data
        return ride_data

    def _update_acceleration(self) -> None:
        acceleration = self._update_free_road_acceleration_component()

        if self.leading_vehicle:
            acceleration += self._update_leading_vehicle_acceleration_component(
                self.leading_vehicle
            )

        self.acceleration = acceleration

    def _update_free_road_acceleration_component(self):
        return self.maximum_acceleration * (
            1 - (self.velocity / self.desired_velocity) ** self.acceleration_exponent
        )

    def _update_leading_vehicle_acceleration_component(self, leading_vehicle: Vehicle):
        approaching_rate = self.velocity - leading_vehicle.velocity
        net_distance = leading_vehicle.position - self.position - self.vehicle_length

        desired_minimum_gap = (
            self.mininimal_desired_distance
            + self.driver_reaction_time * self.velocity
            + (self.velocity * approaching_rate)
            / (2 * (self.maximum_acceleration * self.desired_deceleration) ** (1 / 2))
        )

        deceleration_term = desired_minimum_gap / net_distance

        return -(deceleration_term**2)

    def _calculate_updated_velocity(self, time_step: float):
        return self.velocity + self.acceleration * time_step

    def _update_position(self, time_step: float):
        self.position += self.velocity * time_step + (self.acceleration * time_step**2) / 2

    def _update_position_negative_velocity(self, time_step: float):
        self.position -= self.velocity * time_step / 2

    def _change_road(self, past_road: float) -> None:
        try:
            self._enter_road()
        except IndexError:
            self.is_ride_finished = True

        self.position = past_road

    def _update_ride_data(self):
        road_data = self.ride_data["roads_data"][self.current_road.index]

        road_data["position"].append(self.position)
        road_data["velocity"].append(self.velocity)
        road_data["acceleration"].append(self.acceleration)

    def move(self, time_step: float) -> None:
        self._update_acceleration()

        updated_velocity = self._calculate_updated_velocity(time_step)
        if updated_velocity < 0:
            self._update_position_negative_velocity(time_step)
            self.velocity = 0
        else:
            self.velocity = updated_velocity
            self._update_position(time_step)

        if (past_road := (self.position - self.current_road.length)) > 0:  # type: ignore
            self._change_road(past_road)
        elif self.leading_vehicle and self.current_road.vehicles.index(self) == 0:
            self.leading_vehicle = None

        self._update_ride_data()
