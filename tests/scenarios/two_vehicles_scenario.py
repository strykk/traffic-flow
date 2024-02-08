from collections import deque

import numpy as np
from plotly.subplots import make_subplots

from traffic_flow import models


def run_scenario() -> list[dict]:
    highway = models.Road((0, 0), (2_000, 0), "A4")
    route = deque([highway])
    vehicle1 = models.Vehicle(route)
    vehicle2 = models.Vehicle(route)
    vehicle2.position = 400
    vehicle2.desired_velocity = 25

    two_vehicles_simulation = models.TrafficFlow()
    two_vehicles_simulation.total_time = 240
    two_vehicles_simulation.add_vehicle(vehicle1)
    two_vehicles_simulation.add_vehicle(vehicle2)

    two_vehicles_simulation.run()
    return two_vehicles_simulation.simulation_evolution


def plot_result(data):

    properties = ["position", "velocity", "acceleration"]
    fig = make_subplots(
        3, 2, shared_xaxes=True, row_titles=[_property.title() for _property in properties]
    )

    for k, car_data in enumerate(data):
        road_data = car_data["roads_data"]
        time = np.arange(len(road_data.get("position"))) / 60  # type: ignore

        for n, _property in enumerate(properties):
            fig.add_scatter(
                x=time, y=road_data.get(_property), row=n + 1, col=k + 1, showlegend=False
            )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Time (s)",
        yaxis4_range=(0, 33.333),
        yaxis5_range=(0, 0.8),
        yaxis6_range=(0, 0.8),
    )
    fig.show()


if __name__ == "__main__":
    simulation_evolution = run_scenario()

    plot_result(simulation_evolution)
