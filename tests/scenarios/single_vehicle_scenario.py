import numpy as np
from plotly.subplots import make_subplots

from traffic_flow import models
from traffic_flow.simulation_helpers.vehicle_generator import VehiclesGenerator


def run_scenario() -> list[dict]:
    highway = models.Road((0, 0), (2_000, 0), "A4")
    vehicles_generator = VehiclesGenerator()

    roadmap = {"A4": highway}
    route = ["A4"]

    vehicles_generator.add_vehicle(route, 0)
    vehicle_sepcifications = vehicles_generator.vehicles_specifications

    single_vehicle_simulation = models.TrafficFlow(vehicle_sepcifications, roadmap)

    single_vehicle_simulation.run()
    return single_vehicle_simulation.simulation_evolution


def process_simulation_evolution(
    simulation_evolution: list[dict],
) -> dict[str, list]:

    clean_data = simulation_evolution.pop()["roads_data"]["A4"]
    return clean_data


def plot_result(data: dict[str, list]):
    properties = ["position", "velocity", "acceleration"]
    fig = make_subplots(
        3, 1, shared_xaxes=True, subplot_titles=[_property.title() for _property in properties]
    )

    time = np.arange(len(data.get("position"))) / 60  # type: ignore

    for n, _property in enumerate(properties):
        fig.add_scatter(x=time, y=data.get(_property), row=n + 1, col=1, showlegend=False)

    fig.update_layout(template="plotly_white", xaxis_title="Time (s)", yaxis_title="Distance (m)")
    fig.update_layout(yaxis2_title="Velocity (m/s)")
    fig.update_layout(yaxis3_title="Acceleration (m/s²)")
    fig.show()


if __name__ == "__main__":
    simulation_evolution = run_scenario()
    clean_data = process_simulation_evolution(simulation_evolution)

    plot_result(clean_data)
