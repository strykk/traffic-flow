from traffic_flow.models.road import Road


class TrafficFlow:
    """Single simulation of a traffic flow"""

    def __init__(self) -> None:
        self.time_step = 1 / 60  # seconds
        self.total_time = 120  # seconds

        self.roads = list[Road]()

    def add_road(self, road: Road) -> None:
        self.roads.append(road)

    def update(self):
        vehicles_on_roadmap_positions = list[list[float]]()

        for road in self.roads:
            vehicles_on_roadmap_positions.append(road.update(self.time_step))

        return vehicles_on_roadmap_positions

    def run(self):
        # Stores positions of all vehicles from all roads in the whole simulation.
        simulation_evolution = []
        time = self.time_step

        while time <= self.total_time:
            simulation_evolution.append(self.update())
            time += self.time_step

        return simulation_evolution
