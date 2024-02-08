# Postpone evaluation of annotations so you can use own class in a method definitions.
from __future__ import annotations

from collections import defaultdict, deque

# from traffic_flow.models.road import Road


class Vehicle:
    """Single agent in a simulation

    A vehicle is defined by a set of parameters required by the model
    (references will be placed in README).
    """

    def __init__(
        self,
        route: list[str],
        # TODO: Refactor this mess.
        vehicle_configs: dict | None = None,
        vehicle_starting_properties: dict | None = None,
        ride_data: dict | None = None,
    ) -> None:
        if not route:
            raise ValueError("Each vehicle must have non-empty route!")
        self.route = deque(route)
        self.ride_data = self._initialize_ride_data(ride_data)

        self._set_vehicle_configs(vehicle_configs)
        self._set_vehicle_starting_properties(vehicle_starting_properties)

        self.leading_vehicle = None
        self.first_vehicle = False
        self.is_ride_finished = False

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

        self.new_position: float
        self.new_velocity: float

        self.max_velocity = self.desired_velocity
        self.slower_zone = False

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

        for key, value in default_vehicle_starting_properties.items():
            setattr(self, "_".join(["new", key]), value)

    def start_ride(self, roadmap: dict[str, "Road"]) -> None:  # type: ignore # noqa
        first_road = roadmap[self.route.popleft()]
        self.current_road = first_road
        if first_road.vehicles:
            self.leading_vehicle = first_road.vehicles[-1]
        else:
            self.first_vehicle = True  # Remember to check it in updates!

        first_road.add_vehicle(self)

    def _change_road(self, distance_passed: float) -> None:
        try:
            next_road_name = self.route.popleft()
            next_road = self.current_road.get_next_road(next_road_name)

            self.current_road = next_road
            if next_road.vehicles:
                self.leading_vehicle = next_road.vehicles[-1]
            else:
                self.first_vehicle = True  # Remember to check it in updates!
                self.leading_vehicle = None

            next_road.add_vehicle(self)
            self.new_position = distance_passed

        except IndexError:
            self.is_ride_finished = True

    def _initialize_ride_data(self, ride_data: dict | None) -> dict:
        if ride_data is None:
            ride_data = {}

        roads_data = {}
        for road_name in self.route:
            roads_data[road_name] = defaultdict(list)

        ride_data["roads_data"] = roads_data
        return ride_data

    def _update_free_road_acceleration_component(self):
        return self.maximum_acceleration * (
            1 - (self.velocity / self.max_velocity) ** self.acceleration_exponent
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

    def _update_acceleration(self) -> None:
        acceleration = self._update_free_road_acceleration_component()

        if self.leading_vehicle:
            acceleration += self._update_leading_vehicle_acceleration_component(
                self.leading_vehicle
            )

        self.acceleration = acceleration

    def _calculate_updated_velocity(self, time_step: float):
        return self.velocity + self.acceleration * time_step

    def _update_position(self, time_step: float):
        self.new_position += self.new_velocity * time_step + (self.acceleration * time_step**2) / 2

    def _update_position_negative_velocity(self, time_step: float):
        self.new_position -= self.new_velocity * time_step / 2

    def _update_ride_data(self):
        road_data = self.ride_data["roads_data"][self.current_road.road_name]

        road_data["position"].append(self.new_position)
        road_data["velocity"].append(self.new_velocity)
        road_data["acceleration"].append(self.acceleration)

    def _slow_down(self, max_velocity: float):
        self.max_velocity = max_velocity

    def _stop_vehicle(self):
        self.acceleration = -self.desired_deceleration * self.velocity / self.max_velocity

    def move(self, time_step: float) -> None:
        # Swap variables.
        self.velocity = self.new_velocity
        self.position = self.new_position

        distance_to_node = self.current_road.length - self.position

        # Check only if the vehicle is first vehicle - others adapt according to the equation.
        if self.first_vehicle:
            if (
                traffic_lights := self.current_road.traffic_lights
            ) and not self.current_road.green_light:
                if distance_to_node < traffic_lights.slowing_down_distance:
                    self._slow_down(traffic_lights.approaching_speed)
                    self.slower_zone = True

                if distance_to_node < traffic_lights.stopping_distance:
                    self._stop_vehicle()
                else:
                    self._update_acceleration()
            else:
                if self.slower_zone:
                    self.max_velocity = self.desired_velocity
                    self.slower_zone = False
                self._update_acceleration()
        else:
            if self.slower_zone:
                self.max_velocity = self.desired_velocity
                self.slower_zone = False
            self._update_acceleration()

        updated_velocity = self._calculate_updated_velocity(time_step)

        if updated_velocity < 0:
            self._update_position_negative_velocity(time_step)
            self.new_velocity = 0
        else:
            self.new_velocity = updated_velocity
            self._update_position(time_step)

        # New distance!
        distance_to_node = self.current_road.length - self.new_position
        # TODO: Optimize it later by making the road remember the first vehicle.
        if not self.first_vehicle and self.current_road.vehicles.index(self) == 0:
            self.first_vehicle = True
            self.leading_vehicle = None

        if distance_to_node < 0:
            self.current_road.remove_vehicle()
            self._change_road(-distance_to_node)

        self._update_ride_data()
