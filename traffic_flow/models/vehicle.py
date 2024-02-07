from __future__ import (
    annotations,  # Postpone evaluation of annotations so you can use own class in a method definition.
)


class Vehicle:
    """Single agent in a simulation

    A vehicle is defined by a set of parameters required by the model
    (references will be placed in README).
    """

    def __init__(self) -> None:
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
        self.position = 0

        self.velocity = 0
        self.acceleration = 0

    def _update_acceleration(self, leading_vehicle: Vehicle | None = None) -> None:
        acceleration = self._update_free_road_acceleration_component()

        if leading_vehicle:
            acceleration += self._update_leading_vehicle_acceleration_component(leading_vehicle)

        self.acceleration = acceleration

    def _update_free_road_acceleration_component(self):
        return self.maximum_acceleration * (1 - (self.velocity / self.desired_velocity) ** self.acceleration_exponent)

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

    def move(self, time_step: float, leading_vehicle: Vehicle) -> float:
        self._update_acceleration(leading_vehicle)

        updated_velocity = self._calculate_updated_velocity(time_step)
        if updated_velocity < 0:
            self._update_position_negative_velocity(time_step)
            self.velocity = 0
        else:
            self.velocity = updated_velocity
            self._update_position(time_step)

        return self.position
