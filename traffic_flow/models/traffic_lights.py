from itertools import cycle

from .road import Road


class TrafficLights:
    def __init__(
        self,
        roads: list[Road],
        cycle_times: list[float],
        cycle_green_lights: list[tuple[bool]],
        approaching_speed: float = 5,
        slowing_down_distance: int = 50,
        stopping_distance: int = 15,
    ) -> None:
        if len(cycle_green_lights) != len(cycle_times):
            raise ValueError("The length of cycle_green_lights and cycle_times must be equal!")
        self.roads = self._set_up_roads(roads)

        self.cycle_times = cycle(cycle_times)
        self.cycle_green_lights = self._set_up_cycle_green_lights(cycle_green_lights)

        self.approaching_speed = approaching_speed
        self.slowing_down_distance = slowing_down_distance
        self.stopping_distance = stopping_distance

        self._next_cycle()

    def _set_up_cycle_green_lights(
        self, cycle_green_lights: list[tuple[bool]]
    ) -> cycle[tuple[bool]]:

        for cycle_lights_set in cycle_green_lights:
            if len(cycle_lights_set) != len(self.roads):
                raise ValueError(
                    "Length of each element of cycle_green_lights must be equal to number of roads!"  # noqa
                )

        return cycle(cycle_green_lights)

    def _set_up_roads(self, roads: list[Road]) -> list[Road]:
        for road in roads:
            road.set_traffic_lights(self)

        return roads

    def _next_cycle(self) -> None:
        green_lights = next(self.cycle_green_lights)

        for n, road in enumerate(self.roads):
            road.set_green_light(green_lights[n])

        self.counter = next(self.cycle_times)

    def tic(self, time_step: float) -> None:
        self.counter -= time_step

        if self.counter <= 0:
            self._next_cycle()
