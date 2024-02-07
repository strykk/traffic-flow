import numpy as np
from plotly import graph_objects as go

from traffic_flow import models


def run_scenario() -> list[list[list[float]]]:
    vehicle = models.Vehicle()
    highway = models.Road((0, 0), (2_000, 0))

    single_vehicle_simulation = models.TrafficFlow()

    highway.add_vehicle(vehicle)
    single_vehicle_simulation.add_road(highway)

    return single_vehicle_simulation.run()


def process_simulation_evolution(
    simulation_evolution: list[list[list[float]]],
) -> list[float]:

    clean_data = [
        position for roadmap in simulation_evolution for road in roadmap for position in road
    ]

    return clean_data


def plot_result(data: list[float]):
    fig = go.Figure()

    time = np.arange(len(data)) / 60  # time_step value

    fig.add_scatter(x=time, y=data)

    fig.update_layout(template="plotly_white", xaxis_title="Time (s)", yaxis_title="Distance (m)")
    fig.show()


if __name__ == "__main__":
    simulation_evolution = run_scenario()
    clean_data = process_simulation_evolution(simulation_evolution)

    plot_result(clean_data)
