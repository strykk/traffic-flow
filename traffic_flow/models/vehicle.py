# Postpone evaluation of annotations so you can use own class in a method definitions.
from __future__ import annotations

from collections import defaultdict, deque

from traffic_flow.models.road import Road


class Vehicle:
    """Single agent in a simulation

    A vehicle is defined by a set of parameters required by the model
    (references will be placed in README).
    """

    def __init__(
        self,
        route: list[Road],
        vehicle_configs: dict | None = None,
        vehicle_starting_properties: dict | None = None,
        ride_data: dict | None = None,
    ) -> None:
        self.route = deque(route)
        self.ride_data = self._initialize_ride_data(ride_data)

        self._set_vehicle_configs(vehicle_configs)
        self._set_vehicle_starting_properties(vehicle_starting_properties)
        self.leading_vehicle = None
        self._start_ride()

        self.vehicle_length: int  # l, m
        self.desired_velocity: float  # v0, m/s
        self.maximum_acceleration: float  # a, m/s²
        self.desired_deceleration: float  # b, m/s²,
        self.mininimal_desired_distance: float  # s0, m
        self.acceleration_exponent: float  # delta
        self.driver_reaction_time: float  # T, s

        # Position in meters with respect to the road the vehicle is currently on.
        self.position: float

        self.velocity: float
        self.acceleration: float

    def _set_attributes(self, attributes: dict) -> None:
        for key, value in attributes.items():
            setattr(self, key, value)

    def _set_vehicle_configs(self, vehicle_configs: dict | None) -> None:
        default_vehicle_configs = {
            "vehicle_length": 5,  # l, m
            "desired_velocity": 33.333,  # v0, m/s
            "maximum_acceleration": 0.73,  # a, m/s²
            "desired_deceleration": 1.67,  # b, m/s²,
            "mininimal_desired_distance": 2,  # s0, m
            "acceleration_exponent": 4,  # delta
            "driver_reaction_time": 1.6,  # T, s
        }

        if vehicle_configs:
            default_vehicle_configs |= vehicle_configs

        self._set_attributes(default_vehicle_configs)

    def _set_vehicle_starting_properties(self, vehicle_starting_properties: dict | None) -> None:
        default_vehicle_starting_properties = {
            "position": 0.0,
            "velocity": 0,
            "acceleration": 0,
        }

        if vehicle_starting_properties:
            default_vehicle_starting_properties |= vehicle_starting_properties

        self._set_attributes(default_vehicle_starting_properties)

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

    def _initialize_ride_data(self, ride_data: dict | None) -> dict:
        if ride_data is None:
            ride_data = {}

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
